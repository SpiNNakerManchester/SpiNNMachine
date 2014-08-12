from spinn_machine import exceptions
from spinn_machine.machine import Machine

import logging
from spinn_machine.processor import Processor
from spinn_machine.router import Router
from spinn_machine.chip import Chip
from spinn_machine.sdram import SDRAM

logger = logging.getLogger(__name__)


class VirtualMachine(Machine):
    """class for using a machien object without a board. virutal based machine

    """

    def __init__(self, x_dimension, y_dimension, with_wrap_arounds):
        """initator for a virtual machine

        :param x_dimension: the x dimension of the virtual machine
        :param y_dimension: the y dimension of the virtual machine
        :param with_wrap_arounds: bool defining if wrap around links exist
        :type x_dimension: int
        :type y_dimension: int
        :type with_wrap_arounds: bool
        :return: None
        :rtype: None
        :raise None: this emthod does not raise any known exceptions
        """
        Machine.__init__(self, ())
        self._initiate_virtual_machine(x_dimension, y_dimension,
                                       with_wrap_arounds)

    def _initiate_virtual_machine(self, x_dimension, y_dimension,
                                  with_wrap_arounds):
        """main method to build a virutal machien object

        :param x_dimension: the x dimension of the virtual machine
        :param y_dimension: the y dimension of the virtual machine
        :param with_wrap_arounds: bool defining if wrap around links exist
        :type x_dimension: int
        :type y_dimension: int
        :type with_wrap_arounds: bool
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
                                              with_wrap_arounds)
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

    def _calcualte_links(self, x, y, x_dimension, y_dimension, wrap_around):
        """calcualtes the links needed for a machine strucutre

        :param x: chip x coord
        :param y: chip y coord
        :param x_dimension: max size of machine in x dimension
        :param y_dimension: max size of machine in y dimension
        :param wrap_around: bool saying if wrap arounds should be considered
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
                                                                   wrap_around)
        elif x_dimension == 8 and y_dimension == 8:
            return self._initlize_neighbour_links_for_48_chip_board(x, y,
                                                                    wrap_around)
        else:
            raise exceptions.SpinnMachineInvalidParameterException(
                "x_dimension, and y_dimension",
                "the combination has no known wiring,"
                "EXPLORE: I don't know how to interconnect the chips of "
                "this machine, needs to be explored dynamically", "")

    def _initlize_neighbour_links_for_4_chip_board(self, x, y, wrap_around):
        """creates links for a 4 chip board's chip

        :param x: the x corod of the chip
        :param y: the y corod of the chip
        :param wrap_around: bool if wrapa rounds should be considered
        :type x: int
        :type y: int
        :type wrap_around: bool
        :return  iterbale of links
        :rtype: iterable of spinnmachine.link.Link
        :raise none: this emthod does not raise any known exception
        """
        pass


    def _initlize_neighbour_links_for_48_chip_board(self, x, y, wrap_around):
        """creates links for a 48 chip board's chip

        :param x: the x corod of the chip
        :param y: the y corod of the chip
        :param wrap_around: bool if wrapa rounds should be considered
        :type x: int
        :type y: int
        :type wrap_around: bool
        :return  iterbale of links
        :rtype: iterable of spinnmachine.link.Link
        :raise none: this emthod does not raise any known exception
        """
        pass