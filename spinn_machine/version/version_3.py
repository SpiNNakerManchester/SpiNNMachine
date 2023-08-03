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

from spinn_utilities.overrides import overrides
from .version_spin1 import VersionSpin1
from spinn_machine.full_wrap_machine import FullWrapMachine
from spinn_machine.exceptions import SpinnMachineException

CHIPS_PER_BOARD = {(0, 0): 18, (0, 1): 18, (1, 0): 18, (1, 1): 18}


class Version3(VersionSpin1):
    """
    Code for the small Spin1 4 Chip boards

    Covers versions 2 and 3
    """

    __slots__ = []

    @property
    @overrides(VersionSpin1.name)
    def name(self):
        return "Spin1 4 Chip"

    @property
    @overrides(VersionSpin1.number)
    def number(self):
        return 3

    @property
    @overrides(VersionSpin1.board_shape)
    def board_shape(self):
        return (2, 2)

    @property
    @overrides(VersionSpin1.chip_core_map)
    def chip_core_map(self):
        return CHIPS_PER_BOARD

    @overrides(VersionSpin1.get_potential_ethernet_chips)
    def get_potential_ethernet_chips(self, width, height):
        return [(0, 0)]

    @overrides(VersionSpin1._verify_size)
    def _verify_size(self, width, height):
        if width != 2:
            raise SpinnMachineException("Unexpected {width=}")
        if height != 2:
            raise SpinnMachineException("Unexpected {height=}")

    @overrides(VersionSpin1._create_machine)
    def _create_machine(self, width, height, origin):
        return FullWrapMachine(width, height, CHIPS_PER_BOARD, origin)
