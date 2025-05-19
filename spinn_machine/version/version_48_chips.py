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

import math
from typing import Optional, Sequence, Tuple
from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XY
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.machine import Machine
from spinn_machine.full_wrap_machine import FullWrapMachine
from spinn_machine.horizontal_wrap_machine import HorizontalWrapMachine
from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.vertical_wrap_machine import VerticalWrapMachine
from spinn_machine import SpiNNakerTriadGeometry
from .abstract_version import AbstractVersion


class Version48Chips(AbstractVersion):
    """
    Code shared by 48 Chip boards

    """
    # pylint: disable=abstract-method

    __slots__ = ()

    @property
    @overrides(AbstractVersion.board_shape)
    def board_shape(self) -> Tuple[int, int]:
        return (8, 8)

    @overrides(AbstractVersion.get_potential_ethernet_chips)
    def get_potential_ethernet_chips(
            self, width: int, height: int) -> Sequence[XY]:
        geometry = SpiNNakerTriadGeometry.get_spinn5_geometry()
        return geometry.get_potential_ethernet_chips(width, height)

    @overrides(AbstractVersion._verify_size)
    def _verify_size(self, width: int, height: int) -> None:
        if width <= 8:
            if width == 8 and height == 8:
                # 1 board
                return
            else:
                raise SpinnMachineException(
                    f"{width=} and {height=} not supported")
        elif height <= 8:
            raise SpinnMachineException(
                f"{width=} and {height=} not supported")
        if width % 4 != 0:
            raise SpinnMachineException(
                f"{width=} must be a multiple of 12 "
                f"or a multiple of 12 plus 4")
        if height % 4 != 0:
            raise SpinnMachineException(
                f"{height=} must be a multiple of 12 "
                f"or a multiple of 12 plus 4")

    @overrides(AbstractVersion._create_machine)
    def _create_machine(self, width: int, height: int, origin: str) -> Machine:
        if width % 12 == 0:
            if height % 12 == 0:
                return FullWrapMachine(
                    width, height, self.chip_core_map, origin)
            else:
                return HorizontalWrapMachine(
                    width, height, self.chip_core_map, origin)
        else:
            if height % 12 == 0:
                return VerticalWrapMachine(
                    width, height, self.chip_core_map, origin)
            else:
                return NoWrapMachine(width, height, self.chip_core_map, origin)

    @overrides(AbstractVersion.illegal_ethernet_message)
    def illegal_ethernet_message(self, x: int, y: int) -> Optional[str]:
        if x % 4 != 0:
            return "Only Chip with X divisible by 4 may be an Ethernet Chip"
        if (x + y) % 12 != 0:
            return "Only Chip with x + y divisible by 12 " \
                   "may be an Ethernet Chip"
        return None

    @overrides(AbstractVersion.size_from_n_boards)
    def size_from_n_boards(self, n_boards: int) -> Tuple[int, int]:
        if n_boards <= 1:
            return 8, 8
        # This replicates how spalloc does it
        # returning a rectangle of triads
        triads = math.ceil(n_boards / 3)
        width = math.ceil(math.sqrt(triads))
        height = math.ceil(triads / width)
        return width * 12 + 4, height * 12 + 4

    @property
    @overrides(AbstractVersion.supports_multiple_boards)
    def supports_multiple_boards(self) -> bool:
        return True
