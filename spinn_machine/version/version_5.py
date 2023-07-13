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

from .version_spin1 import VersionSpin1


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
                return FullWrapMachine(width, height, origin)
            else:
                return HorizontalWrapMachine(width, height, origin)
        else:
            if height % 12 == 0:
                return VerticalWrapMachine(width, height, origin)
            else:
                return NoWrapMachine(width, height, origin)
