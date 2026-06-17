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

from typing import Any, Dict, Final

from spinn_utilities.typing.coords import XY
from spinn_utilities.overrides import overrides

from .version_48_chips import Version48Chips
from .version_factory import Spin2Gen
from .version_spin2 import VersionSpin2

# TODO get real values
CHIPS_PER_BOARD: Final = {
    (0, 0): 152, (0, 1): 152, (0, 2): 152, (0, 3): 152, (1, 0): 152,
    (1, 1): 152, (1, 2): 152, (1, 3): 152, (1, 4): 152, (2, 0): 152,
    (2, 1): 152, (2, 2): 152, (2, 3): 152, (2, 4): 152, (2, 5): 152,
    (3, 0): 152, (3, 1): 152, (3, 2): 152, (3, 3): 152, (3, 4): 152,
    (3, 5): 152, (3, 6): 152, (4, 0): 152, (4, 1): 152, (4, 2): 152,
    (4, 3): 152, (4, 4): 152, (4, 5): 152, (4, 6): 152, (4, 7): 152,
    (5, 1): 152, (5, 2): 152, (5, 3): 152, (5, 4): 152, (5, 5): 152,
    (5, 6): 152, (5, 7): 152, (6, 2): 152, (6, 3): 152, (6, 4): 152,
    (6, 5): 152, (6, 6): 152, (6, 7): 152, (7, 3): 152, (7, 4): 152,
    (7, 5): 152, (7, 6): 152, (7, 7): 152
}


class Version248(VersionSpin2, Version48Chips):
    # pylint: disable=abstract-method
    """
    Code for the 48 Chip Spin2 board versions
    """

    __slots__ = ()

    @property
    @overrides(VersionSpin2.name)
    def name(self) -> str:
        return "Spin2 48 Chips"

    @property
    @overrides(VersionSpin2.number)
    def number(self) -> int:
        return Spin2Gen.SPIN2_48CHIP.value

    @property
    @overrides(VersionSpin2.chip_core_map)
    def chip_core_map(self) -> Dict[XY, int]:
        return CHIPS_PER_BOARD

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Version248)
