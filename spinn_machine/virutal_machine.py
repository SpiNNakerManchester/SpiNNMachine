from spinn_machine import exceptions
from spinn_machine.machine import Machine

import logging
from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM
from spinn_machine.link import Link

logger = logging.getLogger(__name__)


class VirtualMachine(Machine):
    """class for using a machine object without a board. virtual based machine

    """

    def __init__(self, width, height, with_wrap_arounds,
                 version=None):
        """constructor for a virtual machine

        :param width: the width of the virtual machine in chips
        :type width: int
        :param height: the height of the virtual machine in chips
        :type height: int
        :param with_wrap_arounds: bool defining if wrap around links exist
        :type with_wrap_arounds: bool
        :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type version: int
        :return: None
        :rtype: None
        :raise None: this method does not raise any known exceptions
        """
        Machine.__init__(self, ())
        self._initiate_virtual_machine(width, height,
                                       with_wrap_arounds, version)

    def _initiate_virtual_machine(self, width, height,
                                  with_wrap_arounds, version):
        """main method to build a virtual machine object

        :param width: the width of the virtual machine in chips
        :type width: int
        :param height: the height of the virtual machine in chips
        :type height: int
        :param with_wrap_arounds: bool defining if wrap around links exist
        :type with_wrap_arounds: bool
        :param version: the version id of a board. if set to none, then a \
                dimensional version of a board is produces, if a version is \
                given the virtual board reflects whatever links exist on that \
                board version
        :type version: int
        :return: None
        :rtype: None
        :raise SpinnMachineInvalidParameterException: If the width or height\
                is negative
        """

        if width < 0 or height < 0:
            raise exceptions.SpinnMachineInvalidParameterException(
                "width or height", "value less than 0",
                "the dimensions of the virtual machine are not supported, as a"
                "machine should not have a negative dimension")

        if version == 5 and with_wrap_arounds:
            raise exceptions.SpinnMachineInvalidParameterException(
                "version and with_wrap_arounds",
                "version = 5 and requires wrap arounds",
                "A spinn-5 board on its own requires changes to scamp and "
                "the low level software to support wrap arounds. Therefore "
                "this machine is not acceptable to be generated.")

        if version == 5 and width != 8 and height != 8:
            raise exceptions.SpinnMachineInvalidParameterException(
                "version, width, height",
                "version = 5 whilst height and width do not work out for "
                "a spinn-5",
                "A spinn-5 must have height and width of 8. Please "
                "fix and try again")

        # if x and y are none, assume a 48 chip board
        logger.debug("width = {} and height  = {}"
                     .format(width, height))
        board48gaps = [(0, 4), (0, 5), (0, 6), (0, 7), (1, 5), (1, 6), (1, 7),
                       (2, 6), (2, 7), (3, 7), (5, 0), (6, 0), (6, 1), (7, 0),
                       (7, 1), (7, 2)]

        # calculate the chip ids which this machine is going to have
        chip_ids = list()
        for i in xrange(width):
            for j in xrange(height):
                coords = (i, j)
                if (version == 5 and width == 8 and height == 8 and
                        coords in board48gaps):
                    pass
                    # a chip doesn't exist in this static position
                    # on these boards, so nullify it
                else:
                    chip_ids.append((i, j))

        for i in xrange(width):
            for j in xrange(height):
                coords = (i, j)
                if (version == 5 and width == 8 and height == 8 and
                        coords in board48gaps):
                    pass
                    # a chip doesn't exist in this static position
                    # on these boards, so nullify it
                else:
                    processors = list()
                    for processor_id in range(0, 18):
                        processors.append(Processor(processor_id, 200000000))
                    chip_links = self._calculate_links(
                        i, j, width, height, with_wrap_arounds, version,
                        chip_ids)
                    chip_router = Router(chip_links, False)
                    sdram = SDRAM()

                    chip = Chip(i, j, processors, chip_router, sdram, 0, 0,
                                "127.0.0.1")
                    self.add_chip(chip)

        processor_count = 0
        for chip in self.chips:
            processor_count += len(list(chip.processors))

        link_count = 0
        for chip in self.chips:
            link_count += len(list(chip.router.links))

        logger.debug(
            "Static Allocation Complete. {} calculated app cores and {} links!"
            .format(processor_count, link_count))

    def _calculate_links(
            self, x, y, width, height, wrap_around, version, chip_ids):
        """ calculates the links needed for a machine structure

        :param x: chip x coord
        :param y: chip y coord
        :param width: the width of the virtual machine in chips
        :type width: int
        :param height: the height of the virtual machine in chips
        :type height: int
        :param wrap_around: bool defining if wrap around links exist
        :type wrap_around: bool
        :param version: the version id of a board. if set to none, then a \
                dimensional version of a board is produces, if a version is \
                given the virtual board reflects whatever links exist on that \
                board version
        :param chip_ids: the list of ids that this machine will have for
        its chips
        :type chip_ids: iterable of tuple (x, y)
        :type version: int
        :return: iterable of links
        :rtype: iterable of spinn_machine.link.Link
        :raiseNone: this method does not raise any known exceptions

        """
        if width == 2 and height == 2:
            return self._initialize_neighbour_links_for_4_chip_board(
                x, y, wrap_around, version)
        else:
            return self._initialize_neighbour_links_for_other_boards(
                x, y, width - 1, height - 1, wrap_around, version, chip_ids)

    @staticmethod
    def _initialize_neighbour_links_for_4_chip_board(
            x, y, wrap_around, version):
        """creates links for a 4 chip board's chip

        :param x: the x coordinate of the chip
        :type x: int
        :param y: the y coordinate of the chip
        :type y: int
        :param wrap_around: bool if wrap rounds should be considered
        :type wrap_around: bool
        :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type version: int
        :return  iterable of links
        :rtype: iterable of spinn_machine.link.Link
        :raise none: this method does not raise any known exception
        """
        links = list()
        if x == 0 and y == 0:
            links.append(Link(source_x=0, source_y=0, destination_y=0,
                              destination_x=1, source_link_id=0,
                              multicast_default_from=3,
                              multicast_default_to=3))
            links.append(Link(source_x=0, source_y=0, destination_y=1,
                              destination_x=1, source_link_id=1,
                              multicast_default_from=4,
                              multicast_default_to=4))
            links.append(Link(source_x=0, source_y=0, destination_y=1,
                              destination_x=0, source_link_id=2,
                              multicast_default_from=5,
                              multicast_default_to=5))
            if wrap_around:
                links.append(Link(source_x=0, source_y=0, destination_y=1,
                                  destination_x=0, source_link_id=5,
                                  multicast_default_from=2,
                                  multicast_default_to=2))

                if version is None:
                    links.append(Link(source_x=0, source_y=0, destination_y=1,
                                      destination_x=1, source_link_id=4,
                                      multicast_default_from=1,
                                      multicast_default_to=1))
                    links.append(Link(source_x=0, source_y=0, destination_y=0,
                                      destination_x=1, source_link_id=3,
                                      multicast_default_from=0,
                                      multicast_default_to=0))
        if x == 0 and y == 1:
            links.append(Link(source_x=0, source_y=1, destination_y=1,
                              destination_x=1, source_link_id=0,
                              multicast_default_from=3,
                              multicast_default_to=3))
            links.append(Link(source_x=0, source_y=1, destination_y=0,
                              destination_x=0, source_link_id=5,
                              multicast_default_from=2,
                              multicast_default_to=2))
            if wrap_around:
                links.append(Link(source_x=0, source_y=1, destination_y=0,
                                  destination_x=1, source_link_id=1,
                                  multicast_default_from=4,
                                  multicast_default_to=4))
                links.append(Link(source_x=0, source_y=1, destination_y=0,
                                  destination_x=0, source_link_id=2,
                                  multicast_default_from=5,
                                  multicast_default_to=5))
                if version is None:
                    links.append(Link(source_x=0, source_y=1, destination_y=1,
                                      destination_x=1, source_link_id=3,
                                      multicast_default_from=0,
                                      multicast_default_to=0))
                    links.append(Link(source_x=0, source_y=1, destination_y=0,
                                      destination_x=1, source_link_id=4,
                                      multicast_default_from=1,
                                      multicast_default_to=1))

        if x == 1 and y == 0:
            links.append(Link(source_x=1, source_y=0, destination_y=1,
                              destination_x=1, source_link_id=2,
                              multicast_default_from=5,
                              multicast_default_to=5))
            links.append(Link(source_x=1, source_y=0, destination_y=0,
                              destination_x=0, source_link_id=3,
                              multicast_default_from=0,
                              multicast_default_to=0))
            if wrap_around:
                links.append(Link(source_x=1, source_y=0, destination_y=1,
                                  destination_x=0, source_link_id=4,
                                  multicast_default_from=1,
                                  multicast_default_to=1))
                links.append(Link(source_x=1, source_y=0, destination_y=1,
                                  destination_x=1, source_link_id=5,
                                  multicast_default_from=2,
                                  multicast_default_to=2))
                if version is None:
                    links.append(Link(source_x=1, source_y=0, destination_y=1,
                                      destination_x=0, source_link_id=1,
                                      multicast_default_from=4,
                                      multicast_default_to=4))
                    links.append(Link(source_x=1, source_y=0, destination_y=0,
                                      destination_x=0, source_link_id=0,
                                      multicast_default_from=3,
                                      multicast_default_to=3))
        if x == 1 and y == 1:
            links.append(Link(source_x=1, source_y=1, destination_y=0,
                              destination_x=0, source_link_id=4,
                              multicast_default_from=1,
                              multicast_default_to=1))
            links.append(Link(source_x=1, source_y=1, destination_y=0,
                              destination_x=1, source_link_id=5,
                              multicast_default_from=2,
                              multicast_default_to=2))
            links.append(Link(source_x=1, source_y=1, destination_y=1,
                              destination_x=0, source_link_id=3,
                              multicast_default_from=0,
                              multicast_default_to=0))
            if wrap_around:
                links.append(Link(source_x=1, source_y=1, destination_y=0,
                                  destination_x=1, source_link_id=2,
                                  multicast_default_from=5,
                                  multicast_default_to=5))
                if version is None:
                    links.append(Link(source_x=1, source_y=1, destination_y=0,
                                      destination_x=0, source_link_id=1,
                                      multicast_default_from=4,
                                      multicast_default_to=4))
                    links.append(Link(source_x=1, source_y=1, destination_y=1,
                                      destination_x=0, source_link_id=0,
                                      multicast_default_from=3,
                                      multicast_default_to=3))
        return links

    @staticmethod
    def _initialize_neighbour_links_for_other_boards(
            x, y, max_x, max_y,  wrap_around, version, chip_ids):
        """creates links for a 48 chip board's chip

        :param x: the x coordinate of the chip
        :type x: int
        :param y: the y coordinate of the chip
        :type y: int
        :param max_x: the max value of a chip in the x dimension
        :type max_x: int
        :param max_y: the max value of a chip in the y dimension
        :type max_y: int
        :param wrap_around: bool if wrap rounds should be considered
        :type wrap_around: bool
        :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type version: int
        :return  iterable of links
        :rtype: iterable of spinn_machine.link.Link
        :raise none: this method does not raise any known exception
        """

        links = list()

        # deal with the 3 basic links from 0 to 2
        # sits away from the right edge of the board
        if x < max_x:
            if (x + 1, y) in chip_ids:
                links.append(Link(source_x=x, source_y=y, destination_y=y,
                                  destination_x=x + 1, source_link_id=0,
                                  multicast_default_from=3,
                                  multicast_default_to=3))

            # sits away from the top edge of the board
            if y < max_y:
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
            elif wrap_around and version is None:
                if (x + 1, 0) in chip_ids:
                    # top edge of the board
                    links.append(Link(source_x=x, source_y=y, destination_y=0,
                                      destination_x=x + 1, source_link_id=1,
                                      multicast_default_from=4,
                                      multicast_default_to=4))
                if (x, 0) in chip_ids:
                    links.append(Link(source_x=x, source_y=y, destination_y=0,
                                      destination_x=x, source_link_id=2,
                                      multicast_default_from=5,
                                      multicast_default_to=5))
        else:  # sits on the right edge of the board
            if wrap_around and version is None:
                if (0, y) in chip_ids:
                    links.append(Link(source_x=x, source_y=y, destination_y=y,
                                      destination_x=0, source_link_id=0,
                                      multicast_default_from=3,
                                      multicast_default_to=3))
            if y < max_y:  # does not sit at the top edge of the board
                if (x, y + 1) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y + 1,
                        destination_x=x, source_link_id=2,
                        multicast_default_from=5, multicast_default_to=5))
            elif wrap_around and version is None:
                if (x, 0) in chip_ids:
                    # sits on the top edge of the board
                    links.append(Link(source_x=x, source_y=y, destination_y=0,
                                      destination_x=x, source_link_id=2,
                                      multicast_default_from=5,
                                      multicast_default_to=5))

            # dealing with top right link
            if wrap_around and version is None:
                if y < max_y:
                    if (0, y + 1) in chip_ids:
                        # if not at top corner, then  go up and around
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=y + 1,
                            destination_x=0, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))
                else:
                    if (0, 0) in chip_ids:
                        # if at top corner, so around to 0 0
                        links.append(Link(
                            source_x=x, source_y=y, destination_y=0,
                            destination_x=0, source_link_id=1,
                            multicast_default_from=4, multicast_default_to=4))

        # deal with the links 3 4 5
        # not on left side of board
        if x != 0:
            if (x - 1, y) in chip_ids:
                links.append(Link(source_x=x, source_y=y, destination_y=y,
                                  destination_x=x - 1, source_link_id=3,
                                  multicast_default_from=0,
                                  multicast_default_to=0))
            if y != 0:  # not in bottom side of the board
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
            elif wrap_around and version is None:
                if (x - 1, max_y) in chip_ids:
                    # in the bottom side of the board
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=x - 1, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))
                if (x, max_y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=x, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))
        else:  # on left side of board
            if wrap_around and version is None:
                if (max_x, y) in chip_ids:
                    links.append(Link(source_x=x, source_y=y, destination_y=y,
                                      destination_x=max_x, source_link_id=3,
                                      multicast_default_from=0,
                                      multicast_default_to=0))
            if y != 0:
                if (max_x, y - 1) in chip_ids:
                    # not on the bottom side of the board
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y - 1,
                        destination_x=max_x, source_link_id=4,
                        multicast_default_from=2, multicast_default_to=2))
                if (x, y - 1) in chip_ids:
                    # not on the bottom side of the board
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=y - 1,
                        destination_x=x, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))
            elif wrap_around and version is None:
                if (max_x, max_y) in chip_ids:
                    # in the bottom corner of the board
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=max_x, source_link_id=4,
                        multicast_default_from=1, multicast_default_to=1))
                if (x, max_y) in chip_ids:
                    links.append(Link(
                        source_x=x, source_y=y, destination_y=max_y,
                        destination_x=x, source_link_id=5,
                        multicast_default_from=2, multicast_default_to=2))
        return links
