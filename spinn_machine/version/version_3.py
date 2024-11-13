# Copyright (c) 2023 The University of Manchester
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

from typing import Any, Dict, Final, List, Optional, Sequence, Tuple
from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XY
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.full_wrap_machine import FullWrapMachine
from spinn_machine.machine import Machine
from .version_spin1 import VersionSpin1
from .abstract_version import ChipActiveTime, RouterPackets

CHIPS_PER_BOARD: Final = {(0, 0): 18, (0, 1): 18, (1, 0): 18, (1, 1): 18}


class Version3(VersionSpin1):
    """
    Code for the small Spin1 4 Chip boards

    Covers versions 2 and 3
    """
    __slots__ = ()

    #: From measuring the power of an idle 4-chip board for 1 hour, the cost
    #: is 3.56W
    WATTS_FOR_4_CHIP_BOARD_IDLE_COST: Final = 3.56

    @property
    @overrides(VersionSpin1.name)
    def name(self) -> str:
        return "Spin1 4 Chip"

    @property
    @overrides(VersionSpin1.number)
    def number(self) -> int:
        return 3

    @property
    @overrides(VersionSpin1.board_shape)
    def board_shape(self) -> Tuple[int, int]:
        return (2, 2)

    @property
    @overrides(VersionSpin1.chip_core_map)
    def chip_core_map(self) -> Dict[XY, int]:
        return CHIPS_PER_BOARD

    @overrides(VersionSpin1.get_potential_ethernet_chips)
    def get_potential_ethernet_chips(
            self, width: int, height: int) -> Sequence[XY]:
        return [(0, 0)]

    @overrides(VersionSpin1._verify_size)
    def _verify_size(self, width: int, height: int) -> None:
        if width != 2:
            raise SpinnMachineException(f"Unexpected {width=}")
        if height != 2:
            raise SpinnMachineException(f"Unexpected {height=}")

    @overrides(VersionSpin1._create_machine)
    def _create_machine(self, width: int, height: int, origin: str) -> Machine:
        return FullWrapMachine(width, height, CHIPS_PER_BOARD, origin)

    @overrides(VersionSpin1.illegal_ethernet_message)
    def illegal_ethernet_message(self, x: int, y: int) -> Optional[str]:
        if x != 0 or y != 0:
            return "Only Chip 0, 0 may be an Ethernet Chip"
        return None

    @property
    @overrides(VersionSpin1.supports_multiple_boards)
    def supports_multiple_boards(self) -> bool:
        return False

    @overrides(VersionSpin1.spinnaker_links)
    def spinnaker_links(self) -> List[Tuple[int, int, int]]:
        return [(0, 0, 3), (1, 0, 0)]

    @overrides(VersionSpin1.fpga_links)
    def fpga_links(self) -> List[Tuple[int, int, int, int, int]]:
        return []

    @overrides(VersionSpin1.get_idle_energy)
    def get_idle_energy(
            self, time_s: float, n_frames: int, n_boards: int,
            n_chips: int) -> float:
        if n_frames != 0:
            raise SpinnMachineException(
                "A version 3 SpiNNaker 1 board has no frames!")
        if n_boards > 1:
            raise SpinnMachineException(
                "A version 3 SpiNNaker 1 board has exactly one board!")

        # We allow n_boards to be 0 to discount the cost of the board
        if n_boards == 0:
            return n_chips * self.WATTS_PER_IDLE_CHIP * time_s
        return self.WATTS_FOR_4_CHIP_BOARD_IDLE_COST * time_s

    @overrides(VersionSpin1.get_active_energy)
    def get_active_energy(
            self, time_s: float, n_frames: int, n_boards: int, n_chips: int,
            chip_active_time: ChipActiveTime,
            router_packets: RouterPackets) -> float:
        return (
            self.get_idle_energy(time_s, n_frames, n_boards, n_chips) +
            self._get_router_active_energy(router_packets) +
            self._get_core_active_energy(chip_active_time))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Version3)
