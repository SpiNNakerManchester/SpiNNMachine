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

from typing import List, Iterable, Tuple
from spinn_utilities.abstract_base import AbstractBase
from spinn_utilities.exceptions import ConfigException
from spinn_utilities.overrides import overrides

from spinn_machine.exceptions import SpinnMachineException
from .abstract_version import AbstractVersion


class VersionSpin1(AbstractVersion, metaclass=AbstractBase):
    # pylint: disable=abstract-method
    """
    Shared code for all Spin1 board versions
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(max_cores_per_chip=18, max_sdram_per_chip=123469792)

    @property
    @overrides(AbstractVersion.n_scamp_cores)
    def n_scamp_cores(self) -> int:
        return 1

    @property
    @overrides(AbstractVersion.n_router_entries)
    def n_router_entries(self) -> int:
        return 1023

    @property
    @overrides(AbstractVersion.minimum_cores_expected)
    def minimum_cores_expected(self) -> int:
        return 5

    @property
    @overrides(AbstractVersion.clock_speeds_hz)
    def clock_speeds_hz(self) -> List[int]:
        return [200]

    @property
    @overrides(AbstractVersion.dtcm_bytes)
    def dtcm_bytes(self) -> int:
        return 2 ** 16

    @overrides(AbstractVersion.quads_maps)
    def quads_maps(self) -> None:
        return None

    @overrides(AbstractVersion.qx_qy_qp_to_id)
    def qx_qy_qp_to_id(self, qx: int, qy: int, qp: int) -> int:
        raise SpinnMachineException("Not supported in Version 1")

    @overrides(AbstractVersion.id_to_qx_qy_qp)
    def id_to_qx_qy_qp(self, core_id: int) -> Tuple[int, int, int]:
        raise SpinnMachineException("Not supported in Version 1")

    @overrides(AbstractVersion.version_parse_cores_string)
    def version_parse_cores_string(self, core_string: str) -> Iterable[int]:
        raise ConfigException(
            f"{core_string} does not represent cores for Version 1 boards")
