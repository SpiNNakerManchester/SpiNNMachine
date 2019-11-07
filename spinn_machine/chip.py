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

from collections import OrderedDict
from six import iteritems, itervalues
from spinn_utilities.ordered_set import OrderedSet
from .processor import Processor

standard_processors = {}


class Chip(object):
    """ Represents a SpiNNaker chip with a number of cores, an amount of\
        SDRAM shared between the cores, and a router.\
        The chip is iterable over the processors, yielding\
        (processor_id, processor) where:

            * processor_id is the ID of a processor
            * processor is the processor with processor_id
    """

    # tag 0 is reserved for stuff like IO STD
    _IPTAG_IDS = OrderedSet(range(1, 8))

    __slots__ = (
        "_x", "_y", "_p", "_router", "_sdram", "_ip_address", "_virtual",
        "_tag_ids", "_nearest_ethernet_x", "_nearest_ethernet_y",
        "_n_user_processors"
    )

    # pylint: disable=too-many-arguments
    def __init__(self, x, y, n_processors, router, sdram, nearest_ethernet_x,
                 nearest_ethernet_y, ip_address=None, virtual=False,
                 tag_ids=None, down_cores=None):
        """
        :param x: the x-coordinate of the chip's position in the\
            two-dimensional grid of chips
        :type x: int
        :param y: the y-coordinate of the chip's position in the\
            two-dimensional grid of chips
        :type y: int
        :param n_processors: the number of processors including monitor\
            processors.
        :type n_processors: int
        :param router: a router for the chip
        :type router: :py:class:`~spinn_machine.Router`
        :param sdram: an SDRAM for the chip
        :type sdram: :py:class:`~spinn_machine.SDRAM`
        :param ip_address: \
            the IP address of the chip or None if no Ethernet attached
        :type ip_address: str
        :param virtual: boolean which defines if this chip is a virtual one
        :type virtual: bool
        :param tag_ids: IDs to identify the chip for SDP can be empty to
            define no tags or None to allocate tag automatically
            based on if there is an ip_address
        :type tag_ids: iterable(int) or None
        :param nearest_ethernet_x: the nearest Ethernet x coordinate
        :type nearest_ethernet_x: int or None
        :param nearest_ethernet_y: the nearest Ethernet y coordinate
        :type nearest_ethernet_y: int or None
        :param down_cores: Ids of cores that are down for this Chip
        :type down_cores: collection of int
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If processors contains any two processors with the same\
            processor_id
        """
        self._x = x
        self._y = y
        self._p = self.__generate_processors(n_processors, down_cores)
        self._router = router
        self._sdram = sdram
        self._ip_address = ip_address
        if tag_ids is not None:
            self._tag_ids = tag_ids
        elif self._ip_address is None:
            self._tag_ids = []
        else:
            self._tag_ids = self._IPTAG_IDS
        self._virtual = virtual
        self._nearest_ethernet_x = nearest_ethernet_x
        self._nearest_ethernet_y = nearest_ethernet_y

    def __generate_processors(self, n_processors, down_cores):
        global standard_processors
        if down_cores is None:
            if n_processors not in standard_processors:
                processors = OrderedDict()
                processors[0] = Processor.factory(0, True)
                for i in range(1, n_processors):
                    processors[i] = Processor.factory(i)
                standard_processors[n_processors] = processors
            self._n_user_processors = n_processors - 1
            return standard_processors[n_processors]
        else:
            processors = dict()
            if 0 in down_cores:
                raise NotImplementedError(
                    "Declaring core 0 as down is not supported")
            processors[0] = Processor.factory(0, True)
            for i in range(1, n_processors):
                if i not in down_cores:
                    processors[i] = Processor.factory(i)
            self._n_user_processors = n_processors - 1 - len(down_cores)
            return processors

    def is_processor_with_id(self, processor_id):
        """ Determines if a processor with the given ID exists in the chip.\
            Also implemented as __contains__(processor_id)

        :param processor_id: the processor ID to check for
        :type processor_id: int
        :return: Whether the processor with the given ID exists
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        return processor_id in self._p

    def get_processor_with_id(self, processor_id):
        """ Return the processor with the specified ID or None if the\
            processor does not exist.

        :param processor_id: the ID of the processor to return
        :type processor_id: int
        :return: \
            the processor with the specified ID, or None if no such processor
        :rtype: Processor
        :raise None: does not raise any known exceptions
        """
        if processor_id in self._p:
            return self._p[processor_id]
        return None

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

        :rtype: iterable(Processor)
        :raise None: does not raise any known exceptions
        """
        return itervalues(self._p)

    @property
    def n_processors(self):
        """ The total number of processors

        :rtype: int
        """
        return len(self._p)

    @property
    def n_user_processors(self):
        """ The total number of processors that are not monitors

        :rtype: int
        """
        return self._n_user_processors

    @property
    def virtual(self):
        """ Boolean which defines if the chip is virtual or not

        :return: if the chip is virtual
        :rtype: boolean
        :raise None: this method does not raise any known exceptions
        """
        return self._virtual

    @property
    def router(self):
        """ The router object associated with the chip

        :return: router associated with the chip
        :rtype: Router
        :raise None: does not raise any known exceptions
        """
        return self._router

    @property
    def sdram(self):
        """ The SDRAM associated with the chip

        :return: SDRAM associated with the chip
        :rtype: SDRAM
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
        """ The x coordinate of the nearest Ethernet chip

        :return: the x coordinate of the nearest Ethernet chip
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._nearest_ethernet_x

    @property
    def nearest_ethernet_y(self):
        """ The y coordinate of the nearest Ethernet chip

        :return: the y coordinate of the nearest Ethernet chip
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._nearest_ethernet_y

    @property
    def tag_ids(self):
        """ The tag IDs supported by this chip

        :return: the set of IDs.
        :rtype: iterable(int)
        :raise None: this method does not raise any exception
        """
        return self._tag_ids

    def get_first_none_monitor_processor(self):
        """ Get the first processor in the list which is not a monitor core

        :return: a processor, if any non-monitor processors exist
        :rtype: Processor or None
        """
        for processor in self.processors:
            if not processor.is_monitor:
                return processor
        return None

    def __iter__(self):
        """ Get an iterable of processor identifiers and processors

        :return: An iterable of (processor_id, processor) where:
            * processor_id is the ID of a processor
            * processor is the processor with the ID
        :rtype: iterable(int,Processor)
        :raise None: does not raise any known exceptions
        """
        return iteritems(self._p)

    def __len__(self):
        """ The number of processors associated with this chip.

        :return: The number of items in the underlying iterator.
        :rtype: int
        """
        return len(self._p)

    def __getitem__(self, processor_id):
        if processor_id in self._p:
            return self._p[processor_id]
        # Note difference from get_processor_with_id(); this is to conform to
        # standard Python semantics
        raise KeyError(processor_id)

    def __contains__(self, processor_id):
        return self.is_processor_with_id(processor_id)

    __REPR_TEMPLATE = ("[Chip: x={}, y={}, sdram={}, ip_address={}, "
                       "router={}, processors={}, nearest_ethernet={}:{}]")

    def __str__(self):
        return self.__REPR_TEMPLATE.format(
            self._x, self._y, self.sdram, self.ip_address,
            self.router, list(self._p.values()),
            self._nearest_ethernet_x, self._nearest_ethernet_y)

    def __repr__(self):
        return self.__str__()
