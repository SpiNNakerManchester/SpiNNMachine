# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    from collections.abc import defaultdict
except ImportError:
    from collections import defaultdict
import logging
from .chip import Chip
from .exceptions import SpinnMachineInvalidParameterException
from .full_wrap_machine import FullWrapMachine
from .machine import Machine
from .no_wrap_machine import NoWrapMachine
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
            "A version {} board has complex wrap-arounds; set version "
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
    return width, height


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
    return width, height


def _verify_width_height(width, height):
    if (width == height == 2):
        return
    if (width == height == 8):
        return
    if (width % 12 != 0) and (width - 4) % 12 != 0:
        raise SpinnMachineInvalidParameterException(
            "width", width,
            "A virtual machine must have a width that is divisible by 12 or "
            "width - 4 that is divisible by 12")
    if (height % 12 != 0) and (height - 4) % 12 != 0:
        raise SpinnMachineInvalidParameterException(
            "height", height,
            "A virtual machine must have a height that is divisible by 12 or "
            "height - 4 that is divisible by 12")


def virtual_machine(
        width=None, height=None, with_wrap_arounds=None, version=None,
        n_cpus_per_chip=Machine.MAX_CORES_PER_CHIP, with_monitors=True,
        sdram_per_chip=SDRAM.DEFAULT_SDRAM_BYTES, down_chips=None,
        down_cores=None, down_links=None,
        router_entries_per_chip=Router.ROUTER_DEFAULT_AVAILABLE_ENTRIES,
        validate=True):
    """
    :param width: the width of the virtual machine in chips
    :type width: int
    :param height: the height of the virtual machine in chips
    :type height: int
    :param with_wrap_arounds: bool defining if wrap around links exist
        If set a board with the requested wrap around is created
        regardless of the board size.

        In None the wrap around will be auto detected by machine_factory

        Note: Use either with_wrap_arounds or version but not both
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
    :param validate: if True will call the machine validate function
    :type validate: bool
    """

    factory = _VirtualMachine(
        width, height, with_wrap_arounds, version, n_cpus_per_chip,
        with_monitors, sdram_per_chip, down_chips, down_cores, down_links,
        router_entries_per_chip, validate)
    return factory.machine


def virtual_submachine(machine, ethernet_chip):
    """ Creates a virtual machine based off a real machine but just with the \
        system resources of a single board (identified by its ethernet chip).

    :param machine: The machine to create the virtual machine from. \
        May be a virtual machine. May be a single-board machine.
    :param ethernet_chip: The chip that can talk to the board's ethernet.
    """
    # build fake setup for the routing
    eth_x = ethernet_chip.x
    eth_y = ethernet_chip.y

    # Work out where all the down chips and links on the board are
    down_links = set()
    up_chips = set()
    for chip in machine.get_chips_by_ethernet(eth_x, eth_y):
        fake_x, fake_y = fake_xy = machine.get_local_xy(chip)
        up_chips.add(fake_xy)
        down_links.update({
            (fake_x, fake_y, link)
            for link in range(Router.MAX_LINKS_PER_ROUTER)
            if not chip.router.is_link(link)})
    down_chips = {
        xy for xy in machine.local_xys if xy not in up_chips}

    # Create a fake machine consisting of only the one board that
    # the routes should go over
    return virtual_machine(
        min(machine.width, Machine.SIZE_X_OF_ONE_BOARD),
        min(machine.height, Machine.SIZE_Y_OF_ONE_BOARD),
        False, down_chips=down_chips, down_links=down_links)


class _VirtualMachine(object):
    """ A Virtual SpiNNaker machine factory
    """

    __slots__ = (
        "_down_cores",
        "_down_links",
        "_n_cpus_per_chip",
        "_n_router_entries_per_router",
        "_machine",
        "_sdram_per_chip",
        "_weird_processor",
        "_with_monitors")

    _4_chip_down_links = {
        (0, 0, 3), (0, 0, 4), (0, 1, 3), (0, 1, 4),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
    }

    ORIGIN = "Virtual"

    # pylint: disable=too-many-arguments
    def __init__(
            self, width=None, height=None, with_wrap_arounds=False,
            version=None, n_cpus_per_chip=Machine.MAX_CORES_PER_CHIP,
            with_monitors=True, sdram_per_chip=SDRAM.DEFAULT_SDRAM_BYTES,
            down_chips=None, down_cores=None, down_links=None,
            router_entries_per_chip=Router.ROUTER_DEFAULT_AVAILABLE_ENTRIES,
            validate=True):

        self._n_router_entries_per_router = router_entries_per_chip

        if down_chips is None:
            down_chips = []

        # Verify the machine
        # Check for not enough info or out of range
        _verify_basic_sanity(version, width, height)

        # Version 2/3
        if version in Machine.BOARD_VERSION_FOR_4_CHIPS:
            width, height = _verify_4_chip_board(
                version, width, height, with_wrap_arounds)
            self._machine = machine_from_size(
                width, height, origin=self.ORIGIN)
        # Version 4/5
        elif version in Machine.BOARD_VERSION_FOR_48_CHIPS:
            width, height = _verify_48_chip_board(
                version, width, height, with_wrap_arounds)
            self._machine = machine_from_size(
                width, height, origin=self.ORIGIN)
        # Autodetect
        elif version is None:
            _verify_width_height(width, height)
            if with_wrap_arounds is None:
                self._machine = machine_from_size(
                    width, height, origin=self.ORIGIN)
            elif with_wrap_arounds:
                self._machine = FullWrapMachine(
                    width, height, origin=self.ORIGIN)
            else:
                self._machine = NoWrapMachine(
                    width, height, origin=self.ORIGIN)
        else:
            raise SpinnMachineInvalidParameterException(
                "version",
                version,
                "The only supported version numbers are 2, 3, 4, 5")

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
            self._down_links.update(_VirtualMachine._4_chip_down_links)
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
        for (eth_x, eth_y) in ethernet_chips:
            for x_y in self._machine.get_xys_by_ethernet(eth_x, eth_y):
                if x_y not in down_chips:
                    configured_chips[x_y] = (eth_x, eth_y)

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

        self._machine.add_spinnaker_links()
        self._machine.add_fpga_links()
        if validate:
            self._machine.validate()

    @property
    def machine(self):
        return self._machine

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
        for link_id in range(6):
            if (x, y, link_id) not in self._down_links:
                link_x_y = self._machine.xy_over_link(x, y, link_id)
                if link_x_y in configured_chips:
                    links.append(
                        Link(source_x=x, source_y=y,
                             destination_x=link_x_y[0],
                             destination_y=link_x_y[1],
                             source_link_id=link_id))
        return links
