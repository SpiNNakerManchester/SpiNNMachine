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
from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.machine import Machine
from spinn_machine import SpiNNakerTriadGeometry

from .version_48_chips import Version48Chips
from .version_factory import SPIN2_48CHIP
from .version_spin2 import VersionSpin2

# TODO get real values
CHIPS_PER_BOARD: Final = {
    (0, 0): 152, (0, 1): 152, (0, 2): 152, (0, 3): 152, (1, 0): 152,
    (1, 1): 151, (1, 2): 152, (1, 3): 151, (1, 4): 152, (2, 0): 152,
    (2, 1): 152, (2, 2): 152, (2, 3): 152, (2, 4): 152, (2, 5): 152,
    (3, 0): 152, (3, 1): 151, (3, 2): 152, (3, 3): 151, (3, 4): 152,
    (3, 5): 150, (3, 6): 152, (4, 0): 152, (4, 1): 152, (4, 2): 152,
    (4, 3): 150, (4, 4): 152, (4, 5): 152, (4, 6): 152, (4, 7): 152,
    (5, 1): 152, (5, 2): 151, (5, 3): 152, (5, 4): 151, (5, 5): 152,
    (5, 6): 151, (5, 7): 152, (6, 2): 151, (6, 3): 151, (6, 4): 152,
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
        return SPIN2_48CHIP

    @property
    @overrides(VersionSpin2.chip_core_map)
    def chip_core_map(self) -> Mapping[XY, int]:
        return CHIPS_PER_BOARD

    @overrides(VersionSpin2.spinnaker_links)
    def spinnaker_links(self) -> List[Tuple[int, int, int]]:
        # TODO
        return []

    @overrides(VersionSpin2.fpga_links)
    def fpga_links(self) -> List[Tuple[int, int, int, int, int]]:
        # TODO
        return []
