from spinn_machine import exceptions
from spinn_machine.machine import Machine
from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM
from spinn_machine.link import Link

import logging
from spinn_machine.spinnaker_triad_geometry import SpiNNakerTriadGeometry

logger = logging.getLogger(__name__)


class VirtualMachine(Machine):
    """ A Virtual SpiNNaker machine
    """

    __slots__ = (
        "_n_cpus_per_chip",

        "_with_wrap_arounds",

        "_sdram_per_chip",

        "_with_monitors",

        "_down_chips",

        "_down_cores",

        "_down_links"
    )

    _4_chip_down_links = {
        (0, 0, 3), (0, 0, 4), (0, 1, 3), (0, 1, 4),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
    }

    def __init__(
            self, width=None, height=None, with_wrap_arounds=False,
            version=None, n_cpus_per_chip=18, with_monitors=True,
            sdram_per_chip=None, down_chips=None, down_cores=None,
            down_links=None):
        """

        :param width: the width of the virtual machine in chips
        :type width: int
        :param height: the height of the virtual machine in chips
        :type height: int
        :param with_wrap_arounds: bool defining if wrap around links exist
        :type with_wrap_arounds: bool
        :param version: the version id of a board; if None, a machine is\
                    created with the correct dimensions, otherwise the machine\
                    will be a single board of the given version
        :type version: int
        :param n_cpus_per_chip: The number of CPUs to put on each chip
        :type n_cpus_per_chip: int
        :param with_monitors: True if CPU 0 should be marked as a monitor
        :type with_monitors: bool
        :param sdram_per_chip: The amount of SDRAM to give to each chip
        :type sdram_per_chip: int or None
        """
        Machine.__init__(self, (), 0, 0)

        # Verify the machine
        if ((width is not None and width < 0) or
                (height is not None and height < 0)):
            raise exceptions.SpinnMachineInvalidParameterException(
                "width or height", "{} or {}".format(width, height),
                "Negative dimensions are not supported")

        if version is None and (width is None or height is None):
            raise exceptions.SpinnMachineInvalidParameterException(
                "version, width, height",
                "{}, {}, {}".format(version, width, height),
                "Either version must be specified, "
                "or width and height must both be specified")

        if version is not None and (version < 2 or version > 5):
            raise exceptions.SpinnMachineInvalidParameterException(
                "version", str(version),
                "Version must be between 2 and 5 inclusive or None")

        if ((version == 5 or version == 4) and
                with_wrap_arounds is not None and with_wrap_arounds):
            raise exceptions.SpinnMachineInvalidParameterException(
                "version and with_wrap_arounds",
                "{} and True".format(version),
                "A version {} board does not have wrap arounds; set "
                "version to None or with_wrap_arounds to None".format(version))

        if (version == 2 or version == 3) and with_wrap_arounds is not None:
            raise exceptions.SpinnMachineInvalidParameterException(
                "version and with_wrap_arounds",
                "{} and {}".format(version, with_wrap_arounds),
                "A version {} board has complex wrap arounds; set "
                "version to None or with_wrap_arounds to None".format(version))

        if ((version == 5 or version == 4) and (
                (width is not None and width != 8) or
                (height is not None and height != 8))):
            raise exceptions.SpinnMachineInvalidParameterException(
                "version, width, height",
                "{}, {}, {}".format(version, width, height),
                "A version {} board has a width and height of 8; set "
                "version to None or width and height to None".format(version))

        if ((version == 2 or version == 3) and (
                (width is not None and width != 2) or
                (height is not None and height != 2))):
            raise exceptions.SpinnMachineInvalidParameterException(
                "version, width, height",
                "{}, {}, {}".format(version, width, height),
                "A version {} board has a width and height of 2; set "
                "version to None or width and height to None".format(version))

        if (version is None and with_wrap_arounds and
                not ((width == 8 and height == 8) or
                     (width == 2 and height == 2) or
                     (width % 12 == 0 and height % 12 == 0))):
            raise exceptions.SpinnMachineInvalidParameterException(
                "version, width, height, with_wrap_arounds",
                "{}, {}, {}, {}".format(
                    version, width, height, with_wrap_arounds),
                "A generic machine with wrap arounds must be either have a"
                " width and height which are both either 2 or 8 or a width"
                " and height that are divisible by 12".format(version))

        if (version is None and not with_wrap_arounds and
                not ((width == 8 and height == 8) or
                     (width == 2 and height == 2) or
                     ((width - 4) % 12 == 0 and (height - 4) % 12 == 0))):
            raise exceptions.SpinnMachineInvalidParameterException(
                "version, width, height, with_wrap_arounds",
                "{}, {}, {}, {}".format(
                    version, width, height, with_wrap_arounds),
                "A generic machine without wrap arounds must be either have a"
                " width and height which are both either 2 or 8 or a width - 4"
                " and height - 4 that are divisible by 12".format(version))

        # Get parameters for specific versions of boards
        if version == 5 or version == 4:
            if width is None:
                width = 8
            if height is None:
                height = 8
            with_wrap_arounds = False
        if version == 2 or version == 3:
            if width is None:
                width = 2
            if height is None:
                height = 2
            with_wrap_arounds = True
        logger.debug("width = {} and height  = {}".format(width, height))

        # Set up the maximum chip x and y
        self._max_chip_x = width - 1
        self._max_chip_y = height - 1

        # Store the details
        self._n_cpus_per_chip = n_cpus_per_chip
        self._with_wrap_arounds = with_wrap_arounds
        self._sdram_per_chip = sdram_per_chip
        self._with_monitors = with_monitors

        # Store and compute the down items
        self._down_cores = down_cores if down_cores is not None else set()
        self._down_chips = down_chips if down_chips is not None else set()
        self._down_links = down_links if down_links is not None else set()
        if version == 4 or version == 5:
            self._down_chips.update(Machine.BOARD_48_CHIP_GAPS)
        elif version == 2 or version == 3:
            self._down_links.update(VirtualMachine._4_chip_down_links)

        # Calculate the Ethernet connections in the machine, assuming 48-node
        # boards
        n_ethernets = 0
        ethernet_chips = set()
        eth_width = width
        eth_height = height
        if (version is None and not with_wrap_arounds and
                width > 8 and width % 12 != 0):
            eth_width = width - 4
        if (version is None and not with_wrap_arounds and
                height > 8 and height % 12 != 0):
            eth_height = height - 4
        for start_x, start_y in ((0, 0), (8, 4), (4, 8)):
            for y in range(start_y, eth_height, 12):
                for x in range(start_x, eth_width, 12):
                    if (x, y) not in self._down_chips:
                        ip_address = "127.0.0.{}".format(n_ethernets + 1)
                        n_ethernets += 1
                        ethernet_chips.add((x, y))
                        self.add_chip(self._create_chip(x, y, ip_address))

        # If there are no wrap arounds, and the version is not specified,
        # remove chips not in the network
        if version is None and not self._with_wrap_arounds:

            # Find all the chips that are on the board
            all_chips = {
                (x + eth_x, y + eth_y) for x in range(8) for y in range(8)
                for eth_x, eth_y in ethernet_chips
                if (x, y) not in Machine.BOARD_48_CHIP_GAPS
            }

            self._down_chips = {
                (x, y) for x in range(width) for y in range(height)
                if (x, y) not in all_chips
            }

        self.add_spinnaker_links(version)
        self.add_fpga_links(version)

    @property
    def chips(self):
        for x in range(0, self._max_chip_x + 1):
            for y in range(0, self._max_chip_y + 1):
                if (x, y) in self._chips:
                    yield self._chips[(x, y)]
                elif (x, y) not in self._down_chips:
                    self.add_chip(self._create_chip(x, y))
                    yield self._chips[(x, y)]

    @property
    def chip_coordinates(self):
        for x in range(0, self._max_chip_x + 1):
            for y in range(0, self._max_chip_y + 1):
                if (x, y) not in self._down_chips:
                    yield (x, y)

    def __iter__(self):
        for x in range(0, self._max_chip_x + 1):
            for y in range(0, self._max_chip_y + 1):
                if (x, y) in self._chips:
                    yield (x, y), self._chips[(x, y)]
                elif (x, y) not in self._down_chips:
                    self.add_chip(self._create_chip(x, y))
                    yield (x, y), self._chips[(x, y)]

    def get_chip_at(self, x, y):
        if ((x, y) not in self._chips and (x, y) not in self._down_chips and
                x <= self._max_chip_x and y <= self._max_chip_y):
            self.add_chip(self._create_chip(x, y))
        return Machine.get_chip_at(self, x, y)

    def is_chip_at(self, x, y):
        return ((x, y) not in self._down_chips and
                x <= self._max_chip_x and y <= self._max_chip_y)

    def is_link_at(self, x, y, link):
        return (
            self.is_chip_at(x, y) and
            (x, y, link) not in self._down_links and
            link >= 0 and link <= 5)

    @property
    def n_chips(self):
        return (self._max_chip_x * self._max_chip_y) - len(self._down_chips)

    def __str__(self):
        return "[VirtualMachine: max_x={}, max_y={}]".format(
            self._max_chip_x, self._max_chip_y)

    def get_cores_and_link_count(self):
        n_cores = (
            (self.n_chips * self._n_cpus_per_chip) - len(self._down_cores)
        )
        n_links = self.n_chips * 6 - len(self._down_links)
        return n_cores, n_links

    def _create_chip(self, x, y, ip_address=None):
        processors = list()
        for processor_id in range(0, self._n_cpus_per_chip):
            if (x, y, processor_id) not in self._down_cores:
                processor = Processor(processor_id)
                if processor_id == 0 and self._with_monitors:
                    processor.is_monitor = True
                processors.append(processor)
        chip_links = self._calculate_links(x, y)
        chip_router = Router(chip_links, False)
        if self._sdram_per_chip is None:
            sdram = SDRAM()
        else:
            sdram = SDRAM(self._sdram_per_chip)

        geometry = SpiNNakerTriadGeometry.get_spinn5_geometry()
        eth_x, eth_y = geometry.get_ethernet_chip_coordinates(
            x, y, self._max_chip_x + 1, self._max_chip_y + 1,
            self._boot_x, self._boot_y)

        return Chip(
            x, y, processors, chip_router, sdram, eth_x, eth_y, ip_address)

    def _calculate_links(self, x, y):
        """ Calculate the links needed for a machine structure
        """
        links = list()
        self._add_link(links, 0, x, y, x + 1, y)
        self._add_link(links, 1, x, y, x + 1, y + 1)
        self._add_link(links, 2, x, y, x, y + 1)
        self._add_link(links, 3, x, y, x - 1, y)
        self._add_link(links, 4, x, y, x - 1, y - 1)
        self._add_link(links, 5, x, y, x, y - 1)
        return links

    def _add_link(self, links, link_from, start_x, start_y, end_x, end_y):

        # Work out if the link is wrap around
        wrap_around = False
        if end_x > self._max_chip_x:
            wrap_around = True
            end_x = 0
        if end_y > self._max_chip_y:
            wrap_around = True
            end_y = 0
        if end_x < 0:
            wrap_around = True
            end_x = self._max_chip_x
        if end_y < 0:
            wrap_around = True
            end_y = self._max_chip_y

        # If wrap-arounds is enabled add all links, otherwise only add links
        # where the end isn't a wrap-around
        if self._with_wrap_arounds or not wrap_around:

            # Only add links where the destination chip is not down or the
            # link is not marked as down
            if ((end_x, end_y) not in self._down_chips and
                    (start_x, start_y, link_from) not in self._down_links):

                # Work out the "opposite" link
                link_to = (link_from + 3) % 6
                links.append(Link(
                    source_x=start_x, source_y=start_y, destination_x=end_x,
                    destination_y=end_y, source_link_id=link_from,
                    multicast_default_from=link_to,
                    multicast_default_to=link_to))

    @property
    def maximum_user_cores_on_chip(self):
        return self._n_cpus_per_chip
