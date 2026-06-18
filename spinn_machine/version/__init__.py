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

from .spin1_gen import Spin1Gen
from .spin2_gen import Spin2Gen
from .version_factory import (
    ALL_BOARD_TYPES, BIG_BOARD_TYPES, FOUR_PLUS_BOARD_TYPES,
    FPGA_BOARD_TYPES, GEN1_BOARD_TYPES, GEN2_BOARD_TYPES,
    MANY_BOARD_TYPES, version_factory)

__all__ = ["ALL_BOARD_TYPES", "BIG_BOARD_TYPES", "FOUR_PLUS_BOARD_TYPES",
           "FPGA_BOARD_TYPES", "GEN1_BOARD_TYPES", "GEN2_BOARD_TYPES",
           "MANY_BOARD_TYPES", "version_factory",
           "Spin1Gen", "Spin2Gen"]
