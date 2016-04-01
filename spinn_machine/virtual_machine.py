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

    def __init__(
            self, width=None, height=None, with_wrap_arounds=False,
            version=None, n_cpus_per_chip=18, with_monitors=True,
            sdram_per_chip=None):
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
        Machine.__init__(self, ())

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
                else:
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
                        processor = Processor(processor_id, 200000000)
                        if processor_id == 0 and with_monitors:
                            processor.is_monitor = True
                        processors.append(processor)
                    chip_links = self._calculate_links(
                        i, j, width, height, with_wrap_arounds, version,
                        chip_ids)
                    chip_router = Router(chip_links, False)
                    if sdram_per_chip is None:
                        sdram = SDRAM()
                    else:
                        system_base_address = (
                            SDRAM.DEFAULT_BASE_ADDRESS + sdram_per_chip)
                        sdram = SDRAM(system_base_address=system_base_address)

                    chip = Chip(i, j, processors, chip_router, sdram, 0, 0,
                                "127.0.0.1")
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

    def _calculate_links(
            self, x, y, width, height, wrap_around, version, chip_ids):
        """ Calculate the links needed for a machine structure
        """
        if width == 2 and height == 2:
            return self._initialize_neighbour_links_for_4_chip_board(
                x, y, wrap_around, version)
        else:
            return self._initialize_neighbour_links_for_other_boards(
                x, y, width - 1, height - 1, wrap_around, chip_ids)

    @staticmethod
    def _initialize_neighbour_links_for_4_chip_board(
            x, y, wrap_around, version):
        """ Create links for a chip on a 4-chip board
        """
        links = list()

        if x == 0 and y == 0:
            links.append(Link(
                source_x=0, source_y=0, destination_y=0,
                destination_x=1, source_link_id=0,
                multicast_default_from=3, multicast_default_to=3))
            links.append(Link(
                source_x=0, source_y=0, destination_y=1,
                destination_x=1, source_link_id=1,
                multicast_default_from=4, multicast_default_to=4))
            links.append(Link(
                source_x=0, source_y=0, destination_y=1,
                destination_x=0, source_link_id=2,
                multicast_default_from=5, multicast_default_to=5))

            if wrap_around:
                links.append(Link(
                    source_x=0, source_y=0, destination_y=1,
                    destination_x=0, source_link_id=5,
                    multicast_default_from=2, multicast_default_to=2))

                if version is None:
                    links.append(Link(
                        source_x=0, source_y=0, destination_y=1,
                        destination_x=1, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))
                    links.append(Link(
                        source_x=0, source_y=0, destination_y=0,
                        destination_x=1, source_link_id=3,
                        multicast_default_from=0, multicast_default_to=0))

        if x == 0 and y == 1:
            links.append(Link(
                source_x=0, source_y=1, destination_y=1,
                destination_x=1, source_link_id=0,
                multicast_default_from=3, multicast_default_to=3))
            links.append(Link(
                source_x=0, source_y=1, destination_y=0,
                destination_x=0, source_link_id=5,
                multicast_default_from=2, multicast_default_to=2))

            if wrap_around:
                links.append(Link(
                    source_x=0, source_y=1, destination_y=0,
                    destination_x=1, source_link_id=1,
                    multicast_default_from=4, multicast_default_to=4))
                links.append(Link(
                    source_x=0, source_y=1, destination_y=0,
                    destination_x=0, source_link_id=2,
                    multicast_default_from=5, multicast_default_to=5))

                if version is None:
                    links.append(Link(
                        source_x=0, source_y=1, destination_y=1,
                        destination_x=1, source_link_id=3,
                        multicast_default_from=0, multicast_default_to=0))
                    links.append(Link(
                        source_x=0, source_y=1, destination_y=0,
                        destination_x=1, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))

        if x == 1 and y == 0:
            links.append(Link(
                source_x=1, source_y=0, destination_y=1,
                destination_x=1, source_link_id=2,
                multicast_default_from=5, multicast_default_to=5))
            links.append(Link(
                source_x=1, source_y=0, destination_y=0,
                destination_x=0, source_link_id=3,
                multicast_default_from=0, multicast_default_to=0))

            if wrap_around:
                links.append(Link(
                    source_x=1, source_y=0, destination_y=1,
                    destination_x=0, source_link_id=4,
                    multicast_default_from=1, multicast_default_to=1))
                links.append(Link(
                    source_x=1, source_y=0, destination_y=1,
                    destination_x=1, source_link_id=5,
                    multicast_default_from=2, multicast_default_to=2))

                if version is None:
                    links.append(Link(
                        source_x=1, source_y=0, destination_y=1,
                        destination_x=0, source_link_id=1,
                        multicast_default_from=4, multicast_default_to=4))
                    links.append(Link(
                        source_x=1, source_y=0, destination_y=0,
                        destination_x=0, source_link_id=0,
                        multicast_default_from=3, multicast_default_to=3))

        if x == 1 and y == 1:
            links.append(Link(
                source_x=1, source_y=1, destination_y=0,
                destination_x=0, source_link_id=4,
                multicast_default_from=1, multicast_default_to=1))
            links.append(Link(
                source_x=1, source_y=1, destination_y=0,
                destination_x=1, source_link_id=5,
                multicast_default_from=2, multicast_default_to=2))
            links.append(Link(
                source_x=1, source_y=1, destination_y=1,
                destination_x=0, source_link_id=3,
                multicast_default_from=0, multicast_default_to=0))

            if wrap_around:
                links.append(Link(
                    source_x=1, source_y=1, destination_y=0,
                    destination_x=1, source_link_id=2,
                    multicast_default_from=5, multicast_default_to=5))

                if version is None:
                    links.append(Link(
                        source_x=1, source_y=1, destination_y=0,
                        destination_x=0, source_link_id=1,
                        multicast_default_from=4, multicast_default_to=4))
                    links.append(Link(
                        source_x=1, source_y=1, destination_y=1,
                        destination_x=0, source_link_id=0,
                        multicast_default_from=3, multicast_default_to=3))
        return links

    @staticmethod
    def _initialize_neighbour_links_for_other_boards(
            x, y, max_x, max_y, wrap_around, chip_ids):
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
                links.append(Link(
                    source_x=x, source_y=y, destination_y=y,
                    destination_x=x + 1, source_link_id=0,
                    multicast_default_from=3, multicast_default_to=3))

            if not is_top_edge:

                # Not the top edge of the board
                if (x + 1, y + 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y + 1,
                        destination_x=x + 1, source_link_id=1,
                        multicast_default_from=4, multicast_default_to=4))
                if (x, y + 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y + 1,
                        destination_x=x, source_link_id=2,
                        multicast_default_from=5, multicast_default_to=5))

            elif wrap_around:

                # Top non-right edge of the board
                if (x + 1, 0) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=0,
                        destination_x=x + 1, source_link_id=1,
                        multicast_default_from=4, multicast_default_to=4))
                if (x, 0) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=0,
                        destination_x=x, source_link_id=2,
                        multicast_default_from=5, multicast_default_to=5))
        else:

            # Right edge of the board
            if wrap_around:
                if (0, y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y,
                        destination_x=0, source_link_id=0,
                        multicast_default_from=3, multicast_default_to=3))

            if not is_top_edge:

                # Not the top right corner of the board
                if (x, y + 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y + 1,
                        destination_x=x, source_link_id=2,
                        multicast_default_from=5, multicast_default_to=5))
                if (0, y + 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y + 1,
                        destination_x=0, source_link_id=1,
                        multicast_default_from=4, multicast_default_to=4))

            elif wrap_around:

                # Top right corner of the board
                if (x, 0) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=0,
                        destination_x=x, source_link_id=2,
                        multicast_default_from=5, multicast_default_to=5))
                if (0, 0) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=0,
                        destination_x=0, source_link_id=1,
                        multicast_default_from=4, multicast_default_to=4))

        # Deal with links 3 4 5
        if not is_left_edge:

            # Not the left side of board
            if (x - 1, y) in chip_ids:
                links.append(Link(
                    source_x=x, source_y=y, destination_y=y,
                    destination_x=x - 1, source_link_id=3,
                    multicast_default_from=0, multicast_default_to=0))

            if not is_bottom_edge:

                # Not the bottom side of the board
                if (x - 1, y - 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y - 1,
                        destination_x=x - 1, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))
                if (x, y - 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y - 1,
                        destination_x=x, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))

            elif wrap_around:

                # The bottom non-left side of the board
                if (x - 1, max_y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=x - 1, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))
                if (x, max_y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=x, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))
        else:

            # The left side of board
            if wrap_around:
                if (max_x, y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y,
                        destination_x=max_x, source_link_id=3,
                        multicast_default_from=0, multicast_default_to=0))

            if not is_bottom_edge:

                # Not the bottom left corner of the board
                if (max_x, y - 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y - 1,
                        destination_x=max_x, source_link_id=4,
                        multicast_default_from=2, multicast_default_to=2))
                if (x, y - 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y - 1,
                        destination_x=x, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))

            elif wrap_around:

                # The bottom left corner of the board
                if (max_x, max_y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=max_x, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))
                if (x, max_y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=x, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))

        # Return all the links
        return links
