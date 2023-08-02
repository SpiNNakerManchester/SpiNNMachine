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
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.full_wrap_machine import FullWrapMachine
from spinn_machine.horizontal_wrap_machine import HorizontalWrapMachine
from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.vertical_wrap_machine import VerticalWrapMachine
from spinn_machine import SpiNNakerTriadGeometry
from .version_spin1 import VersionSpin1

CHIPS_PER_BOARD = {
    (0, 0): 18, (0, 1): 18, (0, 2): 18, (0, 3): 18, (1, 0): 18, (1, 1): 17,
    (1, 2): 18, (1, 3): 17, (1, 4): 18, (2, 0): 18, (2, 1): 18, (2, 2): 18,
    (2, 3): 18, (2, 4): 18, (2, 5): 18, (3, 0): 18, (3, 1): 17, (3, 2): 18,
    (3, 3): 17, (3, 4): 18, (3, 5): 17, (3, 6): 18, (4, 0): 18, (4, 1): 18,
    (4, 2): 18, (4, 3): 18, (4, 4): 18, (4, 5): 18, (4, 6): 18, (4, 7): 18,
    (5, 1): 18, (5, 2): 17, (5, 3): 18, (5, 4): 17, (5, 5): 18, (5, 6): 17,
    (5, 7): 18, (6, 2): 18, (6, 3): 18, (6, 4): 18, (6, 5): 18, (6, 6): 18,
    (6, 7): 18, (7, 3): 18, (7, 4): 18, (7, 5): 18, (7, 6): 18, (7, 7): 18
}


class Version5(VersionSpin1):
    """
    Code for the large Spin1 48 Chip boards

    Covers versions 4 and 5
    """

    __slots__ = []

    @property
    @overrides(VersionSpin1.name)
    def name(self):
        return "Spin1 48 Chip"

    @property
    @overrides(VersionSpin1.number)
    def number(self):
        return 5

    @property
    @overrides(VersionSpin1.board_shape)
    def board_shape(self):
        return (8, 8)

    @property
    @overrides(VersionSpin1.chip_core_map)
    def chip_core_map(self):
        return CHIPS_PER_BOARD

    @overrides(VersionSpin1.get_potential_ethernet_chips)
    def get_potential_ethernet_chips(self, width, height):
        geometry = SpiNNakerTriadGeometry.get_spinn5_geometry()
        return geometry.get_potential_ethernet_chips(width, height)

    @overrides(VersionSpin1._verify_size)
    def _verify_size(self, width, height):
        if width == height == 8:
            # 1 board
            return
        if width % 12 not in [0, 4]:
            raise SpinnMachineException(
                f"{width=} must be a multiple of 12 "
                f"or a multiple of 12 plus 4")
        if height % 12 not in [0, 4]:
            raise SpinnMachineException(
                f"{height=} must be a multiple of 12 "
                f"or a multiple of 12 plus 4")

    @overrides(VersionSpin1._create_machine)
    def _create_machine(self, width, height, origin):
        if width % 12 == 0:
            if height % 12 == 0:
                return FullWrapMachine(width, height, CHIPS_PER_BOARD, origin)
            else:
                return HorizontalWrapMachine(
                    width, height, CHIPS_PER_BOARD, origin)
        else:
            if height % 12 == 0:
                return VerticalWrapMachine(
                    width, height, CHIPS_PER_BOARD, origin)
            else:
                return NoWrapMachine(width, height, CHIPS_PER_BOARD, origin)
