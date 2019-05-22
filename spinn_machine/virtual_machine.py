from collections import defaultdict
import logging

from .chip import Chip
from .exceptions import SpinnMachineInvalidParameterException
from .machine import Machine
from .processor import Processor
from .router import Router
from .sdram import SDRAM
from .link import Link
from .spinnaker_triad_geometry import SpiNNakerTriadGeometry
from .machine_factory import machine_from_size

logger = logging.getLogger(__name__)


def _verify_basic_sanity(version, width, height):
    if ((width is not None and width < 0) or
            (height is not None and height < 0)):
        raise SpinnMachineInvalidParameterException(
            "width or height", "{} or {}".format(width, height),
            "Negative dimensions are not supported")
    if version is None and (width is None or height is None):
        raise SpinnMachineInvalidParameterException(
            "version, width, height",
            "{}, {}, {}".format(version, width, height),
            "Either version must be specified, "
            "or width and height must both be specified")
    if version is not None and (version < 2 or version > 5):
        raise SpinnMachineInvalidParameterException(
            "version", str(version),
            "Version must be between 2 and 5 inclusive or None")


def _verify_4_chip_board(version, width, height, wrap_arounds):
    if wrap_arounds is not None:
        raise SpinnMachineInvalidParameterException(
            "version and with_wrap_arounds",
            "{} and {}".format(version, wrap_arounds),
            "A version {} board has complex wrap arounds; set version "
            "to None or with_wrap_arounds to None".format(version))
    if ((width is not None and width != 2) or
            (height is not None and height != 2)):
        raise SpinnMachineInvalidParameterException(
            "version, width, height",
            "{}, {}, {}".format(version, width, height),
            "A version {} board has a width and height of 2; set version "
            "to None or width and height to None".format(version))
    if width is None:
        width = 2
    if height is None:
        height = 2
    return width, height, True


def _verify_48_chip_board(version, width, height, wrap_arounds):
    if wrap_arounds is not None and wrap_arounds:
        raise SpinnMachineInvalidParameterException(
            "version and with_wrap_arounds",
            "{} and True".format(version),
            "A version {} board does not have wrap-arounds; set version "
            "to None or with_wrap_arounds to None".format(version))
    if ((width is not None and width != 8) or
            (height is not None and height != 8)):
        raise SpinnMachineInvalidParameterException(
            "version, width, height",
            "{}, {}, {}".format(version, width, height),
            "A version {} board has a width and height of 8; set version "
            "to None or width and height to None".format(version))
    if width is None:
        width = 8
    if height is None:
        height = 8
    return width, height, False


def _verify_autodetect(version, width, height, wrap_arounds):
    if wrap_arounds and not (
            (width == 2 and height == 2) or
            (width % 12 == 0 and height % 12 == 0)):
        raise SpinnMachineInvalidParameterException(
            "version, width, height, with_wrap_arounds",
            "{}, {}, {}, {}".format(
                version, width, height, wrap_arounds),
            "A generic machine with wrap-arounds must be either have a "
            "width and height which are both 2 or a width and height "
            "that are divisible by 12")
    if not wrap_arounds and not (
            (width == 8 and height == 8) or
            (width == 2 and height == 2) or
            ((width - 4) % 12 == 0 and (height - 4) % 12 == 0)):
        raise SpinnMachineInvalidParameterException(
            "version, width, height, with_wrap_arounds",
            "{}, {}, {}, {}".format(
                version, width, height, wrap_arounds),
            "A generic machine without wrap-arounds must be either have a"
            " width and height which are both either 2 or 8 or a width - 4"
            " and height - 4 that are divisible by 12")


class VirtualMachine(object):
    """ A Virtual SpiNNaker machine
    """

    __slots__ = (
        "_down_cores",
        "_down_links",
        "_height",
        "_n_cpus_per_chip",
        "_n_router_entries_per_router",
        "_machine",
        "_sdram_per_chip",
        "_weird_processor",
        "_width",
        "_with_monitors",
        "_with_wrap_arounds"
        )

    _4_chip_down_links = {
        (0, 0, 3), (0, 0, 4), (0, 1, 3), (0, 1, 4),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
    }

    # pylint: disable=too-maa  ny-arguments
    def __init__(
            self, width=None, height=None, with_wrap_arounds=False,
            version=None, n_cpus_per_chip=Machine.MAX_CORES_PER_CHIP,
            with_monitors=True, sdram_per_chip=SDRAM.DEFAULT_SDRAM_BYTES,
            down_chips=None, down_cores=None, down_links=None,
            router_entries_per_chip=Router.ROUTER_DEFAULT_AVAILABLE_ENTRIES):
        """
        :param width: the width of the virtual machine in chips
        :type width: int
        :param height: the height of the virtual machine in chips
        :type height: int
        :param with_wrap_arounds: bool defining if wrap around links exist
        :type with_wrap_arounds: bool
        :param version: the version ID of a board; if None, a machine is\
            created with the correct dimensions, otherwise the machine will be\
            a single board of the given version.
        :type version: int
        :param n_cpus_per_chip: The number of CPUs to put on each chip
        :type n_cpus_per_chip: int
        :param with_monitors: True if CPU 0 should be marked as a monitor
        :type with_monitors: bool
        :param sdram_per_chip: The amount of SDRAM to give to each chip
        :type sdram_per_chip: int or None
        :param router_entries_per_chip: the number of entries to each router
        :type router_entries_per_chip: int
        """

        self._n_router_entries_per_router = router_entries_per_chip

        if down_chips is None:
            down_chips = []

        # Verify the machine
        # Check for not enough info or out of range
        _verify_basic_sanity(version, width, height)

        # Version 2/3
        if version in Machine.BOARD_VERSION_FOR_4_CHIPS:
            width, height, with_wrap_arounds = _verify_4_chip_board(
                version, width, height, with_wrap_arounds)
        # Version 4/5
        elif version in Machine.BOARD_VERSION_FOR_48_CHIPS:
            width, height, with_wrap_arounds = _verify_48_chip_board(
                version, width, height, with_wrap_arounds)
        # Autodetect
        elif version is None and with_wrap_arounds is None:
            if width == 2 and height == 2:

                # assume the special version 2 or 3 wrap arounds
                version = 2
                self._with_wrap_arounds = True
            elif width == 8 and height == 8:
                self._with_wrap_arounds = False
            elif width % 12 == 0 and height % 12 == 0:
                self._with_wrap_arounds = True
            elif (width - 4) % 12 == 0 and (height - 4) % 12 == 0:
                self._with_wrap_arounds = False
            else:
                raise SpinnMachineInvalidParameterException(
                    "version, width, height, with_wrap_arounds",
                    "{}, {}, {}, {}".format(
                        version, width, height, with_wrap_arounds),
                    "A generic machine with wrap-arounds None must either "
                    "have a width and height which are both either 2 or 8 or "
                    "a width and height that are divisible by 12 or a width "
                    "- 4 and height - 4 that are divisible by 12")

        if version is None and with_wrap_arounds is not None:
            _verify_autodetect(version, width, height, with_wrap_arounds)

        if with_wrap_arounds is None:
            logger.debug("width = %d, height = %d and auto wrap-arounds",
                         width, height)
        else:
            self._with_wrap_arounds = with_wrap_arounds
            logger.debug("width = %d, height = %d and wrap-arounds %s",
                         width, height, self._with_wrap_arounds)

        self._machine = machine_from_size(width, height)
        # Set the maximum board that will be filled in lazy unless set as down
        self._width = width
        self._height = height

        # Store the details
        self._sdram_per_chip = sdram_per_chip
        if with_monitors:
            self._with_monitors = 1
            self._weird_processor = False
        else:
            self._with_monitors = 0
            self._weird_processor = True
        self._n_cpus_per_chip = n_cpus_per_chip
        if n_cpus_per_chip != Machine.MAX_CORES_PER_CHIP:
            self._weird_processor = True

        # Store the down items
        self._down_cores = defaultdict(set)
        if down_cores is not None:
            for (x, y, p) in down_cores:
                self._down_cores[(x, y)].add(p)
        self._down_links = down_links if down_links is not None else set()
        if version in Machine.BOARD_VERSION_FOR_4_CHIPS:
            self._down_links.update(VirtualMachine._4_chip_down_links)
        if down_chips is None:
            down_chips = []

        # Calculate the Ethernet connections in the machine, assuming 48-node
        # boards
        geometry = SpiNNakerTriadGeometry.get_spinn5_geometry()
        ethernet_chips = geometry.get_potential_ethernet_chips(width, height)

        # Compute list of chips that are possible based on configuration
        # If there are no wrap arounds, and the the size is not 2 * 2,
        # the possible chips depend on the 48 chip board's gaps
        configured_chips = dict()
        if height > 2:
            for (eth_x, eth_y) in ethernet_chips:
                for x_y in self._machine.x_y_by_ethernet(eth_x, eth_y):
                    if x_y not in down_chips:
                        configured_chips[x_y] = (eth_x, eth_y)
        else:
            for x in range(2):
                for y in range(2):
                    if (x, y) not in down_chips:
                        configured_chips[(x, y)] = (0, 0)

        # TODO This needs to change as it previous checked against empty
        # for chip in self._unreachable_outgoing_chips:
        #    configured_chips.remove(chip)
        # for chip in self._unreachable_incoming_chips:
        #    configured_chips.remove(chip)

        for (x, y) in configured_chips:
            if configured_chips[(x, y)] == (x, y):
                new_chip = self._create_chip(
                    x, y, configured_chips, "127.0.{}.{}".format(x, y))
            else:
                new_chip = self._create_chip(x, y, configured_chips)
            self._machine.add_chip(new_chip)

        self._machine.add_spinnaker_links(version)
        self._machine.add_fpga_links(version)

    @property
    def machine(self):
        return self._machine


    ALLOWED_LINK_DELTAS = {
        0: (+1, 0),
        1: (+1, +1),
        2: (0, +1),
        3: (-1, 0),
        4: (-1, -1),
        5: (0, -1)}

    def normalize(self, x, y):
        if self._with_wrap_arounds:
            return ((x + self._width) % self._width,
                    (y + self._height) % self._height)
        return (x, y)

    def _create_processors_specific(self, x, y):
        processors = list()
        down = self._down_cores[(x, y)]
        for processor_id in range(0, self._with_monitors):
            if (x, y, processor_id) not in down:
                processor = Processor.factory(processor_id, is_monitor=True)
                processors.append(processor)
        for processor_id in range(self._with_monitors, self._n_cpus_per_chip):
            if (x, y, processor_id) not in down:
                processor = Processor.factory(processor_id, is_monitor=False)
                processors.append(processor)
        return processors

    def _create_chip(self, x, y, configured_chips, ip_address=None):
        if self._weird_processor or (x, y) in self._down_cores:
            processors = self._create_processors_specific(x, y)
        else:
            processors = None
        chip_links = self._calculate_links(x, y, configured_chips)
        chip_router = Router(
            chip_links,
            n_available_multicast_entries=self._n_router_entries_per_router)
        if self._sdram_per_chip is None:
            sdram = SDRAM()
        else:
            sdram = SDRAM(self._sdram_per_chip)

        (eth_x, eth_y) = configured_chips[(x, y)]

        return Chip(
            x, y, processors, chip_router, sdram, eth_x, eth_y, ip_address)

    def _calculate_links(self, x, y, configured_chips):
        """ Calculate the links needed for a machine structure
        """
        links = list()
        self._add_link(links, 0, x, y, x + 1, y, configured_chips)
        self._add_link(links, 1, x, y, x + 1, y + 1, configured_chips)
        self._add_link(links, 2, x, y, x, y + 1, configured_chips)
        self._add_link(links, 3, x, y, x - 1, y, configured_chips)
        self._add_link(links, 4, x, y, x - 1, y - 1, configured_chips)
        self._add_link(links, 5, x, y, x, y - 1, configured_chips)
        return links

    def _add_link(self, links, link_from, source_x, source_y,
                  destination_x, destination_y, configured_chips):
        if (source_x, source_y, link_from) in self._down_links:
            return  # Down chips say do not add

        destination_x, destination_y = self.normalize(
            destination_x, destination_y)
        if (destination_x, destination_y) not in configured_chips:
            return  # No destination to connect to

        link_to = (link_from + 3) % 6
        links.append(
            Link(source_x=source_x, source_y=source_y,
                 destination_x=destination_x, destination_y=destination_y,
                 source_link_id=link_from,
                 multicast_default_from=link_to,
                 multicast_default_to=link_to))
