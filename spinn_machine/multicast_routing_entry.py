from spinn_machine.exceptions import SpinnMachineAlreadyExistsException
from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class MulticastRoutingEntry(object):
    """ Represents an entry in a multicast routing table
    """
    
    def __init__(self, key_combo, mask, processor_ids, link_ids, defaultable):
        """
        
        :param key_combo: The routing key_combo
        key_combope key: int
        :param mask: The route key_combo mask
        :type mask: int
        :param processor_ids: The destination processor ids
        :type processor_ids: iterable of int
        :param link_ids: The destination link ids
        :type link_ids: iterable of int
        :param defaultable: if this entry is defaultable (it receives packets \
        from its directly opposite route position)
        :type defaultable: bool
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException:
                    * If processor_ids contains the same id more than once
                    * If link_ids contains the same id more than once
        """
        self._key_combo = key_combo
        self._mask = mask
        self._defaultable = defaultable
        
        # Add processor ids, checking that there is only one of each
        self._processor_ids = set()
        for processor_id in processor_ids:
            if processor_id in self._processor_ids:
                raise SpinnMachineAlreadyExistsException(
                    "processor id", str(processor_id))
            self._processor_ids.add(processor_id)
        
        # Add link ids, checking that there is only one of each
        self._link_ids = set()
        for link_id in link_ids:
            if link_id in self._link_ids:
                raise SpinnMachineAlreadyExistsException(
                    "link id", str(link_id))
            self._link_ids.add(link_id)
    
    @property
    def key_combo(self):
        """ The routing key
        
        :return: The routing key
        :rtype: int
        """
        return self._key_combo
    
    @property
    def mask(self):
        """ The routing mask
        
        :return: The routing mask
        :rtype: int
        """
        return self._mask
    
    @property
    def processor_ids(self):
        """ The destination processor ids
        
        :return: An iterable of processor ids
        :rtype: iterable of int
        """
        return self._processor_ids
    
    @property
    def link_ids(self):
        """ The destination link ids
        
        :return: An iterable of link ids
        :rtype: iterable of int
        """
        return self._link_ids

    @property
    def defaultable(self):
        """if this entry is a defaultable entry
        :return: the bool that represents if a entry is defaultable or not
        :rtype: bool
        """
        return self._defaultable
    
    def merge(self, other_entry):
        """ Merges together two multicast routing entries.  The entry to merge\
            must have the same key and mask.  The merge will join the processor\
            ids and link ids from both the entries.  This could be used to add\
            a new destination to an existing route in a routing table.\
            It is also possible to use the add (+) operator or the or (|)\
            operator with the same effect.
            
        :param other_entry: The multicast entry to merge with this entry
        :type other_entry: :py:class:`MulticastRoutingEntry`
        :return: A new multicast routing entry with merged destinations
        :rtype: :py:class:`MulticastRoutingEntry`
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:\
                    If the key and mask of the other entry do not match
        """
        if other_entry.key_combo != self.key_combo:
            raise SpinnMachineInvalidParameterException(
                "other_entry.key", hex(other_entry.key_combo),
                "The key does not match {}".format(hex(self.key_combo)))
        
        if other_entry.mask != self.mask:
            raise SpinnMachineInvalidParameterException(
                "other_entry.mask", hex(other_entry.mask),
                "The mask does not match {}".format(hex(self.mask)))

        defaultable = self._defaultable
        if self._defaultable != other_entry.defaultable:
            defaultable = False

        new_entry = MulticastRoutingEntry(
            self.key_combo, self.mask,
            self._processor_ids.union(other_entry.processor_ids),
            self._link_ids.union(other_entry.link_ids), defaultable)
        return new_entry
    
    def __add__(self, other_entry):
        """ Allows overloading of + to merge two entries together.\
            See :py:meth:`merge`
        """
        return self.merge(other_entry)
    
    def __or__(self, other_entry):
        """ Allows overloading of | to merge two entries together.\
            See :py:meth:`merge`
        """
        return self.merge(other_entry)
