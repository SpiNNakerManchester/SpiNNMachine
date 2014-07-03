class MulticastRoutingEntry(object):
    """ Represents an entry in a multicast routing table
    """
    
    def __init__(self, key, mask, processor_ids, link_ids):
        """
        
        :param key: The routing key
        :type key: int
        :param mask: The route key mask
        :type mask: int
        :param processor_ids: The destination processor ids
        :type processor_ids: iterable of int
        :param link_ids: The destination link ids
        :type link_ids: iterable of int
        :raise None: No known exceptions are raised
        """
        pass
    
    @property
    def key(self):
        """ The routing key
        
        :return: The routing key
        :rtype: int
        """
        pass
    
    @property
    def mask(self):
        """ The routing mask
        
        :return: The routing mask
        :rtype: int
        """
        pass
    
    @property
    def processor_ids(self):
        """ The destination processor ids
        
        :return: An iterable of processor ids
        :rtype: iterable of int
        """
        pass
    
    @property
    def link_ids(self):
        """ The destination link ids
        
        :return: An iterable of link ids
        :rtype: iterable of int
        """
        pass
    
    def merge(self, other_entry):
        """ Merges together two multicast routing entries.  The entry to merge\
            must have the same key and mask.  The merge will join the processor\
            ids and link ids from both the entries.  This could be used to add\
            a new destination to an existing route in a routing table.
            
        :param other_entry: The multicast entry to merge with this entry
        :type other_entry: :py:class:`MulticastRoutingEntry`
        :return: A new multicast routing entry with merged destinations
        :rtype: :py:class:`MulticastRoutingEntry`
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:\
                    If the key and mask of the other entry do not match
        """
        pass
