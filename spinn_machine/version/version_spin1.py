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

from spinn_utilities.abstract_base import AbstractBase
from spinn_utilities.overrides import overrides
from .abstract_version import AbstractVersion


class VersionSpin1(AbstractVersion, metaclass=AbstractBase):
    """
    Shared code for all Spin1 board versions
    """

    __slots__ = []

    def __init__(self):
        super().__init__(max_cores_per_chip=18, max_sdram_per_chip=123469792)

    @property
    @overrides(AbstractVersion.n_non_user_cores)
    def n_non_user_cores(self):
        return 1

    @property
    @overrides(AbstractVersion.n_router_entries)
    def n_router_entries(self):
        return 1023
