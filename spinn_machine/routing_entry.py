# Copyright (c) 2024 The University of Manchester
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
from spinn_machine.router import Router
from .exceptions import SpinnMachineAlreadyExistsException


class RoutingEntry(object):
    """
    Represents an entry in a SpiNNaker chip's multicast routing table.
    """

    __slots__ = (
        "_defaultable", "_processor_ids",
        "_link_ids", "_spinnaker_route", "__repr")

    @overload
    def __init__(self, *, processor_ids: Iterable[int],
                 link_ids: Iterable[int],
                 defaultable: bool = False,
                 spinnaker_route: None = None):
        ...

    @overload
    def __init__(self, int, *, processor_ids: None = None,
                 link_ids: None = None,
                 defaultable: bool = False,
                 spinnaker_route: int):
        ...

    # pylint: disable=too-many-arguments
    def __init__(self, *, processor_ids: Optional[Iterable[int]] = None,
                 link_ids: Optional[Iterable[int]] = None,
                 defaultable: bool = False,
                 spinnaker_route: Optional[int] = None) -> None:
        """
        .. note::
            The processor_ids and link_ids parameters are only optional if a
            spinnaker_route is provided. If a spinnaker_route is provided
            the processor_ids and link_ids parameters are ignored.

        :param processor_ids: The destination processor IDs
        :type processor_ids: iterable(int) or None
        :param link_ids: The destination link IDs
        :type link_ids: iterable(int) or None
        :param bool defaultable:
            If this entry is defaultable (it receives packets
            from its directly opposite route position)
        :param spinnaker_route:
            The processor_ids and link_ids expressed as a single int.
        :type spinnaker_route: int or None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException:
            * If processor_ids contains the same ID more than once
            * If link_ids contains the same ID more than once
        :raise TypeError: if no spinnaker_route provided and either
            processor_ids or link_ids is missing or `None`
        """
        self._defaultable: bool = defaultable
        self.__repr: Optional[str] = None

        # Add processor IDs, ignore duplicates
        if spinnaker_route is None:
            assert processor_ids is not None
            assert link_ids is not None
            self._processor_ids: Optional[FrozenSet[int]] = \
                frozenset(processor_ids)
            self._link_ids: Optional[FrozenSet[int]] = frozenset(link_ids)
            self._spinnaker_route: int = self._calc_spinnaker_route()
        else:
            self._spinnaker_route = spinnaker_route
            self._processor_ids = None
            self._link_ids = None

    # TODO from FixedRouteEntry use or loose
    @staticmethod
    def __check_dupes(sequence: Iterable[int], name: str):
        check = set()
        for _id in sequence:
            if _id in check:
                raise SpinnMachineAlreadyExistsException(name, str(_id))
            check.add(_id)

    @property
    def processor_ids(self) -> FrozenSet[int]:
        """
        The destination processor IDs.

        :rtype: frozenset(int)
        """
        if self._processor_ids is None:
            self._processor_ids, self._link_ids = self._calc_routing_ids()
        return self._processor_ids

    @property
    def link_ids(self) -> FrozenSet[int]:
        """
        The destination link IDs.

        :rtype: frozenset(int)
        """
        if self._link_ids is None:
            self._processor_ids, self._link_ids = self._calc_routing_ids()
        return self._link_ids

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
        return self._defaultable

    @property
    def spinnaker_route(self) -> int:
        """
        The encoded SpiNNaker route.

        :rtype: int
        """
        return self._spinnaker_route

    def merge(self, other: RoutingEntry) -> RoutingEntry:
        """
        Merges together two routing entries. The merge will join the
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
        # 2 different merged routes can NEVER be defaultable
        return RoutingEntry(
            spinnaker_route=self.spinnaker_route | other.spinnaker_route,
            defaultable=self.defaultable and other.defaultable)

    def __eq__(self, other_entry: Any) -> bool:
        if not isinstance(other_entry, RoutingEntry):
            return False
        if self._spinnaker_route != other_entry._spinnaker_route:
            return False
        return (self._defaultable == other_entry.defaultable)

    def __hash__(self) -> int:
        return self._spinnaker_route * 29 * int(self._defaultable) * 131

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        if not self.__repr:
            self.__repr = (
                f"{{{', '.join(map(str, sorted(self.processor_ids)))}}}:"
                f"{{{', '.join(map(str, sorted(self.link_ids)))}}}")
        return self.__repr

    def __str__(self) -> str:
        return self.__repr__()

    def _calc_spinnaker_route(self) -> int:
        """
        Convert a routing table entry represented in software to a
        binary routing table entry usable on the machine.

        :rtype: int
        """
        route_entry = 0
        assert self._processor_ids is not None
        for processor_id in self._processor_ids:
            route_entry |= (1 << (Router.MAX_LINKS_PER_ROUTER + processor_id))
        assert self._link_ids is not None
        for link_id in self._link_ids:
            route_entry |= (1 << link_id)
        return route_entry

    def _calc_routing_ids(self) -> Tuple[FrozenSet[int], FrozenSet[int]]:
        """
        Convert a binary routing table entry usable on the machine to lists of
        route IDs usable in a routing table entry represented in software.

        :rtype: tuple(frozenset(int), frozenset(int))
        """
        processor_ids = (pi for pi in range(0, Router.MAX_CORES_PER_ROUTER)
                         if self._spinnaker_route & 1 <<
                         (Router.MAX_LINKS_PER_ROUTER + pi))
        link_ids = (li for li in range(0, Router.MAX_LINKS_PER_ROUTER)
                    if self._spinnaker_route & 1 << li)
        return frozenset(processor_ids), frozenset(link_ids)
