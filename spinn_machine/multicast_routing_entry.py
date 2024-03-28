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
from typing import Any, FrozenSet
from .exceptions import SpinnMachineInvalidParameterException
from .routing_entry import RoutingEntry


class MulticastRoutingEntry(object):
    """
    Represents an entry in a SpiNNaker chip's routing table,
    including the key and mask
    """

    __slots__ = (
        "_key", "_mask", "_routing_entry")

    def __init__(self, key: int, mask: int,
                 routing_entry: RoutingEntry):
        """
        :param int key: The routing key_combo
        :param int mask: The route key_combo mask
        :param RoutingEntry: routing_entry
        """
        self._key: int = key
        self._mask: int = mask
        self._routing_entry = routing_entry

        if (key & mask) != key:
            raise SpinnMachineInvalidParameterException(
                "key_mask_combo and mask",
                f"{key} and {mask}",
                "The key combo is changed when masked with the mask. This"
                " is determined to be an error in the tool chain. Please "
                "correct this and try again.")

    @property
    def key(self) -> int:
        """
        The routing key.

        :rtype: int
        """
        return self._key

    @property
    def mask(self) -> int:
        """
        The routing mask.

        :rtype: int
        """
        return self._mask

    @property
    def processor_ids(self) -> FrozenSet[int]:
        """
        The destination processor IDs.

        :rtype: frozenset(int)
        """
        return self._routing_entry.processor_ids

    @property
    def link_ids(self) -> FrozenSet[int]:
        """
        The destination link IDs.

        :rtype: frozenset(int)
        """
        return self._routing_entry.link_ids

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
        if other.key != self.key:
            raise SpinnMachineInvalidParameterException(
                "other.key", hex(other.key),
                f"The key does not match 0x{self.key:x}")
        if other.mask != self.mask:
            raise SpinnMachineInvalidParameterException(
                "other.mask", hex(other.mask),
                f"The mask does not match 0x{self.mask:x}")

        routing_entry = self._routing_entry.merge(other._routing_entry)
        return MulticastRoutingEntry(
            self.key, self.mask, routing_entry)

    def __eq__(self, other_entry: Any) -> bool:
        if not isinstance(other_entry, MulticastRoutingEntry):
            return False
        if self.key != other_entry.key:
            return False
        if self.mask != other_entry.mask:
            return False
        return (self._routing_entry == other_entry._routing_entry)

    def __hash__(self) -> int:
        return (self.key * 13 + self.mask * 19 +
                hash(self._routing_entry))

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return (f"{self._key}:{self._mask}:"
                f"{repr(self._routing_entry)}")

    def __str__(self) -> str:
        return self.__repr__()
