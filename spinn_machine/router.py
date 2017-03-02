from spinn_machine import exceptions

from collections import OrderedDict


class Router(object):
    """ Represents a router of a chip, with a set of available links.\
        The router is iterable over the links, providing (source_link_id,\
        link) where:

            * source_link_id is the id of a link
            * link is the link with id source_link_id
    """
    ROUTER_DEFAULT_AVAILABLE_ENTRIES = 1024

    ROUTER_DEFAULT_CLOCK_SPEED = 150 * 1024 * 1024

    __slots__ = (
        "_clock_speed", "_emergency_routing_enabled", "_links",
        "_n_available_multicast_entries"
    )

    def __init__(
            self, links, emergency_routing_enabled=False,
            clock_speed=ROUTER_DEFAULT_CLOCK_SPEED,
            n_available_multicast_entries=ROUTER_DEFAULT_AVAILABLE_ENTRIES):
        """
        :param links: iterable of links
        :type links: iterable of :py:class:`spinn_machine.link.Link`
        :param emergency_routing_enabled: Determines if the router emergency\
                    routing is operating
        :type emergency_routing_enabled: bool
        :param clock_speed: The router clock speed in cycles per second
        :type clock_speed: int
        :param n_available_multicast_entries: The number of entries available\
                    in the routing table
        :type n_available_multicast_entries: int
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    any two links have the same source_link_id
        """
        self._links = OrderedDict()
        for link in links:
            self.add_link(link)

        self._emergency_routing_enabled = emergency_routing_enabled
        self._clock_speed = clock_speed
        self._n_available_multicast_entries = n_available_multicast_entries

    def add_link(self, link):
        """ Add a link to the router of the chip

        :param link: The link to be added
        :type link: :py:class:`spinn_machine.link.Link`
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    another link already exists with the same source_link_id
        """
        if link.source_link_id in self._links:
            raise exceptions.SpinnMachineAlreadyExistsException(
                "link", str(link.source_link_id))
        self._links[link.source_link_id] = link

    def is_link(self, source_link_id):
        """ Determine if there is a link with id source_link_id.\
            Also implemented as __contains__(source_link_id)

        :param source_link_id: The id of the link to find
        :type source_link_id: int
        :return: True if there is a link with the given id, False otherwise
        :rtype: bool
        :raise None: No known exceptions are raised
        """
        return source_link_id in self._links

    def __contains__(self, source_link_id):
        """ See :py:meth:`is_link`
        """
        return self.is_link(source_link_id)

    def get_link(self, source_link_id):
        """ Get the link with the given id, or None if no such link.\
            Also implemented as __getitem__(source_link_id)

        :param source_link_id: The id of the link to find
        :type source_link_id: int
        :return: The link, or None if no such link
        :rtype: :py:class:`spinn_machine.link.Link`
        :raise None: No known exceptions are raised
        """
        if source_link_id in self._links:
            return self._links[source_link_id]
        return None

    def __getitem__(self, source_link_id):
        """ See :py:meth:`get_link`
        """
        return self.get_link(source_link_id)

    @property
    def links(self):
        """ The available links of this router

        :return: an iterable of available links
        :rtype: iterable of :py:class:`spinn_machine.link.Link`
        :raise None: does not raise any known exceptions
        """
        return self._links.itervalues()

    def __iter__(self):
        """ Get an iterable of source link ids and links in the router

        :return: an iterable of tuples of (source_link_id, link) where:
                    * source_link_id is the id of the link
                    * link is a router link
        :rtype: iterable of (int, :py:class:`spinn_machine.link.Link`)
        :raise None: does not raise any known exceptions
        """
        return self._links.iteritems()

    @property
    def emergency_routing_enabled(self):
        """ Indicator of whether emergency routing is enabled

        :return: True if emergency routing is enabled, False otherwise
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        return self._emergency_routing_enabled

    @property
    def clock_speed(self):
        """ The clock speed of the router in cycles per second

        :return: The clock speed in cycles per second
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._clock_speed

    @property
    def n_available_multicast_entries(self):
        """ The number of available multicast entries in the routing tables

        :return: The number of available entries
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._n_available_multicast_entries

    @staticmethod
    def convert_routing_table_entry_to_spinnaker_route(routing_table_entry):
        """ Convert a routing table entry represented in software to a\
            binary routing table entry usable on the machine

        :param routing_table_entry: The entry to convert
        :type routing_table_entry:\
            :py:class:`spinnmachine.multicast_routing_entry.MulticastRoutingEntry`
        :rtype: int
        """
        route_entry = 0
        for processor_id in routing_table_entry.processor_ids:
            if processor_id > 26 or processor_id < 0:
                raise exceptions.SpinnMachineInvalidParameterException(
                    "route.processor_ids",
                    str(routing_table_entry.processor_ids),
                    "Processor ids must be between 0 and 26")
            route_entry |= (1 << (6 + processor_id))
        for link_id in routing_table_entry.link_ids:
            if link_id > 5 or link_id < 0:
                raise exceptions.SpinnMachineInvalidParameterException(
                    "route.link_ids", str(routing_table_entry.link_ids),
                    "Link ids must be between 0 and 5")
            route_entry |= (1 << link_id)
        return route_entry

    def get_neighbouring_chips_coords(self):
        """ Utility method to convert links into x and y coordinates

        :return: iterable list of destination coordinates in x and y dict
        :rtype: iterable of dict

        """
        next_hop_chips_coords = list()
        for link in self.links:
            next_hop_chips_coords.append(
                {'x': link.destination_x, 'y': link.destination_y})
        return next_hop_chips_coords

    def __str__(self):
        return (
            "[Router: clock_speed={} MHz, emergency_routing={},"
            "available_entries={}, links={}]".format(
                (self._clock_speed / 1000000),
                self._emergency_routing_enabled,
                self._n_available_multicast_entries, self._links.values()))

    def __repr__(self):
        return self.__str__()
