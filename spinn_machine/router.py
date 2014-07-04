from collections import OrderedDict
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException

DEFAULT_AVAILABLE_ENTRIES = 1024
DEFAULT_CLOCK_SPEED = 150 * 1024 * 1024

class Router(object):
    """ Represents a router of a chip, with a set of available links.\
        The router is iterable over the links, providing (source_link_id, link)\
        where:
        
            * source_link_id is the id of a link
            * link is the link with id source_link_id
    """
    
    def __init__(self, links, emergency_routing_enabled, clock_speed, 
            n_available_multicast_entries):
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
        for link in sorted(links, key=lambda x: x.source_link_id):
            if link.source_link_id in self._links:
                raise SpinnMachineAlreadyExistsException(
                        "link", str(link.source_link_id))
            self._links[link.source_link_id] = link
            
        self._emergency_routing_enabled = emergency_routing_enabled
        self._clock_speed = clock_speed
        self._n_available_multicast_entries = n_available_multicast_entries
            
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
