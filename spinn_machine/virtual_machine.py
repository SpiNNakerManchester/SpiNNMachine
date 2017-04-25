from spinn_machine import exceptions
from spinn_machine.machine import Machine
from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM
from spinn_machine.link import Link

from spinn_utilities.ordered_set import OrderedSet

import logging
from spinn_machine.spinnaker_triad_geometry import SpiNNakerTriadGeometry

logger = logging.getLogger(__name__)


class VirtualMachine(Machine):
    """ A Virtual SpiNNaker machine
    """

    __slots__ = (
        "_configured_chips",
        "_default_processors",
        "_down_cores",
        "_down_links",
        "_extra_chips",
        "_n_cpus_per_chip",
        "_original_width",
        "_original_height",
        "_sdram_per_chip",
        "_with_monitors",
        "_with_wrap_arounds")

    _4_chip_down_links = {
        (0, 0, 3), (0, 0, 4), (0, 1, 3), (0, 1, 4),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
    }

    def __init__(
            self, width=None, height=None, with_wrap_arounds=False,
            version=None, n_cpus_per_chip=18, with_monitors=True,
            sdram_per_chip=None, down_chips=[], down_cores=None,
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
        # Check for not enough info or out of range
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

        # Version 2/3
        if (version == 2 or version == 3):
            if with_wrap_arounds is not None:
                raise exceptions.SpinnMachineInvalidParameterException(
                    "version and with_wrap_arounds",
                    "{} and {}".format(version, with_wrap_arounds),
                    "A version {} board has complex wrap arounds; set "
                    "version to None or with_wrap_arounds to None"
                    .format(version))
            if ((width is not None and width != 2) or
                    (height is not None and height != 2)):
                raise exceptions.SpinnMachineInvalidParameterException(
                    "version, width, height",
                    "{}, {}, {}".format(version, width, height),
                    "A version {} board has a width and height of 2; set "
                    "version to None or width and height to None"
                    .format(version))
            if width is None:
                width = 2
            if height is None:
                height = 2
            with_wrap_arounds = True

        # Version 4/5
        if (version == 5 or version == 4):
            if with_wrap_arounds is not None and with_wrap_arounds:
                raise exceptions.SpinnMachineInvalidParameterException(
                    "version and with_wrap_arounds",
                    "{} and True".format(version),
                    "A version {} board does not have wrap arounds; set "
                    "version to None or with_wrap_arounds to None"
                    .format(version))
            if ((width is not None and width != 8) or
                    (height is not None and height != 8)):
                raise exceptions.SpinnMachineInvalidParameterException(
                    "version, width, height",
                    "{}, {}, {}".format(version, width, height),
                    "A version {} board has a width and height of 8; set "
                    "version to None or width and height to None"
                    .format(version))
            if width is None:
                width = 8
            if height is None:
                height = 8
            with_wrap_arounds = False

        if (version is None and with_wrap_arounds is None):
            if (width == 2 and height == 2):

                # assume the special version 2 or 3 wrap arounds
                version = 2
                self._with_wrap_arounds = True
            elif (width == 8 and height == 8):
                self._with_wrap_arounds = False
            elif (width % 12 == 0 and height % 12 == 0):
                self._with_wrap_arounds = True
            elif ((width - 4) % 12 == 0 and (height - 4) % 12 == 0):
                self._with_wrap_arounds = False
            else:
                raise exceptions.SpinnMachineInvalidParameterException(
                    "version, width, height, with_wrap_arounds",
                    "{}, {}, {}, {}".format(
                        version, width, height, with_wrap_arounds),
                    "A generic machine with wrap arounds None"
                    " must be either have a width and height "
                    " which are both either 2 or 8 or a width"
                    " and height that are divisible by 12"
                    " or a width - 4 and height - 4 that are divisible by 12"
                    .format(version))

        if (version is None and (with_wrap_arounds is True) and
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

        if (version is None and (with_wrap_arounds is False) and
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

        if with_wrap_arounds is None:
            logger.debug("width = {}, height = {} and auto wrap arounds"
                         .format(width, height))
        else:
            self._with_wrap_arounds = with_wrap_arounds
            logger.debug("width = {}, height = {} and wrap arounds {}"
                         .format(width, height, self._with_wrap_arounds))

        # Set up the maximum chip x and y
        self._max_chip_x = width - 1
        self._max_chip_y = height - 1
        # Set the maximum board that will be filled in lazy unless set as down
        self._original_width = width
        self._original_height = height

        # Store the details
        self._n_cpus_per_chip = n_cpus_per_chip
        self._sdram_per_chip = sdram_per_chip
        if with_monitors:
            self._with_monitors = 1
        else:
            self._with_monitors = 0
        self._default_processors = dict()

        # Store the down items
        self._down_cores = down_cores if down_cores is not None else set()
        self._down_links = down_links if down_links is not None else set()
        if version == 2 or version == 3:
            self._down_links.update(VirtualMachine._4_chip_down_links)
        if down_chips is None:
            down_chips = []

        # add storage for any chips added later
        self._extra_chips = OrderedSet()

        # Calculate the Ethernet connections in the machine, assuming 48-node
        # boards
        n_ethernets = 0
        ethernet_chips = []
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
                    if (x, y) not in down_chips:
                        n_ethernets += 1
                        ethernet_chips.append((x, y))

        # Compute list of chips that are possible based on configuration
        # If there are no wrap arounds, and the the size is not 2 * 2,
        # the possible chips depend on the 48 chip board's gaps
        if height > 2 and not self._with_wrap_arounds:

            # Find all the chips that are on the board
            self._configured_chips = OrderedSet({
                (x + eth_x, y + eth_y) for x in range(8) for y in range(8)
                for eth_x, eth_y in ethernet_chips
                if (x, y) not in Machine.BOARD_48_CHIP_GAPS and
                (x, y) not in down_chips
            })
        else:
            self._configured_chips = OrderedSet((x, y) for x in range(width)
                                                for y in range(height) if
                                                (x, y) not in down_chips)

        # Assign "ip addresses" to the Ethernet chips
        for i in range(len(ethernet_chips)):
            (a, b) = divmod(i + 1, 128)
            ip_address = "127.0.{}.{}".format(a, b)
            (x, y) = ethernet_chips[i]
            new_chip = self._create_chip(x, y, ip_address)
            Machine.add_chip(self, new_chip)

        self.add_spinnaker_links(version)
        self.add_fpga_links(version)

    def add_chip(self, chip):
        """ Add a chip to the machine

        :param chip: The chip to add to the machine
        :type chip: :py:class:`spinn_machine.chip.Chip`
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    a chip with the same x and y coordinates already exists
        """
        if self.is_chip_at(chip.x, chip.y):
            raise exceptions.SpinnMachineAlreadyExistsException(
                "chip", "{}, {}".format(chip.x, chip.y))
        Machine.add_chip(self, chip)
        self._extra_chips.add((chip.x, chip.y))

    @property
    def chips(self):
        for (x, y) in self.chip_coordinates:
            if not (x, y) in self._chips:
                Machine.add_chip(self, self._create_chip(x, y))
            yield self._chips[(x, y)]

    @property
    def chip_coordinates(self):
        for (x, y) in self._configured_chips:
            yield (x, y)
        for (x, y) in self._extra_chips:
            yield (x, y)

    def __iter__(self):
        for (x, y) in self.chip_coordinates:
            if not (x, y) in self._chips:
                Machine.add_chip(self, self._create_chip(x, y))
            yield (x, y), self._chips[(x, y)]

    def get_chip_at(self, x, y):
        if not self.is_chip_at(x, y):
            return None
        if (x, y) not in self._chips:
            Machine.add_chip(self, self._create_chip(x, y))
        chip_id = (x, y)
        return self._chips[chip_id]

    def is_chip_at(self, x, y):
        if (x, y) in self._configured_chips:
            return True
        if (x, y) in self._extra_chips:
            return True
        return False

    def is_link_at(self, x, y, link):
        if (x, y) in self._chips:
            return self._chips[x, y].router.is_link(link)
        if link == 0:
            return self._creatable_link(
                link_from=link, source_x=x, source_y=x,
                destination_x=x + 1, destination_y=y)
        if link == 1:
            return self._creatable_link(
                link_from=link, source_x=x, source_y=x,
                destination_x=x + 1, destination_y=y + 1)
        if link == 2:
            return self._creatable_link(
                link_from=link, source_x=x, source_y=x,
                destination_x=x, destination_y=y + 1)
        if link == 3:
            return self._creatable_link(
                link_from=link, source_x=x, source_y=x,
                destination_x=x - 1, destination_y=y)
        if link == 4:
            return self._creatable_link(
                link_from=link, source_x=x, source_y=x,
                destination_x=x - 1, destination_y=y - 1)
        if link == 5:
            return self._creatable_link(
                link_from=link, source_x=x, source_y=x,
                destination_x=x, destination_y=y - 1)
        return False  # Illegal link value

    @property
    def n_chips(self):
        return len(self._configured_chips) + len(self._extra_chips)

    def __str__(self):
        return "[VirtualMachine: max_x={}, max_y={}]".format(
            self._max_chip_x, self._max_chip_y)

    def get_cores_and_link_count(self):
        n_cores = (
            (self.n_chips * self._n_cpus_per_chip) - len(self._down_cores)
        )
        n_links = self.n_chips * 6 - len(self._down_links)
        return n_cores, n_links

    def _create_processors_general(self, num_monitors):
        processors = list()
        for processor_id in range(0, num_monitors):
            processor = Processor(processor_id, is_monitor=True)
            processors.append(processor)
        for processor_id in range(num_monitors, self._n_cpus_per_chip):
            processor = Processor(processor_id, is_monitor=False)
            processors.append(processor)
        return processors

    def _create_processors_specific(self, x, y):
        processors = list()
        for processor_id in range(0, self._with_monitors):
            if (x, y, processor_id) not in self._down_cores:
                processor = Processor(processor_id, is_monitor=True)
                processors.append(processor)
        for processor_id in range(self._with_monitors, self._n_cpus_per_chip):
            if (x, y, processor_id) not in self._down_cores:
                processor = Processor(processor_id, is_monitor=False)
                processors.append(processor)
        return processors

    def _create_chip(self, x, y, ip_address=None):
        down = False
        for processor_id in range(self._n_cpus_per_chip):
            if (x, y, processor_id) in self._down_cores:
                down = True
                break
        if down:
            processors = self._create_processors_specific(x, y)
        else:
            if self._with_monitors not in self._default_processors:
                self._default_processors[self._with_monitors] = \
                    self._create_processors_general(self._with_monitors)
            processors = self._default_processors[self._with_monitors]
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

    def _add_link(self, links, link_from, source_x, source_y,
                  destination_x, destination_y):
        if self._creatable_link(link_from, source_x, source_y,
                                destination_x, destination_y):
            link_to = (link_from + 3) % 6
            links.append(
                Link(source_x=source_x, source_y=source_y,
                     destination_x=destination_x, destination_y=destination_y,
                     source_link_id=link_from,
                     multicast_default_from=link_to,
                     multicast_default_to=link_to))

    def _creatable_link(self, link_from, source_x, source_y,
                        destination_x, destination_y):
        if self._with_wrap_arounds:

            # Correct for wrap around
            if destination_x == self._original_width:
                destination_x = 0
            if destination_y == self._original_height:
                destination_y = 0
            if destination_x == -1:
                destination_x = self._original_width - 1
            if destination_y == -1:
                destination_y = self._original_height - 1

        # Check only against chips that can be created
        # Chips directly added will have the links directly added as well
        if not (source_x, source_y) in self._configured_chips:
            return False
        if not (destination_x, destination_y) in self._configured_chips:
            return False
        if (source_x, source_y, link_from) in self._down_links:
            return False
        return True

    def reserve_system_processors(self):
        """ Sets one of the none monitor system processors as a system\
            processor on every Chip

        Updates maximum_user_cores_on_chip

        :rtype None
        """
        # Handle existing chips
        reserved_cores, failed_chips = Machine.reserve_system_processors(self)

        # Go through the remaining cores and get a virtual unused core
        for x, y in self.chip_coordinates:
            if (x, y) not in self._chips:
                core_added = False
                for processor_id in range(0, self._with_monitors):
                    if (x, y, processor_id) not in self._down_cores:
                        reserved_cores.add_processor(x, y, processor_id)
                        core_added = True
                        break

                if not core_added:
                    failed_chips.append((x, y))

        # Ensure future chips get an extra monitor
        self._with_monitors += 1

        return reserved_cores, failed_chips

    @property
    def maximum_user_cores_on_chip(self):
        return max(self._maximum_user_cores_on_chip,
                   self._n_cpus_per_chip - self._with_monitors)
