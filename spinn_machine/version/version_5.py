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

from typing import Any, Dict, Final, List, Tuple
from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XY

from .version_48_chips import Version48Chips
from .version_spin1 import VersionSpin1
from .abstract_version import ChipActiveTime, RouterPackets

CHIPS_PER_BOARD: Final = {
    (0, 0): 18, (0, 1): 18, (0, 2): 18, (0, 3): 18, (1, 0): 18, (1, 1): 17,
    (1, 2): 18, (1, 3): 17, (1, 4): 18, (2, 0): 18, (2, 1): 18, (2, 2): 18,
    (2, 3): 18, (2, 4): 18, (2, 5): 18, (3, 0): 18, (3, 1): 17, (3, 2): 18,
    (3, 3): 17, (3, 4): 18, (3, 5): 17, (3, 6): 18, (4, 0): 18, (4, 1): 18,
    (4, 2): 18, (4, 3): 18, (4, 4): 18, (4, 5): 18, (4, 6): 18, (4, 7): 18,
    (5, 1): 18, (5, 2): 17, (5, 3): 18, (5, 4): 17, (5, 5): 18, (5, 6): 17,
    (5, 7): 18, (6, 2): 18, (6, 3): 18, (6, 4): 18, (6, 5): 18, (6, 6): 18,
    (6, 7): 18, (7, 3): 18, (7, 4): 18, (7, 5): 18, (7, 6): 18, (7, 7): 18
}


class Version5(VersionSpin1, Version48Chips):
    """
    Code for the large Spin1 48 Chip boards

    Covers versions 4 and 5
    """
    __slots__ = ()

    #: measured from the real power meter and timing between
    #: the photos for a days powered off
    #: this is the cost of just a frame itself, including the switch and
    #: cooling, while the system is idle.
    WATTS_FOR_FRAME_IDLE_COST: Final = 117

    #: measured from the loading of the column and extrapolated
    #: this is the cost of just a frame itself, including the switch and
    #: cooling, while the system is active, over the idle cost for simplicity
    WATTS_PER_FRAME_ACTIVE_COST_OVERHEAD: Final = 154.163558 - 117

    # pylint: disable=invalid-name
    #: from Optimising the overall power usage on the SpiNNaker neuromimetic
    #: platform, an idle board uses 26.84W and from measurement of a boxed
    #: board with all cores idle for 1 hour including the power supply and all
    #: parts, uses 31.88W, so the overhead is 5.04W
    WATTS_FOR_48_CHIP_BOX_COST_OVERHEAD: Final = 5.04

    # pylint: disable=invalid-name
    #: from Optimising the overall power usage on the SpiNNaker neuromimetic
    #: platform, an idle board uses 26.84W
    WATTS_FOR_48_CHIP_BOARD_IDLE_COST: Final = 26.84

    @property
    @overrides(VersionSpin1.name)
    def name(self) -> str:
        return "Spin1 48 Chip"

    @property
    @overrides(VersionSpin1.number)
    def number(self) -> int:
        return 5

    @property
    @overrides(VersionSpin1.chip_core_map)
    def chip_core_map(self) -> Dict[XY, int]:
        return CHIPS_PER_BOARD

    @overrides(VersionSpin1.spinnaker_links)
    def spinnaker_links(self) -> List[Tuple[int, int, int]]:
        return [(0, 0, 4)]

    @overrides(VersionSpin1.fpga_links)
    def fpga_links(self) -> List[Tuple[int, int, int, int, int]]:
        return [(0, 0, 3, 1, 1), (0, 0, 4, 1, 0), (0, 0, 5, 0, 15),
                (0, 1, 3, 1, 3), (0, 1, 4, 1, 2),
                (0, 2, 3, 1, 5), (0, 2, 4, 1, 4),
                (0, 3, 2, 1, 8), (0, 3, 3, 1, 7), (0, 3, 4, 1, 6),
                (1, 0, 4, 0, 14), (1, 0, 5, 0, 13),
                (1, 4, 2, 1, 10), (1, 4, 3, 1, 9),
                (2, 0, 4, 0, 12), (2, 0, 5, 0, 11),
                (2, 5, 2, 1, 12), (2, 5, 3, 1, 11),
                (3, 0, 4, 0, 10), (3, 0, 5, 0, 9),
                (3, 6, 2, 1, 14), (3, 6, 3, 1, 13),
                (4, 0, 0, 0, 6), (4, 0, 4, 0, 8),
                (4, 0, 5, 0, 7), (4, 7, 1, 2, 1),
                (4, 7, 2, 2, 0), (4, 7, 3, 1, 15),
                (5, 1, 0, 0, 4), (5, 1, 5, 0, 5),
                (5, 7, 1, 2, 3), (5, 7, 2, 2, 2),
                (6, 2, 0, 0, 2), (6, 2, 5, 0, 3),
                (6, 7, 1, 2, 5), (6, 7, 2, 2, 4),
                (7, 3, 0, 0, 0), (7, 3, 1, 2, 15), (7, 3, 5, 0, 1),
                (7, 4, 0, 2, 14), (7, 4, 1, 2, 13),
                (7, 5, 0, 2, 12), (7, 5, 1, 2, 11),
                (7, 6, 0, 2, 10), (7, 6, 1, 2, 9),
                (7, 7, 0, 2, 8), (7, 7, 1, 2, 7), (7, 7, 2, 2, 6)]

    @overrides(VersionSpin1.get_idle_energy)
    def get_idle_energy(
            self, time_s: float, n_frames: int, n_boards: int,
            n_chips: int) -> float:

        # We allow n_boards to be 0 to discount the cost of the board
        if n_boards == 0:
            energy = n_chips * self.WATTS_PER_IDLE_CHIP * time_s
        else:
            energy = n_boards * self.WATTS_FOR_48_CHIP_BOARD_IDLE_COST * time_s

        # The container of the boards idle energy
        if n_frames != 0:
            if n_boards > 1:
                energy += n_frames * self.WATTS_FOR_FRAME_IDLE_COST * time_s
            elif n_boards == 1:
                energy += (
                    n_frames * self.WATTS_FOR_48_CHIP_BOX_COST_OVERHEAD *
                    time_s)

        return energy

    @overrides(VersionSpin1.get_active_energy)
    def get_active_energy(
            self, time_s: float, n_frames: int, n_boards: int, n_chips: int,
            chip_active_time: ChipActiveTime,
            router_packets: RouterPackets) -> float:
        container_energy = 0.0
        if n_frames != 0:
            container_energy = (
                n_frames * self.WATTS_PER_FRAME_ACTIVE_COST_OVERHEAD * time_s)
        return (
            container_energy +
            self.get_idle_energy(time_s, n_frames, n_boards, n_chips) +
            self._get_router_active_energy(router_packets) +
            self._get_core_active_energy(chip_active_time))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Version5)
