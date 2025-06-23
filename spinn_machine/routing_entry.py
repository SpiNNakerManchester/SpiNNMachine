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
from typing import (Any, Collection, FrozenSet, Optional, overload, Tuple,
                    Union)
from spinn_machine.router import Router
from .exceptions import (SpinnMachineInvalidParameterException)


class RoutingEntry(object):
    """
    Represents an entry in a SpiNNaker chip's multicast routing table.
    """

    __slots__ = (
        "_defaultable", "_processor_ids",
        "_link_ids", "_spinnaker_route", "__repr")

    @overload
    def __init__(self, *, processor_ids: Union[int, Collection[int]],
                 link_ids: Union[int, Collection[int]],
                 incoming_processor: Optional[int] = None,
                 incoming_link: Optional[int] = None,
                 defaultable: None = None,
                 spinnaker_route: None = None):
        ...

    @overload
    def __init__(self, *, processor_ids: None = None,
                 link_ids: None = None,
                 incoming_processor: None = None,
                 incoming_link: None = None,
                 defaultable: Optional[bool] = False,
                 spinnaker_route: int):
        ...

    def __init__(self, *,
                 processor_ids: Optional[Union[int, Collection[int]]] = None,
                 link_ids: Optional[Union[int, Collection[int]]] = None,
                 incoming_processor: Optional[int] = None,
                 incoming_link: Optional[int] = None,
                 defaultable: Optional[bool] = None,
                 spinnaker_route: Optional[int] = None) -> None:
        """
        .. note::
            The processor_ids and link_ids parameters are only optional if a
            spinnaker_route is provided. If a spinnaker_route is provided
            the processor_ids and link_ids parameters are ignored.

        :param processor_ids: The destination processor IDs
        :param link_ids: The destination link IDs
        :param defaultable:
            If this entry is defaultable (it receives packets
            from its directly opposite route position)
        :param spinnaker_route:
            The processor_ids and link_ids expressed as a single int.
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException:
            * If processor_ids contains the same ID more than once
            * If link_ids contains the same ID more than once
        :raise TypeError: if no spinnaker_route provided and either
            processor_ids or link_ids is missing or `None`
        """
        self.__repr: Optional[str] = None
        self._link_ids: Optional[FrozenSet[int]]
        self._processor_ids: Optional[FrozenSet[int]]

        # Add processor IDs, ignore duplicates
        if spinnaker_route is None:
            assert processor_ids is not None
            assert link_ids is not None
            assert defaultable is None
            if isinstance(processor_ids, int):
                processor_ids = [processor_ids]
            if isinstance(link_ids, int):
                link_ids = [link_ids]
            self._processor_ids = frozenset(processor_ids)
            self._link_ids = frozenset(link_ids)
            self._spinnaker_route: int = self._calc_spinnaker_route()
            if incoming_link is None:
                self._defaultable = False
            else:
                if incoming_processor is None:
                    if len(link_ids) != 1:
                        self._defaultable = False
                    else:
                        link_id = next(iter(link_ids))
                        self._defaultable = (
                                ((incoming_link + 3) % 6) == link_id)
                else:
                    raise SpinnMachineInvalidParameterException(
                        "incoming_processor", incoming_processor,
                        "The incoming direction for a path can only be from "
                        "either one link or one processors, not both")
        else:
            assert processor_ids is None
            assert link_ids is None
            assert incoming_link is None
            assert incoming_processor is None
            self._spinnaker_route = spinnaker_route
            self._processor_ids = None
            self._link_ids = None
            if defaultable:
                self._defaultable = True
            else:
                self._defaultable = False

    @property
    def processor_ids(self) -> FrozenSet[int]:
        """
        The destination processor IDs.
        """
        if self._processor_ids is None:
            self._processor_ids, self._link_ids = self._calc_routing_ids()
        return self._processor_ids

    @property
    def link_ids(self) -> FrozenSet[int]:
        """
        The destination link IDs.
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
        """
        return self._defaultable

    @property
    def spinnaker_route(self) -> int:
        """
        The encoded SpiNNaker route.
        """
        return self._spinnaker_route

    def merge(self, other: RoutingEntry) -> RoutingEntry:
        """
        Merges together two routing entries. The merge will join the
        processor IDs and link IDs from both the entries.  This could be
        used to add a new destination to an existing route in a
        routing table. It is also possible to use the add (`+`) operator
        or the or (`|`) operator with the same effect.

        :param other:
            The multicast entry to merge with this entry
        :return: A new multicast routing entry with merged destinations
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:
            If the key and mask of the other entry do not match
        """
        # 2 different merged routes can NEVER be defaultable
        if self == other:
            return self
        return RoutingEntry(
            spinnaker_route=self.spinnaker_route | other.spinnaker_route,
            defaultable=False)

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
            if self._defaultable:
                self.__repr += "(defaultable)"
        return self.__repr

    def __str__(self) -> str:
        return self.__repr__()

    def _calc_spinnaker_route(self) -> int:
        """
        Convert a routing table entry represented in software to a
        binary routing table entry usable on the machine.
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
        """
        processor_ids = (pi for pi in range(0, Router.MAX_CORES_PER_ROUTER)
                         if self._spinnaker_route & 1 <<
                         (Router.MAX_LINKS_PER_ROUTER + pi))
        link_ids = (li for li in range(0, Router.MAX_LINKS_PER_ROUTER)
                    if self._spinnaker_route & 1 << li)
        return frozenset(processor_ids), frozenset(link_ids)
