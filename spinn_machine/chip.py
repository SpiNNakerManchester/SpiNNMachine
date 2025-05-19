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
from typing import (Iterable, Iterator, Optional, Tuple)

from typing_extensions import Self

from spinn_utilities.ordered_set import OrderedSet
from spinn_utilities.typing.coords import XY

from .router import Router


class Chip(XY):
    """
    Represents a SpiNNaker chip with a number of cores, an amount of
    SDRAM shared between the cores, and a router.
    """

    # tag 0 is reserved for stuff like IO STD
    _IPTAG_IDS = OrderedSet(range(1, 8))

    def __new__(cls, x: int, y: int, scamp_processors: Iterable[int],
                placable_processors: Iterable[int], router: Router,
                sdram: int, nearest_ethernet_x: int, nearest_ethernet_y: int,
                ip_address: Optional[str] = None,
                tag_ids: Optional[Iterable[int]] = None,
                parent_link: Optional[int] = None) -> Self:
        return tuple.__new__(cls, (x, y))

    def __init__(self, x: int, y: int, scamp_processors: Iterable[int],
                 placable_processors: Iterable[int], router: Router,
                 sdram: int, nearest_ethernet_x: int, nearest_ethernet_y: int,
                 ip_address: Optional[str] = None,
                 tag_ids: Optional[Iterable[int]] = None,
                 parent_link: Optional[int] = None):
        """
        :param int x: the x-coordinate of the chip's position in the
            two-dimensional grid of chips
        :param int y: the y-coordinate of the chip's position in the
            two-dimensional grid of chips
        :param iterable(int) scamp_processors:
            the ids of scamp processors
        :param iterable(int) placable_processors:
            the ids of processors excluding scamp processors.
        :param ~spinn_machine.Router router: a router for the chip
        :param int sdram: an SDRAM for the chip
        :param ip_address:
            the IP address of the chip, or ``None`` if no Ethernet attached
        :type ip_address: str or None
        :param tag_ids: IDs to identify the chip for SDP can be empty to
            define no tags or `None` to allocate tag automatically
            based on if there is an ip_address
        :type tag_ids: iterable(int) or None
        :param nearest_ethernet_x: the nearest Ethernet x coordinate
        :type nearest_ethernet_x: int or None
        :param nearest_ethernet_y: the nearest Ethernet y coordinate
        :type nearest_ethernet_y: int or None
        :param parent_link: The link down which the parent chips is found in
            the tree of chips towards the root (boot) chip
        :type parent_link: int or None
        :param v_to_p_map: An array indexed by virtual core which gives the
            physical core number or 0xFF if no entry for the core
        :type v_to_p_map: bytearray or None
        :raise ~spinn_machine.exceptions.SpinnMachineAlreadyExistsException:
            If processors contains any two processors with the same
            ``processor_id``
        """
        # X and Y set by new
        _, _ = x, y
        self._scamp_processors = tuple(scamp_processors)
        self._placable_processors = tuple(placable_processors)
        self._router = router
        self._sdram = sdram
        self._ip_address = ip_address
        if tag_ids is not None:
            self._tag_ids = OrderedSet(tag_ids)
        elif self._ip_address is None:
            self._tag_ids = OrderedSet()
        else:
            self._tag_ids = self._IPTAG_IDS
        self._nearest_ethernet_x = nearest_ethernet_x
        self._nearest_ethernet_y = nearest_ethernet_y
        self._parent_link = parent_link

    def is_processor_with_id(self, processor_id: int) -> bool:
        """
        Determines if a processor with the given ID exists in the chip.
        Also implemented as ``__contains__(processor_id)``

        :param int processor_id: the processor ID to check for
        :return: Whether the processor with the given ID exists
        :rtype: bool
        """
        if processor_id in self._placable_processors:
            return True
        return processor_id in self._scamp_processors

    @property
    def x(self) -> int:
        """
        The X-coordinate of the chip in the two-dimensional grid of chips.

        :rtype: int
        """
        return self[0]

    @property
    def y(self) -> int:
        """
        The Y-coordinate of the chip in the two-dimensional grid of chips.

        :rtype: int
        """
        return self[1]

    @property
    def all_processor_ids(self) -> Iterator[int]:
        """
        An iterable of id's of all available processors

        :rtype: iterable(int)
        """
        yield from self._scamp_processors
        yield from self._placable_processors

    @property
    def n_processors(self) -> int:
        """
        The total number of processors.

        :rtype: int
        """
        return len(self._scamp_processors) + len(self._placable_processors)

    @property
    def placable_processors_ids(self) -> Tuple[int, ...]:
        """
        An iterable of available placable/ non scamp processor ids.

        :rtype: iterable(int)
        """
        return self._placable_processors

    @property
    def n_placable_processors(self) -> int:
        """
        The total number of processors that are placable / not used by scamp.

        :rtype: int
        """
        return len(self._placable_processors)

    @property
    def scamp_processors_ids(self) -> Tuple[int, ...]:
        """
        An iterable of available scamp processors.

        :rtype: iterable(int)
        """
        return self._scamp_processors

    @property
    def n_scamp_processors(self) -> int:
        """
        The total number of processors that are used by scamp.

        :rtype: int
        """
        return len(self._scamp_processors)

    @property
    def router(self) -> Router:
        """
        The router object associated with the chip.

        :rtype: Router
        """
        return self._router

    @property
    def sdram(self) -> int:
        """
        The SDRAM associated with the chip.

        :rtype: int
        """
        return self._sdram

    @property
    def ip_address(self) -> Optional[str]:
        """
        The IP address of the chip, or ``None`` if there is no Ethernet
        connected to the chip.

        :rtype: str or None
        """
        return self._ip_address

    @property
    def nearest_ethernet_x(self) -> int:
        """
        The X-coordinate of the nearest Ethernet chip.

        :rtype: int
        """
        return self._nearest_ethernet_x

    @property
    def nearest_ethernet_y(self) -> int:
        """
        The Y-coordinate of the nearest Ethernet chip.

        :rtype: int
        """
        return self._nearest_ethernet_y

    @property
    def tag_ids(self) -> OrderedSet[int]:
        """
        The tag IDs supported by this chip.

        :rtype: iterable(int)
        """
        return self._tag_ids

    @property
    def parent_link(self) -> Optional[int]:
        """
        The link down which the parent is found in the tree of chips rooted
        at the machine root chip (probably 0, 0 in most cases).  This will
        be ``None`` if the chip information didn't contain this value.

        :rtype: int or None
        """
        return self._parent_link

    def __str__(self) -> str:
        if self._ip_address:
            ip_info = f"ip_address={self.ip_address} "
        else:
            ip_info = ""
        return (
            f"[Chip: x={self[0]}, y={self[1]}, {ip_info}"
            f"n_cores={self.n_processors}]")

    def __repr__(self) -> str:
        return self.__str__()
