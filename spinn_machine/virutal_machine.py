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
    """class for using a machien object without a board. virutal based machine

    """

    def __init__(self, x_dimension, y_dimension, with_wrap_arounds,
                 version=None):
        """initator for a virtual machine

        :param x_dimension: the x dimension of the virtual machine
        :param y_dimension: the y dimension of the virtual machine
        :param with_wrap_arounds: bool defining if wrap around links exist
        :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type version: int
        :type x_dimension: int
        :type y_dimension: int
        :type with_wrap_arounds: bool

        :return: None
        :rtype: None
        :raise None: this emthod does not raise any known exceptions
        """
        Machine.__init__(self, ())
        self._initiate_virtual_machine(x_dimension, y_dimension,
                                       with_wrap_arounds, version)

    def _initiate_virtual_machine(self, x_dimension, y_dimension,
                                  with_wrap_arounds, version):
        """main method to build a virutal machien object

        :param x_dimension: the x dimension of the virtual machine
        :param y_dimension: the y dimension of the virtual machine
        :param with_wrap_arounds: bool defining if wrap around links exist
        :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type x_dimension: int
        :type y_dimension: int
        :type with_wrap_arounds: bool
        :type version: int
        :return: None
        :rtype: None
        :raise SpinnMachineInvalidParameterException: when some param is invalid\
        such as the x_dimension or y_dimension is negative
        """

        if x_dimension < 0 or y_dimension < 0:
            raise exceptions.SpinnMachineInvalidParameterException(
                "x_dimension or y_dimension", "value less than 0",
                "the dimensions of the virtual machine are not supported, as a"
                "machine should not have a negaitve dimension")

        # if x and y are none, assume a 48 chip board
        logger.debug("xdim = {} and ydim  = {}".format(x_dimension, y_dimension))
        board48gaps = [(0, 4), (0, 5), (0, 6), (0, 7), (1, 5), (1, 6), (1, 7),
                       (2, 6), (2, 7), (3, 7), (5, 0), (6, 0), (6, 1), (7, 0),
                       (7, 1), (7, 2)]
        for i in xrange(x_dimension):
            for j in xrange(y_dimension):
                coords = (i, j)
                if x_dimension >= 8 and y_dimension >= 8 \
                   and coords in board48gaps:
                    pass
                    # a chip doesn't exist in this static position
                    # on these boards, so nullify it
                else:
                    processors = list()
                    for processor_id in range(0, 18):
                        processors.append(Processor(processor_id, 200000000))
                    chip_links = \
                        self._calcualte_links(i, j, x_dimension, y_dimension,
                                              with_wrap_arounds, version)
                    chip_router = Router(chip_links, False)
                    sdram = SDRAM()

                    chip = Chip(i, j, processors, chip_router, sdram)
                    self.add_chip(chip)

        processor_count = 0
        for chip in self.chips:
            processor_count += len(chip.processors)

        link_count = 0
        for chip in self.chips:
            link_count += len(chip.router.links)

        logger.debug(
            "Static Allocation Complete. {} calculated app cores and {} links!"
            .format(processor_count, link_count))

    def _calcualte_links(self, x, y, x_dimension, y_dimension, wrap_around,
                         version):
        """calcualtes the links needed for a machine strucutre

        :param x: chip x coord
        :param y: chip y coord
        :param x_dimension: max size of machine in x dimension
        :param y_dimension: max size of machine in y dimension
        :param wrap_around: bool saying if wrap arounds should be considered
        :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type version: int
        :type x: int
        :type y: int
        :type x_dimension: int
        :type y_dimension: int
        :type wrap_around: bool
        :return: iterbale of links
        :rtype: iterable of spinnmachine.link.Link
        :raise SpinnMachineInvalidParameterException: when te virtual machine\
        cannot figure how to wire it.

        """
        if x_dimension == 2 and y_dimension == 2:
            return self._initlize_neighbour_links_for_4_chip_board(x, y,
                                                                   wrap_around,
                                                                   version)
        elif x_dimension == 8 and y_dimension == 8:
            return self._initlize_neighbour_links_for_other_boards(
                x, y, x_dimension - 1, y_dimension - 1, wrap_around, version)
        else:
            raise exceptions.SpinnMachineInvalidParameterException(
                "x_dimension, and y_dimension",
                "the combination has no known wiring,"
                "EXPLORE: I don't know how to interconnect the chips of "
                "this machine, needs to be explored dynamically", "")

    @staticmethod
    def _initlize_neighbour_links_for_4_chip_board(x, y, wrap_around,
                                                   version):
        """creates links for a 4 chip board's chip

        :param x: the x corod of the chip
        :param y: the y corod of the chip
        :param wrap_around: bool if wrapa rounds should be considered
         :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type version: int
        :type x: int
        :type y: int
        :type wrap_around: bool
        :return  iterbale of links
        :rtype: iterable of spinnmachine.link.Link
        :raise none: this emthod does not raise any known exception
        """
        links = list()
        if x == 0 and y == 0:
            links.append(Link(source_x=0, source_y=0, destination_y=0,
                              destination_x=1, source_link_id=0,
                              multicast_default_from=3, multicast_default_to=3))
            links.append(Link(source_x=0, source_y=0, destination_y=1,
                              destination_x=1, source_link_id=1,
                              multicast_default_from=4, multicast_default_to=4))
            links.append(Link(source_x=0, source_y=0, destination_y=1,
                              destination_x=0, source_link_id=2,
                              multicast_default_from=5, multicast_default_to=5))
            if wrap_around:
                links.append(Link(source_x=0, source_y=0, destination_y=0,
                                  destination_x=1, source_link_id=5,
                                  multicast_default_from=2,
                                  multicast_default_to=2))

                if version is None:
                    links.append(Link(source_x=0, source_y=0, destination_y=1,
                                      destination_x=1, source_link_id=4,
                                      multicast_default_from=1,
                                      multicast_default_to=1))
                    links.append(Link(source_x=0, source_y=0, destination_y=1,
                                      destination_x=0, source_link_id=3,
                                      multicast_default_from=0,
                                      multicast_default_to=0))
        if x == 0 and y == 1:
            links.append(Link(source_x=0, source_y=1, destination_y=1,
                              destination_x=1, source_link_id=0,
                              multicast_default_from=3, multicast_default_to=3))
            links.append(Link(source_x=0, source_y=1, destination_y=0,
                              destination_x=0, source_link_id=5,
                              multicast_default_from=2, multicast_default_to=2))
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
                              multicast_default_from=5, multicast_default_to=5))
            links.append(Link(source_x=1, source_y=0, destination_y=0,
                              destination_x=0, source_link_id=3,
                              multicast_default_from=0, multicast_default_to=0))
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
                              multicast_default_from=1, multicast_default_to=1))
            links.append(Link(source_x=1, source_y=1, destination_y=0,
                              destination_x=1, source_link_id=5,
                              multicast_default_from=2, multicast_default_to=2))
            links.append(Link(source_x=1, source_y=1, destination_y=1,
                              destination_x=0, source_link_id=3,
                              multicast_default_from=0, multicast_default_to=0))
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
    def _initlize_neighbour_links_for_other_boards(x, y, max_x, max_y,
                                                   wrap_around, version):
        """creates links for a 48 chip board's chip

        :param x: the x corod of the chip
        :param y: the y corod of the chip
        :param max_x: the max value of a chip in the x dimension
        :param max_y: the max value of a chip in the y dimension
        :param wrap_around: bool if wrapa rounds should be considered
        :param version: the version id of a board. if set to none, then a \
        dimensional version of a board is produces, if a version is given the \
        virtual board reflects whatever links exist on that board version
        :type version: int
        :type x: int
        :type y: int
        :type max_x: int
        :type max_y: int
        :type wrap_around: bool
        :return  iterbale of links
        :rtype: iterable of spinnmachine.link.Link
        :raise none: this emthod does not raise any known exception
        """

        links = list()
        #deal with the 3 basic links from 0 to 2
        if x < max_x:  # sits away from the right edge of the board
            links.append(Link(source_x=x, source_y=y, destination_y=y,
                              destination_x=x + 1, source_link_id=0,
                              multicast_default_from=3, multicast_default_to=3))
            if y < max_y:  # sits away from the top edge of the board
                links.append(Link(source_x=x, source_y=y, destination_y=y + 1,
                                  destination_x=x + 1, source_link_id=1,
                                  multicast_default_from=4,
                                  multicast_default_to=4))
                links.append(Link(source_x=x, source_y=y, destination_y=y + 1,
                                  destination_x=x, source_link_id=2,
                                  multicast_default_from=5,
                                  multicast_default_to=5))
            elif wrap_around and version is None:  # top edge of the board
                links.append(Link(source_x=x, source_y=y, destination_y=0,
                                  destination_x=x + 1, source_link_id=1,
                                  multicast_default_from=4,
                                  multicast_default_to=4))
                links.append(Link(source_x=x, source_y=y, destination_y=0,
                                  destination_x=x, source_link_id=2,
                                  multicast_default_from=5,
                                  multicast_default_to=5))
        else:  # sits on the right edge of the board
            if wrap_around and version is None:
                links.append(Link(source_x=x, source_y=y, destination_y=y,
                                  destination_x=0, source_link_id=0,
                                  multicast_default_from=3,
                                  multicast_default_to=3))
            if y < max_y:  # does not sit at the top edge of the board
                links.append(Link(source_x=x, source_y=y, destination_y=y + 1,
                                  destination_x=x, source_link_id=2,
                                  multicast_default_from=5,
                                  multicast_default_to=5))
            elif wrap_around and version is None:  # sits on the top edge of the board
                links.append(Link(source_x=x, source_y=y, destination_y=0,
                                  destination_x=x, source_link_id=2,
                                  multicast_default_from=5,
                                  multicast_default_to=5))
            #dealing with top right link
            if wrap_around and version is None:
                if y < max_y:  # if not at top corner, then  go up and around
                    links.append(Link(source_x=x, source_y=y,
                                      destination_y=y + 1,
                                      destination_x=0, source_link_id=1,
                                      multicast_default_from=4,
                                      multicast_default_to=4))
                else:  # if at top corner, so around to 0 0
                    links.append(Link(source_x=x, source_y=y,
                                      destination_y=0,
                                      destination_x=0, source_link_id=1,
                                      multicast_default_from=4,
                                      multicast_default_to=4))
        #deal with the links 3 4 5
        if x != 0:  # not on left side of baord
            links.append(Link(source_x=x, source_y=y, destination_y=y,
                              destination_x=x - 1, source_link_id=3,
                              multicast_default_from=0, multicast_default_to=0))
            if y != 0:  # not in bottom side of the board
                links.append(Link(source_x=x, source_y=y, destination_y=y - 1,
                                  destination_x=x - 1, source_link_id=4,
                                  multicast_default_from=1,
                                  multicast_default_to=1))
                links.append(Link(source_x=x, source_y=y, destination_y=y - 1,
                                  destination_x=x, source_link_id=5,
                                  multicast_default_from=2,
                                  multicast_default_to=2))
            elif wrap_around and version is None:  # in the bottom side of the board
                links.append(Link(source_x=x, source_y=y, destination_y=max_y,
                                  destination_x=x - 1, source_link_id=4,
                                  multicast_default_from=1,
                                  multicast_default_to=1))
                links.append(Link(source_x=x, source_y=y, destination_y=max_y,
                                  destination_x=x, source_link_id=5,
                                  multicast_default_from=2,
                                  multicast_default_to=2))
        else:  # on left side of board
            if wrap_around and version is None:
                links.append(Link(source_x=x, source_y=y, destination_y=y,
                                  destination_x=max_x, source_link_id=3,
                                  multicast_default_from=0,
                                  multicast_default_to=0))
            if y != 0:  # not on the bottom side of the board
                links.append(Link(source_x=x, source_y=y, destination_y=y - 1,
                                  destination_x=x - 1, source_link_id=4,
                                  multicast_default_from=1,
                                  multicast_default_to=1))
                links.append(Link(source_x=x, source_y=y, destination_y=y - 1,
                                  destination_x=x, source_link_id=5,
                                  multicast_default_from=2,
                                  multicast_default_to=2))
            elif wrap_around and version is None:  # in the bottom corner of the board
                links.append(Link(source_x=x, source_y=y, destination_y=max_y,
                                  destination_x=max_x, source_link_id=4,
                                  multicast_default_from=1,
                                  multicast_default_to=1))
                links.append(Link(source_x=x, source_y=y, destination_y=max_y,
                                  destination_x=x, source_link_id=5,
                                  multicast_default_from=2,
                                  multicast_default_to=2))
        return links