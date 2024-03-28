# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations
from typing import Any, FrozenSet, Iterable, Optional, Tuple, overload
from .exceptions import SpinnMachineInvalidParameterException
from .routing_entry import RoutingEntry


class MulticastRoutingEntry(object):
    """
    Represents an entry in a SpiNNaker chip's routing table,
    including the key and mask
    """

    __slots__ = (
        "_routing_entry_key", "_mask", "_routing_entry")

    def __init__(self, routing_entry_key: int, mask: int,
                 routing_entry: RoutingEntry):
        """
        :param int routing_entry_key: The routing key_combo
        :param int mask: The route key_combo mask
        :param RoutingEntry: routing_entry
        """
        self._routing_entry_key: int = routing_entry_key
        self._mask: int = mask
        self._routing_entry = routing_entry

        if (routing_entry_key & mask) != routing_entry_key:
            raise SpinnMachineInvalidParameterException(
                "key_mask_combo and mask",
                f"{routing_entry_key} and {mask}",
                "The key combo is changed when masked with the mask. This"
                " is determined to be an error in the tool chain. Please "
                "correct this and try again.")

    @property
    def routing_entry_key(self) -> int:
        """
        The routing key.

        :rtype: int
        """
        return self._routing_entry_key

    @property
    def mask(self) -> int:
        """
        The routing mask.

        :rtype: int
        """
        return self._mask

    @property
    def defaultable(self) -> bool:
        """
        Whether this entry is a defaultable entry. An entry is defaultable if
        it is duplicating the default behaviour of the SpiNNaker router (to
        pass a message out on the link opposite from where it was received,
        without routing it to any processors; source and destination chips for
        a message cannot be defaultable).

        :rtype: bool
        """
        return self._routing_entry.defaultable

    @property
    def spinnaker_route(self) -> int:
        """
        The encoded SpiNNaker route.

        :rtype: int
        """
        return self._routing_entry.spinnaker_route

    @property
    def entry(self) -> RoutingEntry:
        return self._routing_entry

    def merge(self, other: MulticastRoutingEntry) -> MulticastRoutingEntry:
        """
        Merges together two multicast routing entries.  The entry to merge
        must have the same key and mask.  The merge will join the
        processor IDs and link IDs from both the entries.  This could be
        used to add a new destination to an existing route in a
        routing table. It is also possible to use the add (`+`) operator
        or the or (`|`) operator with the same effect.

        :param ~spinn_machine.MulticastRoutingEntry other:
            The multicast entry to merge with this entry
        :return: A new multicast routing entry with merged destinations
        :rtype: ~spinn_machine.MulticastRoutingEntry
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:
            If the key and mask of the other entry do not match
        """
        if other.routing_entry_key != self.routing_entry_key:
            raise SpinnMachineInvalidParameterException(
                "other.key", hex(other.routing_entry_key),
                f"The key does not match 0x{self.routing_entry_key:x}")
        if other.mask != self.mask:
            raise SpinnMachineInvalidParameterException(
                "other.mask", hex(other.mask),
                f"The mask does not match 0x{self.mask:x}")

        entry = self.entry.merge(other.entry)
        return MulticastRoutingEntry(
            self.routing_entry_key, self.mask, entry)

    def __eq__(self, other_entry: Any) -> bool:
        if not isinstance(other_entry, MulticastRoutingEntry):
            return False
        if self.routing_entry_key != other_entry.routing_entry_key:
            return False
        if self.mask != other_entry.mask:
            return False
        return (self.entry == other_entry.entry)

    def __hash__(self) -> int:
        return (self.routing_entry_key * 13 + self.mask * 19 +
                hash(self._routing_entry))

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return (f"{self._routing_entry_key}:{self._mask}:" 
                f"{repr(self._routing_entry)}")

    def __str__(self) -> str:
        return self.__repr__()
