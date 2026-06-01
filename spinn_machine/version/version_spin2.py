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
from bidict import bidict

from spinn_machine.exceptions import SpinnMachineException
from .abstract_version import (AbstractVersion, RouterPackets)

CHIPS_PER_BOARD: Final = {(0, 0): 152}
CORE_QX_QY_QP = re.compile(r"(\d)\.(\d)\.(\d)")
QUAD_MAP = bidict(
    {0: (0, 0, 0), 1: (7, 6, 3), 2: (7, 6, 2), 3: (7, 6, 1), 4: (7, 6, 0),
     5: (7, 5, 3), 6: (7, 5, 2), 7: (7, 5, 1), 8: (7, 5, 0),
     9: (6, 6, 3), 10: (6, 6, 2), 11: (6, 6, 1), 12: (6, 6, 0),
     13: (6, 5, 3), 14: (6, 5, 2), 15: (6, 5, 1), 16: (6, 5, 0),
     17: (6, 4, 3), 18: (6, 4, 2), 19: (6, 4, 1), 20: (6, 4, 0),
     21: (5, 4, 3), 22: (5, 4, 2), 23: (5, 4, 1), 24: (5, 4, 0),
     25: (5, 6, 3), 26: (5, 6, 2), 27: (5, 6, 1), 28: (5, 6, 0),
     29: (3, 6, 3), 30: (3, 6, 2), 31: (3, 6, 1), 32: (3, 6, 0),
     33: (4, 6, 3), 34: (4, 6, 2), 35: (4, 6, 1), 36: (4, 6, 0),
     37: (5, 5, 3), 38: (5, 5, 2), 39: (5, 5, 1), 40: (5, 5, 0),
     41: (3, 5, 3), 42: (3, 5, 2), 43: (3, 5, 1), 44: (3, 5, 0),
     45: (4, 5, 3), 46: (4, 5, 2), 47: (4, 5, 1), 48: (4, 5, 0),
     49: (1, 6, 3), 50: (1, 6, 2), 51: (1, 6, 1), 52: (1, 6, 0),
     53: (2, 6, 3), 54: (2, 6, 2), 55: (2, 6, 1), 56: (2, 6, 0),
     57: (1, 5, 3), 58: (1, 5, 2), 59: (1, 5, 1), 60: (1, 5, 0),
     61: (2, 5, 3), 62: (2, 5, 2), 63: (2, 5, 1), 64: (2, 5, 0),
     65: (1, 4, 3), 66: (1, 4, 2), 67: (1, 4, 1), 68: (1, 4, 0),
     69: (2, 4, 3), 70: (2, 4, 2), 71: (2, 4, 1), 72: (2, 4, 0),
     73: (3, 4, 3), 74: (3, 4, 2), 75: (3, 4, 1), 76: (3, 4, 0),
     77: (1, 1, 3), 78: (1, 1, 2), 79: (1, 1, 1), 80: (1, 1, 0),
     81: (2, 1, 3), 82: (2, 1, 2), 83: (2, 1, 1), 84: (2, 1, 0),
     85: (1, 2, 3), 86: (1, 2, 2), 87: (1, 2, 1), 88: (1, 2, 0),
     89: (2, 2, 3), 90: (2, 2, 2), 91: (2, 2, 1), 92: (2, 2, 0),
     93: (1, 3, 3), 94: (1, 3, 2), 95: (1, 3, 1), 96: (1, 3, 0),
     97: (2, 3, 3), 98: (2, 3, 2), 99: (2, 3, 1), 100: (2, 3, 0),
     101: (3, 3, 3), 102: (3, 3, 2), 103: (3, 3, 1), 104: (3, 3, 0),
     105: (5, 1, 3), 106: (5, 1, 2), 107: (5, 1, 1), 108: (5, 1, 0),
     109: (3, 1, 3), 110: (3, 1, 2), 111: (3, 1, 1), 112: (3, 1, 0),
     113: (4, 1, 3), 114: (4, 1, 2), 115: (4, 1, 1), 116: (4, 1, 0),
     117: (5, 2, 3), 118: (5, 2, 2), 119: (5, 2, 1), 120: (5, 2, 0),
     121: (3, 2, 3), 122: (3, 2, 2), 123: (3, 2, 1), 124: (3, 2, 0),
     125: (4, 2, 3), 126: (4, 2, 2), 127: (4, 2, 1), 128: (4, 2, 0),
     129: (7, 1, 3), 130: (7, 1, 2), 131: (7, 1, 1), 132: (7, 1, 0),
     133: (6, 1, 3), 134: (6, 1, 2), 135: (6, 1, 1), 136: (6, 1, 0),
     137: (7, 2, 3), 138: (7, 2, 2), 139: (7, 2, 1), 140: (7, 2, 0),
     141: (6, 2, 3), 142: (6, 2, 2), 143: (6, 2, 1), 144: (6, 2, 0),
     145: (6, 3, 3), 146: (6, 3, 2), 147: (6, 3, 1), 148: (6, 3, 0),
     149: (5, 3, 3), 150: (5, 3, 2), 151: (5, 3, 1), 152: (5, 3, 0)})


class S2_HW_MAP:
    QUAD_MAP = QUAD_MAP
    PERIPHERY = bidict({154: (1,0,0), 155: (2,0,0)})
    S_LINK = bidict({156: (3,0,0),  157: (4,0,0)})
    SW_LINK = bidict({158: (5,0,0), 159: (6,0,0)})
    W_LINK = bidict({160: (7,3,0), 161: (7,4,0)})
    N_LINK = bidict({162: (4,7,0),163: (3,7,0)})
    NE_LINK = bidict({164: (2,7,0),165: (1,7,0)})
    E_LINK = bidict({166: (0,4,0),167:(0,3,0)})
    ROUTER = bidict({168: (4,3,0),169: (4,4,0)})
    MEM_A = bidict({170: (0,6,0), 171: (0,5,0)})
    MEM_B = bidict({172: (0,2,0), 173: (0,1,0)})
    HOST_IF = bidict({174: (5,7,0), 175: (6,7,0)})
    HW_LIST: List[bidict] = [QUAD_MAP, PERIPHERY, S_LINK, SW_LINK, W_LINK, N_LINK, NE_LINK, E_LINK, ROUTER, MEM_A, MEM_B, HOST_IF]

    def __contains__(self, item):
        return any([item in hw for hw in self.HW_LIST])

    def inv(self, item):
        """Emulate the behavior of bidict
        """
        for hw in self.HW_LIST:
            core_id = hw.inv.get(item)
            if core_id is not None:
                return core_id
        raise KeyError(f"Item {item} not found in any hardware map")

    def __getitem__(self, key):
        for hw in self.HW_LIST:
            if key in hw:
                return hw[key]


HW_MAP = S2_HW_MAP()


class VersionSpin2(AbstractVersion, metaclass=AbstractBase):
    # pylint: disable=abstract-method
    """
    Code for the Spin2 board versions
    """

    __slots__ = ["_reverse_quad_map"]

    def __init__(self) -> None:
        super().__init__(max_cores_per_chip=152,
                         max_sdram_per_chip=1073741824)
        self._reverse_quad_map: Dict[Tuple[int, int, int], int] = (
            dict((v, k) for k, v in QUAD_MAP.items()))

    @property
    @overrides(AbstractVersion.n_scamp_cores)
    def n_scamp_cores(self) -> int:
        return 2

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

    @overrides(AbstractVersion.quad_maps)
    def quad_maps(self) -> Dict[int, Tuple[int, int, int]]:
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
            sum_chip_active_time: float,
            router_packets: RouterPackets) -> float:
        # TODO: Work this out for SpiNNaker 2
        raise SpinnMachineException("Spin2 active energy unknown.")

    @overrides(AbstractVersion.get_router_report_packet_types)
    def get_router_report_packet_types(self) -> List[str]:
        # TODO: Work this out for SpiNNaker 2
        raise SpinnMachineException("Spin2 router report packet types unknown")
