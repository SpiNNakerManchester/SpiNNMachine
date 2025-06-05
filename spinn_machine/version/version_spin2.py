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

import re
from typing import Dict, Final, List, Iterable, Tuple

from spinn_utilities.abstract_base import AbstractBase
from spinn_utilities.exceptions import ConfigException
from spinn_utilities.overrides import overrides

from spinn_machine.exceptions import SpinnMachineException
from .abstract_version import (
    AbstractVersion, ChipActiveTime, RouterPackets)

CHIPS_PER_BOARD: Final = {(0, 0): 152}
CORE_QX_QY_QP = re.compile(r"(\d)\.(\d)\.(\d)")
QUAD_MAP = (
    {0: (0, 0, 0), 1: (7, 6, 0), 2: (7, 6, 1), 3: (7, 6, 2), 4: (7, 6, 3),
     5: (7, 5, 0), 6: (7, 5, 1), 7: (7, 5, 2), 8: (7, 5, 3),
     9: (6, 6, 0), 10: (6, 6, 1), 11: (6, 6, 2), 12: (6, 6, 3),
     13: (6, 5, 0), 14: (6, 5, 1), 15: (6, 5, 2), 16: (6, 5, 3),
     17: (6, 4, 0), 18: (6, 4, 1), 19: (6, 4, 2), 20: (6, 4, 3),
     21: (5, 4, 0), 22: (5, 4, 1), 23: (5, 4, 2), 24: (5, 4, 3),
     25: (5, 6, 0), 26: (5, 6, 1), 27: (5, 6, 2), 28: (5, 6, 3),
     29: (3, 6, 0), 30: (3, 6, 1), 31: (3, 6, 2), 32: (3, 6, 3),
     33: (4, 6, 0), 34: (4, 6, 1), 35: (4, 6, 2), 36: (4, 6, 3),
     37: (5, 5, 0), 38: (5, 5, 1), 39: (5, 5, 2), 40: (5, 5, 3),
     41: (3, 5, 0), 42: (3, 5, 1), 43: (3, 5, 2), 44: (3, 5, 3),
     45: (4, 5, 0), 46: (4, 5, 1), 47: (4, 5, 2), 48: (4, 5, 3),
     49: (1, 6, 0), 50: (1, 6, 1), 51: (1, 6, 2), 52: (1, 6, 3),
     53: (2, 6, 0), 54: (2, 6, 1), 55: (2, 6, 2), 56: (2, 6, 3),
     57: (1, 5, 0), 58: (1, 5, 1), 59: (1, 5, 2), 60: (1, 5, 3),
     61: (2, 5, 0), 62: (2, 5, 1), 63: (2, 5, 2), 64: (2, 5, 3),
     65: (1, 4, 0), 66: (1, 4, 1), 67: (1, 4, 2), 68: (1, 4, 3),
     69: (2, 4, 0), 70: (2, 4, 1), 71: (2, 4, 2), 72: (2, 4, 3),
     73: (3, 4, 0), 74: (3, 4, 1), 75: (3, 4, 2), 76: (3, 4, 3),
     77: (1, 1, 0), 78: (1, 1, 1), 79: (1, 1, 2), 80: (1, 1, 3),
     81: (2, 1, 0), 82: (2, 1, 1), 83: (2, 1, 2), 84: (2, 1, 3),
     85: (1, 2, 0), 86: (1, 2, 1), 87: (1, 2, 2), 88: (1, 2, 3),
     89: (2, 2, 0), 90: (2, 2, 1), 91: (2, 2, 2), 92: (2, 2, 3),
     93: (1, 3, 0), 94: (1, 3, 1), 95: (1, 3, 2), 96: (1, 3, 3),
     97: (2, 3, 0), 98: (2, 3, 1), 99: (2, 3, 2), 100: (2, 3, 3),
     101: (3, 3, 0), 102: (3, 3, 1), 103: (3, 3, 2), 104: (3, 3, 3),
     105: (5, 1, 0), 106: (5, 1, 1), 107: (5, 1, 2), 108: (5, 1, 3),
     109: (3, 1, 0), 110: (3, 1, 1), 111: (3, 1, 2), 112: (3, 1, 3),
     113: (4, 1, 0), 114: (4, 1, 1), 115: (4, 1, 2), 116: (4, 1, 3),
     117: (5, 2, 0), 118: (5, 2, 1), 119: (5, 2, 2), 120: (5, 2, 3),
     121: (3, 2, 0), 122: (3, 2, 1), 123: (3, 2, 2), 124: (3, 2, 3),
     125: (4, 2, 0), 126: (4, 2, 1), 127: (4, 2, 2), 128: (4, 2, 3),
     129: (7, 1, 0), 130: (7, 1, 1), 131: (7, 1, 2), 132: (7, 1, 3),
     133: (6, 1, 0), 134: (6, 1, 1), 135: (6, 1, 2), 136: (6, 1, 3),
     137: (7, 2, 0), 138: (7, 2, 1), 139: (7, 2, 2), 140: (7, 2, 3),
     141: (6, 2, 0), 142: (6, 2, 1), 143: (6, 2, 2), 144: (6, 2, 3),
     145: (6, 3, 0), 146: (6, 3, 1), 147: (6, 3, 2), 148: (6, 3, 3),
     149: (5, 3, 0), 150: (5, 3, 1), 151: (5, 3, 2), 152: (5, 3, 3)})


class VersionSpin2(AbstractVersion, metaclass=AbstractBase):
    # pylint: disable=abstract-method
    """
    Code for the Spin2 board versions
    """

    __slots__ = ["_reverse_quad_map"]

    def __init__(self) -> None:
        super().__init__(max_cores_per_chip=153,
                         max_sdram_per_chip=1073741824)
        self._reverse_quad_map: Dict[Tuple[int, int, int], int] = (
            dict((v, k) for k, v in QUAD_MAP.items()))

    @property
    @overrides(AbstractVersion.n_scamp_cores)
    def n_scamp_cores(self) -> int:
        return 1

    @property
    @overrides(AbstractVersion.n_router_entries)
    def n_router_entries(self) -> int:
        return 16384

    @property
    @overrides(AbstractVersion.minimum_cores_expected)
    def minimum_cores_expected(self) -> int:
        return 100

    @property
    @overrides(AbstractVersion.clock_speeds_hz)
    def clock_speeds_hz(self) -> List[int]:
        return [150000000, 300000000]

    @property
    @overrides(AbstractVersion.dtcm_bytes)
    def dtcm_bytes(self) -> int:
        raise SpinnMachineException("Spin2 dtcm bytes unknown.")

    @overrides(AbstractVersion.quads_maps)
    def quads_maps(self) -> Dict[int, Tuple[int, int, int]]:
        return QUAD_MAP

    @overrides(AbstractVersion.qx_qy_qp_to_id)
    def qx_qy_qp_to_id(self, qx: int, qy: int, qp: int) -> int:
        return self._reverse_quad_map[(qx, qy, qp)]

    @overrides(AbstractVersion.id_to_qx_qy_qp)
    def id_to_qx_qy_qp(self, core_id: int) -> Tuple[int, int, int]:
        return QUAD_MAP[core_id]

    @overrides(AbstractVersion.version_parse_cores_string)
    def version_parse_cores_string(self, core_string: str) -> Iterable[int]:
        result = CORE_QX_QY_QP.fullmatch(core_string)
        if result is not None:
            qx = int(result.group(1))
            qy = int(result.group(2))
            qp = int(result.group(3))
            return (self.qx_qy_qp_to_id(qx, qy, qp),)

        raise ConfigException(
            f"{core_string} does not represent cores for Version 2 boards")

    @overrides(AbstractVersion.get_idle_energy)
    def get_idle_energy(
            self, time_s: float, n_frames: int, n_boards: int,
            n_chips: int) -> float:
        # TODO: Work this out for SpiNNaker 2
        raise SpinnMachineException("Spin2 idle energy unknown.")

    @overrides(AbstractVersion.get_active_energy)
    def get_active_energy(
            self, time_s: float, n_frames: int, n_boards: int, n_chips: int,
            chip_active_time: ChipActiveTime,
            router_packets: RouterPackets) -> float:
        # TODO: Work this out for SpiNNaker 2
        raise SpinnMachineException("Spin2 active energy unknown.")

    @overrides(AbstractVersion.get_router_report_packet_types)
    def get_router_report_packet_types(self) -> List[str]:
        # TODO: Work this out for SpiNNaker 2
        raise SpinnMachineException("Spin2 router report packet types unknown")
