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
from typing import Iterable, Optional, Set, Union
from spinn_machine.constants import MAX_LINKS_PER_ROUTER
from spinn_machine.data import MachineDataView

# cache of MachineDataView.get_machine_version().max_cores_per_chip
max_cores_per_chip: int = 0


class BaseMulticastRoutingEntry(object):
    """
    Represents an entry in a SpiNNaker chip's multicast routing table.
    There can be up to 1024 such entries per chip, but some may be reserved
    for system purposes.
    """

    __slots__ = ["_spinnaker_route"]

    def __init__(self, processor_ids:  Union[int, Iterable[int], None],
                 link_ids:  Union[int, Iterable[int], None],
                 spinnaker_route: Optional[int]):
        """
        .. note::
            The processor_ids and link_ids parameters are only optional if a
            spinnaker_route is provided. If a spinnaker_route is provided
            the processor_ids and link_ids parameters are ignored.

        :param processor_ids: The destination processor IDs
        :type processor_ids: iterable(int) or None
        :param link_ids: The destination link IDs
        :type link_ids: iterable(int) or None
        :param spinnaker_route:
            The processor_ids and link_ids expressed as a single int.
        :type spinnaker_route: int or None
        :raise AssertionError: if no spinnaker_route provided and either
            processor_ids or link_ids is missing or `None`
        """
        global max_cores_per_chip
        if max_cores_per_chip == 0:
            max_cores_per_chip = \
                MachineDataView.get_machine_version().max_cores_per_chip

        # Add processor IDs, ignore duplicates
        if spinnaker_route is None:
            self._spinnaker_route = \
                self._calc_spinnaker_route(processor_ids, link_ids)
        else:
            self._spinnaker_route = spinnaker_route

    @property
    def processor_ids(self) -> Set[int]:
        """
        The destination processor IDs.

        :rtype: set(int)
        """
        return set(pi for pi in range(0, max_cores_per_chip)
                if self._spinnaker_route & 1 << (MAX_LINKS_PER_ROUTER + pi))

    @property
    def link_ids(self) -> Set[int]:
        """
        The destination link IDs.

        :rtype: frozenset(int)
        """
        return set(li for li in range(0, MAX_LINKS_PER_ROUTER)
                   if self._spinnaker_route & 1 << li)

    @property
    def spinnaker_route(self) -> int:
        """
        The encoded SpiNNaker route.

        :rtype: int
        """
        return self._spinnaker_route

    def _calc_spinnaker_route(
            self, processor_ids: Union[int, Iterable[int], None],
            link_ids: Union[int, Iterable[int], None]) -> int:
        """
        create a binary routing table entry usable on the machine.

        :rtype: int
        """
        route = 0
        if processor_ids is None:
            pass
        elif isinstance(processor_ids, int):
            route |= (1 << (MAX_LINKS_PER_ROUTER + processor_ids))
        else:
            for processor_id in processor_ids:
                route |= (1 << (MAX_LINKS_PER_ROUTER + processor_id))
        if link_ids is None:
            pass
        elif isinstance(link_ids, int):
            route |= (1 << link_ids)
        else:
            for link_id in link_ids:
                route |= (1 << link_id)
        return route
