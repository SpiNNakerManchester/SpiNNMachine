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

from typing import Any, Dict, Final, List, Tuple

from spinn_utilities.typing.coords import XY
from spinn_utilities.overrides import overrides

from .version_48_chips import Version48Chips
from .version_factory import SPIN2_48CHIP
from .version_spin2 import VersionSpin2

# TODO get real values
CHIPS_PER_BOARD: Final = {
    (0, 0): 153, (0, 1): 153, (0, 2): 153, (0, 3): 153, (1, 0): 153,
    (1, 1): 152, (1, 2): 153, (1, 3): 152, (1, 4): 153, (2, 0): 153,
    (2, 1): 153, (2, 2): 153, (2, 3): 153, (2, 4): 153, (2, 5): 153,
    (3, 0): 153, (3, 1): 152, (3, 2): 153, (3, 3): 152, (3, 4): 153,
    (3, 5): 151, (3, 6): 153, (4, 0): 153, (4, 1): 153, (4, 2): 153,
    (4, 3): 151, (4, 4): 153, (4, 5): 153, (4, 6): 153, (4, 7): 153,
    (5, 1): 153, (5, 2): 152, (5, 3): 153, (5, 4): 152, (5, 5): 153,
    (5, 6): 152, (5, 7): 153, (6, 2): 152, (6, 3): 152, (6, 4): 153,
    (6, 5): 153, (6, 6): 153, (6, 7): 153, (7, 3): 153, (7, 4): 153,
    (7, 5): 153, (7, 6): 153, (7, 7): 153
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
        return SPIN2_48CHIP

    @property
    @overrides(VersionSpin2.chip_core_map)
    def chip_core_map(self) -> Dict[XY, int]:
        return CHIPS_PER_BOARD

    @overrides(VersionSpin2.spinnaker_links)
    def spinnaker_links(self) -> List[Tuple[int, int, int]]:
        # TODO
        return []

    @overrides(VersionSpin2.fpga_links)
    def fpga_links(self) -> List[Tuple[int, int, int, int, int]]:
        # TODO
        return []

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Version248)
