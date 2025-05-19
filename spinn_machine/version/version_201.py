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

from typing import Any, Dict, Final, List, Optional, Sequence, Tuple

from spinn_utilities.typing.coords import XY
from spinn_utilities.overrides import overrides

from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.machine import Machine

from .version_factory import SPIN2_1CHIP
from .version_spin2 import VersionSpin2

CHIPS_PER_BOARD: Final = {(0, 0): 153}


class Version201(VersionSpin2):
    # pylint: disable=abstract-method
    """
    Code for the 1 Chip test Spin2 board versions
    """

    __slots__ = ()

    @property
    @overrides(VersionSpin2.name)
    def name(self) -> str:
        return "Spin2 1 Chip"

    @property
    @overrides(VersionSpin2.number)
    def number(self) -> int:
        return SPIN2_1CHIP

    @property
    @overrides(VersionSpin2.board_shape)
    def board_shape(self) -> Tuple[int, int]:
        return (1, 1)

    @property
    @overrides(VersionSpin2.chip_core_map)
    def chip_core_map(self) -> Dict[XY, int]:
        return CHIPS_PER_BOARD

    @overrides(VersionSpin2.get_potential_ethernet_chips)
    def get_potential_ethernet_chips(
            self, width: int, height: int) -> Sequence[XY]:
        return [(0, 0)]

    @overrides(VersionSpin2._verify_size)
    def _verify_size(self, width: int, height: int) -> None:
        if width != 1:
            raise SpinnMachineException(f"Unexpected {width=}")
        if height != 1:
            raise SpinnMachineException(f"Unexpected {height=}")

    @overrides(VersionSpin2._create_machine)
    def _create_machine(self, width: int, height: int, origin: str) -> Machine:
        return NoWrapMachine(width, height, CHIPS_PER_BOARD, origin)

    @overrides(VersionSpin2.illegal_ethernet_message)
    def illegal_ethernet_message(self, x: int, y: int) -> Optional[str]:
        if x != 0 or y != 0:
            return "Only Chip 0, 0 may be an Ethernet Chip"
        return None

    @property
    @overrides(VersionSpin2.supports_multiple_boards)
    def supports_multiple_boards(self) -> bool:
        return False

    @overrides(VersionSpin2.spinnaker_links)
    def spinnaker_links(self) -> List[Tuple[int, int, int]]:
        return []

    @overrides(VersionSpin2.fpga_links)
    def fpga_links(self) -> List[Tuple[int, int, int, int, int]]:
        return []

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Version201)
