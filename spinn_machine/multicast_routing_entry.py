# spimm_machine imports
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException
from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class MulticastRoutingEntry(object):
    """ Represents an entry in a multicast routing table
    """

    __slots__ = (
        "_routing_entry_key", "_mask", "_defaultable", "_processor_ids",
        "_link_ids"
    )

    def __init__(self, routing_entry_key, mask, processor_ids, link_ids,
                 defaultable):
        """

        :param routing_entry_key: The routing key_combo
        :type routing_entry_key: int
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
        self._routing_entry_key = routing_entry_key
        self._mask = mask
        self._defaultable = defaultable

        if (routing_entry_key & mask) != routing_entry_key:
            raise SpinnMachineInvalidParameterException(
                "key_mask_combo and mask",
                "{} and {}".format(routing_entry_key, mask),
                "The key combo is changed when masked with the mask. This"
                " is determined to be an error in the tool chain. Please "
                "correct this and try again.")

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
    def routing_entry_key(self):
        """ The routing key

        :return: The routing key
        :rtype: int
        """
        return self._routing_entry_key

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
            must have the same key and mask.  The merge will join the\
            processor ids and link ids from both the entries.  This could be\
            used to add a new destination to an existing route in a\
            routing table. It is also possible to use the add (+) operator or\
            the or (|) operator with the same effect.

        :param other_entry: The multicast entry to merge with this entry
        :type other_entry: :py:class:`MulticastRoutingEntry`
        :return: A new multicast routing entry with merged destinations
        :rtype: :py:class:`MulticastRoutingEntry`
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:\
                    If the key and mask of the other entry do not match
        """
        if other_entry.routing_entry_key != self.routing_entry_key:
            raise SpinnMachineInvalidParameterException(
                "other_entry.key", hex(other_entry.routing_entry_key),
                "The key does not match {}".format(
                    hex(self.routing_entry_key)))

        if other_entry.mask != self.mask:
            raise SpinnMachineInvalidParameterException(
                "other_entry.mask", hex(other_entry.mask),
                "The mask does not match {}".format(hex(self.mask)))

        defaultable = self._defaultable
        if self._defaultable != other_entry.defaultable:
            defaultable = False

        new_entry = MulticastRoutingEntry(
            self.routing_entry_key, self.mask,
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

    def __eq__(self, other_entry):
        """
        supports comparisons

        :param other_entry: other Multicast_routing_entry
        """
        if not isinstance(other_entry, MulticastRoutingEntry):
            return False
        return (self._defaultable == other_entry.defaultable and
                self._link_ids == other_entry.link_ids and
                self._mask == other_entry.mask and
                self._processor_ids == other_entry.processor_ids and
                self._routing_entry_key == other_entry.routing_entry_key)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "{}:{}:{}:{}:{}".format(
            self._routing_entry_key, self._mask, self._defaultable,
            self._processor_ids, self._link_ids)

    def __str__(self):
        return self.__repr__()

    def __getstate__(self):
        return dict(
            (slot, getattr(self, slot))
            for slot in self.__slots__
            if hasattr(self, slot)
        )

    def __setstate__(self, state):
        for slot, value in state.items():
            setattr(self, slot, value)
