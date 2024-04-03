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

from typing import Final, List, Mapping, Optional, Sequence, Tuple

from spinn_utilities.abstract_base import AbstractBase
from spinn_utilities.typing.coords import XY
from spinn_utilities.overrides import overrides

from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.full_wrap_machine import FullWrapMachine
from spinn_machine.machine import Machine

from .abstract_version import AbstractVersion

CHIPS_PER_BOARD: Final = {(0, 0): 152}


class Version201(AbstractVersion, metaclass=AbstractBase):
    # pylint: disable=abstract-method
    """
    Code for the 1 Chip test Spin2 board versions
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(max_cores_per_chip=152,
                         max_sdram_per_chip=1073741824)

    @property
    @overrides(AbstractVersion.n_scamp_cores)
    def n_scamp_cores(self) -> int:
        return 1

    @property
    @overrides(AbstractVersion.n_router_entries)
    def n_router_entries(self) -> int:
        return 16384

    @property
    @overrides(AbstractVersion.minimum_cores_expected)
    def minimum_cores_expected(self) -> int:
        return 150

    @property
    @overrides(AbstractVersion.clock_speeds_hz)
    def clock_speeds_hz(self) -> List[int]:
        return [150, 300]

    @property
    @overrides(AbstractVersion.dtcm_bytes)
    def dtcm_bytes(self) -> int:
        raise NotImplementedError

    @property
    @overrides(AbstractVersion.name)
    def name(self) -> str:
        return "Spin2 1 Chip"

    @property
    @overrides(AbstractVersion.number)
    def number(self) -> int:
        return 201

    @property
    @overrides(AbstractVersion.board_shape)
    def board_shape(self) -> Tuple[int, int]:
        return (1, 1)

    @property
    @overrides(AbstractVersion.chip_core_map)
    def chip_core_map(self) -> Mapping[XY, int]:
        return CHIPS_PER_BOARD

    @overrides(AbstractVersion.get_potential_ethernet_chips)
    def get_potential_ethernet_chips(
            self, width: int, height: int) -> Sequence[XY]:
        return [(0, 0)]

    @overrides(AbstractVersion._verify_size)
    def _verify_size(self, width: int, height: int):
        if width != 1:
            raise SpinnMachineException("Unexpected {width=}")
        if height != 1:
            raise SpinnMachineException("Unexpected {height=}")

    @overrides(AbstractVersion._create_machine)
    def _create_machine(self, width: int, height: int, origin: str) -> Machine:
        return FullWrapMachine(width, height, CHIPS_PER_BOARD, origin)

    @overrides(AbstractVersion.illegal_ethernet_message)
    def illegal_ethernet_message(self, x: int, y: int) -> Optional[str]:
        if x != 0 or y != 0:
            return "Only Chip 0, 0 may be an Ethernet Chip"
        return None
