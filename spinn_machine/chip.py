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
from typing import (
    Any, Collection, Dict, Iterable, Iterator, Optional, Tuple)
from spinn_utilities.ordered_set import OrderedSet
from spinn_machine.data import MachineDataView
from .processor import Processor
from .router import Router

# global values so Chip objects can share processor dict objects
# One dict for each number of processors (none dead)
standard_processors = {}
# One dict for the standard monitor processors
standard_monitor_processors = None  # pylint: disable=invalid-name


class Chip(object):
    """
    Represents a SpiNNaker chip with a number of cores, an amount of
    SDRAM shared between the cores, and a router.
    The chip is iterable over the processors, yielding
    ``(processor_id, processor)`` where:

        * ``processor_id`` is the ID of a processor
        * ``processor`` is the :py:class:`Processor` with ``processor_id``
    """

    # tag 0 is reserved for stuff like IO STD
    _IPTAG_IDS = OrderedSet(range(1, 8))

    __slots__ = (
        "_x", "_y", "_router", "_sdram", "_ip_address",
        "_tag_ids", "_nearest_ethernet_x", "_nearest_ethernet_y",
        "_user_processors", "_monitor_processors", "_parent_link",
        "_v_to_p_map"
    )

    # pylint: disable=too-many-arguments, wrong-spelling-in-docstring
    def __init__(self, x: int, y: int, n_processors: int, router: Router,
                 sdram: int, nearest_ethernet_x: int, nearest_ethernet_y: int,
                 ip_address: Optional[str] = None,
                 tag_ids: Optional[Iterable[int]] = None,
                 down_cores: Optional[Collection[int]] = None,
                 parent_link: Optional[int] = None,
                 v_to_p_map: Optional[bytes] = None):
        """
        :param int x: the x-coordinate of the chip's position in the
            two-dimensional grid of chips
        :param int y: the y-coordinate of the chip's position in the
            two-dimensional grid of chips
        :param int n_processors:
            the number of processors including monitor processors.
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
        :param down_cores: Ids of cores that are down for this Chip
        :type down_cores: iterable(int) or None
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
        self._x = x
        self._y = y
        self._monitor_processors = self.__generate_monitors()
        self._user_processors = self.__generate_processors(
            n_processors, down_cores)
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
        self._v_to_p_map = v_to_p_map

    def __generate_monitors(self):
        """
        Generates the monitors assuming all Chips have the same monitor cores

        :return:  Dict[int, Processor]
        """
        global standard_monitor_processors  # pylint: disable=global-statement
        if standard_monitor_processors is None:
            standard_monitor_processors = dict()
            for i in range(
                    MachineDataView.get_machine_version().n_non_user_cores):
                standard_monitor_processors[i] = Processor.factory(i, True)
        return standard_monitor_processors

    def __generate_processors(
            self, n_processors: int,
            down_cores: Optional[Collection[int]]) -> Dict[int, Processor]:
        n_monitors = MachineDataView.get_machine_version().n_non_user_cores
        if down_cores is None:
            if n_processors not in standard_processors:
                processors = dict()
                for i in range(n_monitors, n_processors):
                    processors[i] = Processor.factory(i)
                standard_processors[n_processors] = processors
            return standard_processors[n_processors]
        else:
            processors = dict()
            for i in range(n_monitors):
                if i in down_cores:
                    raise NotImplementedError(
                        f"Declaring monitor core {i} as down is not supported")
            for i in range(n_monitors, n_processors):
                if i not in down_cores:
                    processors[i] = Processor.factory(i)
            return processors

    def is_processor_with_id(self, processor_id: int) -> bool:
        """
        Determines if a processor with the given ID exists in the chip.
        Also implemented as ``__contains__(processor_id)``

        :param int processor_id: the processor ID to check for
        :return: Whether the processor with the given ID exists
        :rtype: bool
        """
        if processor_id in self._user_processors:
            return True
        return processor_id in self._monitor_processors

    def get_processor_with_id(self, processor_id: int) -> Optional[Processor]:
        """
        Return the processor with the specified ID, or ``None`` if the
        processor does not exist.

        :param int processor_id: the ID of the processor to return
        :return:
            the processor with the specified ID,
            or ``None`` if no such processor
        :rtype: Processor or None
        """
        if processor_id in self._user_processors:
            return self._user_processors[processor_id]
        return self._monitor_processors.get(processor_id)

    @property
    def x(self) -> int:
        """
        The X-coordinate of the chip in the two-dimensional grid of chips.

        :rtype: int
        """
        return self._x

    @property
    def y(self) -> int:
        """
        The Y-coordinate of the chip in the two-dimensional grid of chips.

        :rtype: int
        """
        return self._y

    @property
    def processors(self) -> Iterator[Processor]:
        """
        An iterable of available all processors.

        Deprecated: There are many more efficient methods instead.
        - all_processor_ids
        - n_processors
        - n_user_processors
        - user_processors
        - user_processors_ids
        - n_monitor_processors
        - monitor_processors
        - monitor_processors_ids

        :rtype: iterable(Processor)
        """
        yield from self._monitor_processors.values()
        yield from self._user_processors.values()

    @property
    def all_processor_ids(self) -> Iterator[int]:
        """
        An iterable of id's of all available processors

        :rtype: iterable(int)
        """
        yield from self._monitor_processors.keys()
        yield from self._user_processors.keys()

    @property
    def n_processors(self) -> int:
        """
        The total number of processors.

        :rtype: int
        """
        return len(self._monitor_processors) + len(self._user_processors)

    @property
    def user_processors(self) -> Iterator[Processor]:
        """
        An iterable of available user processors.

        :rtype: iterable(Processor)
        """
        yield from self._user_processors.values()

    @property
    def user_processors_ids(self) -> Iterator[int]:
        """
        An iterable of available user processors.

        :rtype: iterable(Processor)
        """
        yield from self._user_processors

    @property
    def n_user_processors(self) -> int:
        """
        The total number of processors that are not monitors.

        :rtype: int
        """
        return len(self._user_processors)

    @property
    def monitor_processors(self) -> Iterator[Processor]:
        """
        An iterable of available monitor processors.

        :rtype: iterable(Processor)
        """
        return self._monitor_processors.values()

    @property
    def monitor_processors_ids(self) -> Iterator[int]:
        """
        An iterable of available user processors.

        :rtype: iterable(Processor)
        """
        yield from self._monitor_processors

    @property
    def n_monitor_processors(self) -> int:
        """
        The total number of processors that are not monitors.

        :rtype: int
        """
        return len(self._monitor_processors)

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
    def tag_ids(self) -> Iterable[int]:
        """
        The tag IDs supported by this chip.

        :rtype: iterable(int)
        """
        return self._tag_ids

    def get_first_none_monitor_processor(self) -> Processor:
        """
        Get the first processor in the list which is not a monitor core.

        :rtype: Processor
        ;raises StopIteration: If there is no user processor
        """
        return next(iter(self._user_processors.values()))

    @property
    def parent_link(self) -> Optional[int]:
        """
        The link down which the parent is found in the tree of chips rooted
        at the machine root chip (probably 0, 0 in most cases).  This will
        be ``None`` if the chip information didn't contain this value.

        :rtype: int or None
        """
        return self._parent_link

    def get_physical_core_id(self, virtual_p: int) -> Optional[int]:
        """
        Get the physical core ID from a virtual core ID.

        :param int virtual_p: The virtual core ID
        :rtype: int or None if core not in map
        """
        if (self._v_to_p_map is None or virtual_p >= len(self._v_to_p_map) or
                self._v_to_p_map[virtual_p] == 0xFF):
            return None
        return self._v_to_p_map[virtual_p]

    def get_physical_core_string(self, virtual_p: int) -> str:
        """
        Get a string that can be appended to a core to show the physical
        core, or an empty string if not possible.

        :param int virtual_p: The virtual core ID
        :rtype: str
        """
        physical_p = self.get_physical_core_id(virtual_p)
        if physical_p is None:
            return ""
        return f" (ph: {physical_p})"

    def __iter__(self) -> Iterator[Tuple[int, Processor]]:
        """
        Get an iterable of processor identifiers and processors

        :return: An iterable of ``(processor_id, processor)`` where:
            * ``processor_id`` is the ID of a processor
            * ``processor`` is the processor with the ID
        :rtype: iterable(tuple(int,Processor))
        """
        yield from self._monitor_processors.items()
        yield from self._user_processors.items()

    def __len__(self) -> int:
        """
        The number of processors associated with this chip.

        :return: The number of items in the underlying iterator.
        :rtype: int
        """
        return len(self._monitor_processors) + len(self._user_processors)

    def __getitem__(self, processor_id: int) -> Processor:
        if processor_id in self._user_processors:
            return self._user_processors[processor_id]
        if processor_id in self._monitor_processors:
            return self._monitor_processors[processor_id]
        # Note difference from get_processor_with_id(); this is to conform to
        # standard Python semantics
        raise KeyError(processor_id)

    def __contains__(self, processor_id: int) -> bool:
        return self.is_processor_with_id(processor_id)

    def __str__(self) -> str:
        if self._ip_address:
            ip_info = f"ip_address={self.ip_address} "
        else:
            ip_info = ""
        return (
            f"[Chip: x={self._x}, y={self._y}, {ip_info}"
            f"n_cores={self.n_processors}, "
            f"mon={self.get_physical_core_id(0)}]")

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Any) -> bool:
        # Equality just on X,Y; that's most useful
        if not isinstance(other, Chip):
            return NotImplemented
        return self._x == other.x and self._y == other.y

    def __hash__(self) -> int:
        return self._x * 256 + self._y
