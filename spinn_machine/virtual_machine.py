from spinn_machine import exceptions
from spinn_machine.machine import Machine
from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM
from spinn_machine.link import Link
from spinn_machine.utilities.progress_bar import ProgressBar

import logging

logger = logging.getLogger(__name__)

_48boardgaps = [
    (0, 4), (0, 5), (0, 6), (0, 7), (1, 5), (1, 6), (1, 7), (2, 6), (2, 7),
    (3, 7), (5, 0), (6, 0), (6, 1), (7, 0), (7, 1), (7, 2)
]


class VirtualMachine(Machine):
    """ A Virtual SpiNNaker machine
    """

    __slots__ = ()

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

        # if x and y are none, assume a 48 chip board
        logger.debug("width = {} and height  = {}".format(width, height))

        # calculate if there are multiple Ethernet connections in the machine
        ethernet_connected_chips = dict()
        ethernet_connected_chip_ids = dict()
        if ((width * height) % 48) == 0:

            # able to make a valid multi-board machine from size of chips
            ethernet_connected_chips[(0, 0)] = list()
            self._locater_extra_ethernet_connected_chips(
                ethernet_connected_chips, 0, 0, width, height)

            # update ids
            counter = 1
            for (e_x, e_y) in ethernet_connected_chips:
                ethernet_connected_chip_ids[(e_x, e_y)] = \
                    "127.0.0.{}".format(counter)
                counter += 1

            # allocate chips to the area codes from standard 48 chips
            self._allocate_chips_to_area_codes(
                ethernet_connected_chips, width, height)
        else:
            ethernet_connected_chips[(0, 0)] = list()
            ethernet_connected_chip_ids[(0, 0)] = "127.0.0.1"
            for i in xrange(width):
                for j in xrange(height):
                    ethernet_connected_chips[(0, 0)].append((i, j))

        # calculate the chip ids which this machine is going to have
        chip_ids = list()
        for i in xrange(width):
            for j in xrange(height):
                coords = (i, j)
                if (version == 5 and width == 8 and height == 8 and
                        coords in _48boardgaps):

                    # a chip doesn't exist in this static position
                    # on these boards, so nullify it
                    pass
                elif down_chips is None or not down_chips.is_chip(i, j):
                    chip_ids.append((i, j))

        progress_bar = ProgressBar(
            width * height, "Generating a virtual machine")

        # Create the chips and their links
        for i in xrange(width):
            for j in xrange(height):
                coords = (i, j)
                if (version == 5 and width == 8 and height == 8 and
                        coords in _48boardgaps):

                    # a chip doesn't exist in this static position
                    # on these boards, so nullify it
                    pass
                else:
                    processors = list()
                    for processor_id in range(0, n_cpus_per_chip):
                        if down_cores is None or not down_cores.is_core(
                                i, j, processor_id):
                            processor = Processor(processor_id)
                            if processor_id == 0 and with_monitors:
                                processor.is_monitor = True
                            processors.append(processor)
                    chip_links = self._calculate_links(
                        i, j, width, height, with_wrap_arounds, version,
                        chip_ids, down_links)
                    chip_router = Router(chip_links, False)
                    if sdram_per_chip is None:
                        sdram = SDRAM()
                    else:
                        sdram = SDRAM(sdram_per_chip)
                    ethernet_connected_chip_x = None
                    ethernet_connected_chip_y = None
                    for (e_x, e_y) in ethernet_connected_chips:
                        if (i, j) in ethernet_connected_chips[(e_x, e_y)]:
                            ethernet_connected_chip_x = e_x
                            ethernet_connected_chip_y = e_y

                    if (i, j) in ethernet_connected_chip_ids:
                        ip_address = ethernet_connected_chip_ids[(i, j)]
                    else:
                        ip_address = None

                    chip = Chip(
                        i, j, processors, chip_router, sdram,
                        ethernet_connected_chip_x, ethernet_connected_chip_y,
                        ip_address)
                    self.add_chip(chip)

                progress_bar.update()

        progress_bar.end()

        processor_count = 0
        for chip in self.chips:
            processor_count += len(list(chip.processors))

        link_count = 0
        for chip in self.chips:
            link_count += len(list(chip.router.links))

        logger.debug(
            "Static Allocation Complete;"
            " {} calculated app cores and {} links!".format(
                processor_count, link_count))

    def _locater_extra_ethernet_connected_chips(
            self, ethernet_connected_chips, start_x, start_y, height, width):
        if start_x + 12 < width:
            ethernet_connected_chips[(start_x + 12, start_y)] = list()
            self._locater_extra_ethernet_connected_chips(
                ethernet_connected_chips, start_x + 12, start_y, width, height)
        if start_x + 8 < width and start_y + 4 < height:
            ethernet_connected_chips[(start_x + 8, start_y + 4)] = list()
            self._locater_extra_ethernet_connected_chips(
                ethernet_connected_chips, start_x + 8, start_y + 4,
                width, height)
        if start_x + 4 < width and start_y + 8 < height:
            ethernet_connected_chips[(start_x + 4, start_y + 8)] = list()
            self._locater_extra_ethernet_connected_chips(
                ethernet_connected_chips, start_x + 4, start_y + 8,
                width, height)
        if start_y + 12 < height:
            ethernet_connected_chips[(start_x, start_y + 12)] = list()
            self._locater_extra_ethernet_connected_chips(
                ethernet_connected_chips, start_x, start_y + 12, width, height)

    @staticmethod
    def _allocate_chips_to_area_codes(
            ethernet_connected_chips, width, height):
        # positions to move relative to the Ethernet connected chip.
        # means move right [first] then move up [second] add [third] going
        # right
        position_edges = ((0, 0, 5), (0, 1, 6), (0, 2, 7),
                          (0, 3, 8), (1, 4, 7), (2, 5, 6),
                          (3, 6, 5), (4, 7, 4))
        for (ex, ey) in ethernet_connected_chips:
            for (move_right, move_up, add) in position_edges:
                start_x = ex + move_right
                start_y = ey + move_up
                for _ in range(add):
                    if start_y < width and start_x < height:
                        ethernet_connected_chips[(ex, ey)].append(
                            (start_x, start_y))
                    else:
                        start_y = start_y % width
                        start_x = start_x % height
                        ethernet_connected_chips[(ex, ey)].append(
                            (start_x, start_y))
                    start_x += 1

    def _calculate_links(
            self, x, y, width, height, wrap_around, version, chip_ids,
            down_links):
        """ Calculate the links needed for a machine structure
        """
        if width == 2 and height == 2:
            return self._initialize_neighbour_links_for_4_chip_board(
                x, y, wrap_around, version, down_links)
        else:
            return self._initialize_neighbour_links_for_other_boards(
                x, y, width - 1, height - 1, wrap_around, chip_ids, down_links)

    @staticmethod
    def _initialize_neighbour_links_for_4_chip_board(
            x, y, wrap_around, version, down_links):
        """ Create links for a chip on a 4-chip board
        """
        links = list()

        if x == 0 and y == 0:
            if down_links is None or ((0, 0), (0, 1), 0) not in down_links:
                links.append(Link(
                    source_x=0, source_y=0, destination_y=0,
                    destination_x=1, source_link_id=0,
                    multicast_default_from=3, multicast_default_to=3))
            if down_links is None or ((0, 0), (1, 1), 1) not in down_links:
                links.append(Link(
                    source_x=0, source_y=0, destination_y=1,
                    destination_x=1, source_link_id=1,
                    multicast_default_from=4, multicast_default_to=4))
            if down_links is None or ((0, 0), (1, 0), 2) not in down_links:
                links.append(Link(
                    source_x=0, source_y=0, destination_y=1,
                    destination_x=0, source_link_id=2,
                    multicast_default_from=5, multicast_default_to=5))

            if wrap_around:
                if down_links is None or ((0, 0), (1, 0), 5) not in down_links:
                    links.append(Link(
                        source_x=0, source_y=0, destination_y=1,
                        destination_x=0, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))

                if version is None:
                    if (down_links is None or
                            ((0, 0), (1, 1), 4) not in down_links):
                        links.append(Link(
                            source_x=0, source_y=0, destination_y=1,
                            destination_x=1, source_link_id=4,
                            multicast_default_from=1, multicast_default_to=1))
                    if (down_links is None or
                            ((0, 0), (0, 1), 3) not in down_links):
                        links.append(Link(
                            source_x=0, source_y=0, destination_y=0,
                            destination_x=1, source_link_id=3,
                            multicast_default_from=0, multicast_default_to=0))

        if x == 0 and y == 1:
            if down_links is None or ((0, 1), (1, 1), 0) not in down_links:
                links.append(Link(
                    source_x=0, source_y=1, destination_y=1,
                    destination_x=1, source_link_id=0,
                    multicast_default_from=3, multicast_default_to=3))
            if down_links is None or ((0, 1), (0, 0), 5) not in down_links:
                links.append(Link(
                    source_x=0, source_y=1, destination_y=0,
                    destination_x=0, source_link_id=5,
                    multicast_default_from=2, multicast_default_to=2))

            if wrap_around:
                if down_links is None or ((0, 1), (0, 1), 1) not in down_links:
                    links.append(Link(
                        source_x=0, source_y=1, destination_y=0,
                        destination_x=1, source_link_id=1,
                        multicast_default_from=4, multicast_default_to=4))
                if down_links is None or ((0, 1), (0, 0), 2) not in down_links:
                    links.append(Link(
                        source_x=0, source_y=1, destination_y=0,
                        destination_x=0, source_link_id=2,
                        multicast_default_from=5, multicast_default_to=5))

                if version is None:
                    if (down_links is None or
                            ((0, 1), (1, 1), 3) not in down_links):
                        links.append(Link(
                            source_x=0, source_y=1, destination_y=1,
                            destination_x=1, source_link_id=3,
                            multicast_default_from=0, multicast_default_to=0))
                    if (down_links is None or
                            ((0, 1), (0, 1), 4) not in down_links):
                        links.append(Link(
                            source_x=0, source_y=1, destination_y=0,
                            destination_x=1, source_link_id=4,
                            multicast_default_from=1, multicast_default_to=1))

        if x == 1 and y == 0:
            if down_links is None or ((1, 0), (1, 1), 2) not in down_links:
                links.append(Link(
                    source_x=1, source_y=0, destination_y=1,
                    destination_x=1, source_link_id=2,
                    multicast_default_from=5, multicast_default_to=5))
            if down_links is None or ((1, 0), (0, 0), 3) not in down_links:
                links.append(Link(
                    source_x=1, source_y=0, destination_y=0,
                    destination_x=0, source_link_id=3,
                    multicast_default_from=0, multicast_default_to=0))

            if wrap_around:
                if down_links is None or ((1, 0), (1, 0), 4) not in down_links:
                    links.append(Link(
                        source_x=1, source_y=0, destination_y=1,
                        destination_x=0, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))
                if down_links is None or ((1, 0), (1, 1), 5) not in down_links:
                    links.append(Link(
                        source_x=1, source_y=0, destination_y=1,
                        destination_x=1, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))

                if version is None:
                    if (down_links is None or
                            ((1, 0), (1, 0), 1) not in down_links):
                        links.append(Link(
                            source_x=1, source_y=0, destination_y=1,
                            destination_x=0, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))
                    if (down_links is None or
                            ((1, 0), (0, 0), 0) not in down_links):
                        links.append(Link(
                            source_x=1, source_y=0, destination_y=0,
                            destination_x=0, source_link_id=0,
                            multicast_default_from=3, multicast_default_to=3))

        if x == 1 and y == 1:
            if down_links is None or ((1, 1), (0, 0), 4) not in down_links:
                links.append(Link(
                    source_x=1, source_y=1, destination_y=0,
                    destination_x=0, source_link_id=4,
                    multicast_default_from=1, multicast_default_to=1))
            if down_links is None or ((1, 1), (0, 1), 5) not in down_links:
                links.append(Link(
                    source_x=1, source_y=1, destination_y=0,
                    destination_x=1, source_link_id=5,
                    multicast_default_from=2, multicast_default_to=2))
            if down_links is None or ((1, 1), (1, 0), 3) not in down_links:
                links.append(Link(
                    source_x=1, source_y=1, destination_y=1,
                    destination_x=0, source_link_id=3,
                    multicast_default_from=0, multicast_default_to=0))

            if wrap_around:
                if down_links is None or ((1, 1), (0, 1), 2) not in down_links:
                    links.append(Link(
                        source_x=1, source_y=1, destination_y=0,
                        destination_x=1, source_link_id=2,
                        multicast_default_from=5, multicast_default_to=5))

                if version is None:
                    if (down_links is None or
                            ((1, 1), (0, 0), 1) not in down_links):
                        links.append(Link(
                            source_x=1, source_y=1, destination_y=0,
                            destination_x=0, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))
                    if (down_links is None or
                            ((1, 1), (1, 0), 0) not in down_links):
                        links.append(Link(
                            source_x=1, source_y=1, destination_y=1,
                            destination_x=0, source_link_id=0,
                            multicast_default_from=3, multicast_default_to=3))
        return links

    @staticmethod
    def _initialize_neighbour_links_for_other_boards(
            x, y, max_x, max_y, wrap_around, chip_ids, down_links):
        """ Creates links for a chip on any other machine
        """

        links = list()
        is_right_edge = (x == max_x)
        is_left_edge = (x == 0)
        is_top_edge = (y == max_y)
        is_bottom_edge = (y == 0)

        # Deal with links 0, 1, 2
        if not is_right_edge:

            # Not the right edge of the board
            if (x + 1, y) in chip_ids:
                if (down_links is None or
                        ((x, y), (y, x + 1), 0) not in down_links):
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y,
                        destination_x=x + 1, source_link_id=0,
                        multicast_default_from=3, multicast_default_to=3))

            if not is_top_edge:

                # Not the top edge of the board
                if (x + 1, y + 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y + 1, x + 1), 1) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y + 1,
                            destination_x=x + 1, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))
                if (x, y + 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y + 1, x), 2) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y + 1,
                            destination_x=x, source_link_id=2,
                            multicast_default_from=5, multicast_default_to=5))

            elif wrap_around:

                # Top non-right edge of the board
                if (x + 1, 0) in chip_ids:
                    if (down_links is None or
                            ((x, y), (0, x + 1), 1) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=0,
                            destination_x=x + 1, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))
                if (x, 0) in chip_ids:
                    if (down_links is None or
                            ((x, y), (0, x), 2) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=0,
                            destination_x=x, source_link_id=2,
                            multicast_default_from=5, multicast_default_to=5))
        else:

            # Right edge of the board
            if wrap_around:
                if (0, y) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y, 0), 0) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y,
                            destination_x=0, source_link_id=0,
                            multicast_default_from=3, multicast_default_to=3))

            if not is_top_edge:

                # Not the top right corner of the board
                if (x, y + 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y + 1, x), 2) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y + 1,
                            destination_x=x, source_link_id=2,
                            multicast_default_from=5, multicast_default_to=5))
                if (0, y + 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y + 1, 0), 1) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y + 1,
                            destination_x=0, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))

            elif wrap_around:

                # Top right corner of the board
                if (x, 0) in chip_ids:
                    if (down_links is None or
                            ((x, y), (0, x), 2) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=0,
                            destination_x=x, source_link_id=2,
                            multicast_default_from=5, multicast_default_to=5))
                if (0, 0) in chip_ids:
                    if (down_links is None or
                            ((x, y), (0, 0), 1) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=0,
                            destination_x=0, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))

        # Deal with links 3 4 5
        if not is_left_edge:

            # Not the left side of board
            if (x - 1, y) in chip_ids:
                if (down_links is None or
                        ((x, y), (y, x - 1), 3) not in down_links):
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y,
                        destination_x=x - 1, source_link_id=3,
                        multicast_default_from=0, multicast_default_to=0))

            if not is_bottom_edge:

                # Not the bottom side of the board
                if (x - 1, y - 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y - 1, x - 1), 4) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y - 1,
                            destination_x=x - 1, source_link_id=4,
                            multicast_default_from=1, multicast_default_to=1))
                if (x, y - 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y - 1, x), 5) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y - 1,
                            destination_x=x, source_link_id=5,
                            multicast_default_from=2, multicast_default_to=2))

            elif wrap_around:

                # The bottom non-left side of the board
                if (x - 1, max_y) in chip_ids:
                    if (down_links is None or
                            ((x, y), (max_y, x - 1), 4) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=max_y,
                            destination_x=x - 1, source_link_id=4,
                            multicast_default_from=1, multicast_default_to=1))
                if (x, max_y) in chip_ids:
                    if (down_links is None or
                            ((x, y), (max_y, x), 5) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=max_y,
                            destination_x=x, source_link_id=5,
                            multicast_default_from=2, multicast_default_to=2))
        else:

            # The left side of board
            if wrap_around:
                if (max_x, y) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y, max_x), 3) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y,
                            destination_x=max_x, source_link_id=3,
                            multicast_default_from=0, multicast_default_to=0))

            if not is_bottom_edge:

                # Not the bottom left corner of the board
                if (max_x, y - 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y - 1, max_x), 4) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y - 1,
                            destination_x=max_x, source_link_id=4,
                            multicast_default_from=2, multicast_default_to=2))
                if (x, y - 1) in chip_ids:
                    if (down_links is None or
                            ((x, y), (y - 1, x), 5) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y - 1,
                            destination_x=x, source_link_id=5,
                            multicast_default_from=2, multicast_default_to=2))

            elif wrap_around:

                # The bottom left corner of the board
                if (max_x, max_y) in chip_ids:
                    if (down_links is None or
                            ((x, y), (max_y, max_x), 4) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=max_y,
                            destination_x=max_x, source_link_id=4,
                            multicast_default_from=1, multicast_default_to=1))
                if (x, max_y) in chip_ids:
                    if (down_links is None or
                            ((x, y), (max_y, x), 5) not in down_links):
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=max_y,
                            destination_x=x, source_link_id=5,
                            multicast_default_from=2, multicast_default_to=2))

        # Return all the links
        return links
