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

from typing import List, Iterable, Tuple, Final
from spinn_utilities.abstract_base import AbstractBase
from spinn_utilities.exceptions import ConfigException
from spinn_utilities.overrides import overrides

from spinn_machine.exceptions import SpinnMachineException
from .abstract_version import (
    AbstractVersion, RouterPackets, ChipActiveTime)


class VersionSpin1(AbstractVersion, metaclass=AbstractBase):
    # pylint: disable=abstract-method
    """
    Shared code for all Spin1 board versions
    """

    #: From Optimising the overall power usage on the SpiNNaker neuromimetic
    #: platform - all chips on a 48-chip board together use 5.23 + 5.17 + 5.52W
    #: + SDRAM of 0.90W = 16.82W when idle, so each chip use 0.35W
    WATTS_PER_IDLE_CHIP: Final = 0.35

    #: From measuring the power of all 48 chips on a boxed board with all cores
    #: idle for 1 hour and 806 cores active for 1 hour we get 31.88W idle and
    #: 59.38W active, so 27.50W active overhead, which is 0.034W per core
    WATTS_PER_CORE_ACTIVE_OVERHEAD: Final = 0.034

    #: stated in papers (SpiNNaker: A 1-W 18 core system-on-Chip for
    #: Massively-Parallel Neural Network Simulation)
    #: 25pJ per bit
    JOULES_PER_ROUTER_BIT = 0.000000000025

    #: stated in papers (SpiNNaker: A 1-W 18 core system-on-Chip for
    #: Massively-Parallel Neural Network Simulation)
    #: 25pJ per bit - spike packets are 40 bits so 1nJ per spike
    JOULES_PER_PACKET: Final = JOULES_PER_ROUTER_BIT * 40

    #: As above, but with extra 32-bits
    JOULES_PER_PACKET_WITH_PAYLOAD: Final = JOULES_PER_ROUTER_BIT * 72

    #: Cost of each packet type
    COST_PER_PACKET_TYPE = {
        "Local_Multicast_Packets": JOULES_PER_PACKET,
        "External_Multicast_Packets": JOULES_PER_PACKET,
        "Reinjected": JOULES_PER_PACKET,
        "Local_P2P_Packets": JOULES_PER_PACKET_WITH_PAYLOAD,
        "External_P2P_Packets": JOULES_PER_PACKET_WITH_PAYLOAD,
        "Local_NN_Packets": JOULES_PER_PACKET,
        "External_NN_Packets": JOULES_PER_PACKET,
        "Local_FR_Packets": JOULES_PER_PACKET_WITH_PAYLOAD,
        "External_FR_Packets": JOULES_PER_PACKET_WITH_PAYLOAD
    }

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
        return [200000000]

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

    @overrides(AbstractVersion.get_router_report_packet_types)
    def get_router_report_packet_types(self) -> List[str]:
        return list(self.COST_PER_PACKET_TYPE.keys())

    def _get_router_active_energy(
            self, router_packets: RouterPackets) -> float:
        return sum(
            value * self.COST_PER_PACKET_TYPE[name]
            for packets in router_packets.values()
            for name, value in packets.items())

    def _get_core_active_energy(
            self, core_active_times: ChipActiveTime) -> float:
        # TODO: treat cores that are active sometimes differently to cores that
        # are always idle
        return sum(
            time * self.WATTS_PER_CORE_ACTIVE_OVERHEAD
            for time, _n_cores in core_active_times.values())
