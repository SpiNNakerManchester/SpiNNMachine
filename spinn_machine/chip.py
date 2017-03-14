from collections import OrderedDict
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException


class Chip(object):

    """ Represents a chip with a number of cores, an amount of SDRAM shared
        between the cores, and a router.\
        The chip is iterable over the processors providing\
        (processor_id, processor) where:

            * processor_id is the id of a processor
            * processor is the processor with processor_id
    """

    # tag 0 is reserved for stuff like IO STD
    IPTAG_IDS = set(range(1, 8))

    __slots__ = (
        "_x", "_y", "_p", "_router", "_sdram", "_ip_address", "_virtual",
        "_tag_ids", "_nearest_ethernet_x", "_nearest_ethernet_y",
        "_n_user_processors"
    )

    def __init__(self, x, y, processors, router, sdram, nearest_ethernet_x,
                 nearest_ethernet_y, ip_address=None, virtual=False,
                 tag_ids=IPTAG_IDS):
        """

        :param x: the x-coordinate of the chip's position in the\
                    two-dimensional grid of chips
        :type x: int
        :param y: the y-coordinate of the chip's position in the\
                    two-dimensional grid of chips
        :type y: int
        :param processors: an iterable of processor objects
        :type processors: iterable of\
                    :py:class:`spinn_machine.processor.Processor`
        :param router: a router for the chip
        :type router: :py:class:`spinn_machine.router.Router`
        :param sdram: an SDRAM for the chip
        :type sdram: :py:class:`spinn_machine.sdram.SDRAM`
        :param ip_address: the IP address of the chip or None if no Ethernet\
                    attached
        :type ip_address: str
        :param virtual: boolean which defines if this chip is a virtual one
        :type virtual: bool
        :param tag_ids: Id to identify the chip for SDP
        :type tag_ids: iterable of int
        :param nearest_ethernet_x: the nearest Ethernet x coord
        :type nearest_ethernet_x: int or None
        :param nearest_ethernet_y: the nearest Ethernet y coord
        :type nearest_ethernet_y: int or None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    processors contains any two processors with the same\
                    processor_id
        """
        self._x = x
        self._y = y
        self._p = OrderedDict()
        self._n_user_processors = 0
        for processor in sorted(processors, key=lambda i: i.processor_id):
            if processor.processor_id in self._p:
                raise SpinnMachineAlreadyExistsException(
                    "processor on {}:{}".format(x, y),
                    str(processor.processor_id))
            self._p[processor.processor_id] = processor
            if not processor.is_monitor:
                self._n_user_processors += 1
        self._router = router
        self._sdram = sdram
        self._ip_address = ip_address
        self._virtual = virtual
        self._tag_ids = tag_ids
        self._nearest_ethernet_x = nearest_ethernet_x
        self._nearest_ethernet_y = nearest_ethernet_y

    def is_processor_with_id(self, processor_id):
        """ Determines if a processor with the given id exists in the chip.\
            Also implemented as __getitem__(processor_id)

        :param processor_id: the processor id to check for
        :type processor_id: int
        :return: True or False based on the existence of the processor
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        return processor_id in self._p

    def __getitem__(self, processor_id):
        """ see :py:meth:`is_processor_with_id`
        """
        return self.is_processor_with_id(processor_id)

    def get_processor_with_id(self, processor_id):
        """ Return the processor with the specified id or None if the\
            processor does not exist.\
            Also implemented as __contains__(processor_id)

        :param processor_id: the id of the processor to return
        :type processor_id: int
        :return: the processor with the specified id or None if no such\
                    processor
        :rtype: :py:class:`spinn_machine.processor.Processor`
        :raise None: does not raise any known exceptions
        """
        if processor_id in self._p:
            return self._p[processor_id]
        return None

    def __contains__(self, processor_id):
        """ see :py:meth:`get_processor_with_id`
        """
        return self.get_processor_with_id(processor_id)

    @property
    def x(self):
        """ The x-coordinate of the chip in the two-dimensional grid of chips

        :return: the x-coordinate of the chip
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip in the two-dimensional grid of chips

        :return: the y-coordinate of the chip
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._y

    @property
    def processors(self):
        """ An iterable of available processors

        :return: iterable of processors
        :rtype: iterable of :py:class:spinn_machine.processor.Processor`
        :raise None: does not raise any known exceptions
        """
        return self._p.itervalues()

    @property
    def n_processors(self):
        """ The total number of processors
        """
        return len(self._p)

    @property
    def n_user_processors(self):
        """ The total number of processors that are not monitors
        """
        return self._n_user_processors

    @property
    def virtual(self):
        """ boolean which defines if the chip is virtual or not

        :return: if the chip is virtual
        :rtype: boolean
        :raise None: this method does not raise any known exceptions
        """
        return self._virtual

    def __iter__(self):
        """ Get an iterable of processor identifiers and processors

        :return: An iterable of (processor_id, processor) where:
                    * procssor_id is the id of a processor
                    * processor is the processor with the id
        :rtype: iterable of (int, :py:class:spinn_machine.processor.Processor`)
        :raise None: does not raise any known exceptions
        """
        return self._p.iteritems()

    @property
    def router(self):
        """ The router object associated with the chip

        :return: router associated with the chip
        :rtype: :py:class:`spinn_machine.router.Router`
        :raise None: does not raise any known exceptions
        """
        return self._router

    @property
    def sdram(self):
        """ The sdram associated with the chip

        :return: sdram associated with the chip
        :rtype: :py:class:`spinn_machine.sdram.SDRAM`
        :raise None: does not raise any known exceptions
        """
        return self._sdram

    @property
    def ip_address(self):
        """ The IP address of the chip

        :return: IP address of the chip, or None if there is no Ethernet\
                    connected to the chip
        :rtype: str
        :raise None: does not raise any known exceptions
        """
        return self._ip_address

    @property
    def nearest_ethernet_x(self):
        """ the x coord of the nearest Ethernet chip

        :return: the x coord of the nearest Ethernet chip
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._nearest_ethernet_x

    @property
    def nearest_ethernet_y(self):
        """ the y coord of the nearest Ethernet chip

        :return: the y coord of the nearest Ethernet chip
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._nearest_ethernet_y

    @property
    def tag_ids(self):
        """ The tag ids supported by this chip

        :return: the set of ids.
        :raise None: this method does not raise any exception
        """
        return self._tag_ids

    def get_first_none_monitor_processor(self):
        """ Get the first processor in the list which is not a monitor core

        :return: a processor
        """
        for processor in self.processors:
            if not processor.is_monitor:
                return processor

    def reserve_a_system_processor(self):
        """ This method should ONLY be called via\
            Machine.reserve_system_processors

        Sets one of the none monitor processors as a system processor

        Updates n_user_processors

        :return:\
            The id of the processor reserved, or None if no processor could\
            be found
        :rtype: int or None
        """
        for processor_id, processor in self._p.iteritems():
            if not processor.is_monitor:
                system_processor = processor.clone_as_system_processor()
                self._p[processor_id] = system_processor
                self._n_user_processors -= 1
                return processor_id

        return None

    def __str__(self):
        return ("[Chip: x={}, y={}, sdram={}, ip_address={}, router={},"
                " processors={}, nearest_ethernet={}:{}]"
                .format(self._x, self._y, self.sdram, self.ip_address,
                        self.router, self._p.values(),
                        self._nearest_ethernet_x, self._nearest_ethernet_y))

    def __repr__(self):
        return self.__str__()
