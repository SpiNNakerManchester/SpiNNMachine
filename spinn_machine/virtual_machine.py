# Copyright (c) 2016 The University of Manchester
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
import math
from collections import defaultdict
import logging
from typing import Dict, List, Optional, Set, Tuple
from spinn_utilities.config_holder import get_config_str_or_none
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY
from spinn_machine.data import MachineDataView
from spinn_machine.ignores import IgnoreChip, IgnoreCore, IgnoreLink
from .chip import Chip
from .router import Router
from .link import Link
from .machine import Machine

logger = FormatAdapter(logging.getLogger(__name__))


def virtual_machine(width: int, height: int, validate: bool = True):
    """
    Create a virtual SpiNNaker machine, used for planning execution.

    :param int width: the width of the virtual machine in chips
    :param int height: the height of the virtual machine in chips
    :param bool validate: if True will call the machine validate function

    :returns: a virtual machine (that cannot execute code)
    :rtype: ~spinn_machine.Machine
    """
    factory = _VirtualMachine(width, height, validate)
    return factory.machine


def virtual_machine_by_min_size(
        width: int, height: int, validate: bool = True):
    """
    Create a virtual SpiNNaker machine, used for planning execution.

    :param int width: the minimum width of the virtual machine in chips
    :param int height: the minimum height of the virtual machine in chips
    :param bool validate: if True will call the machine validate function

    :returns: a virtual machine (that cannot execute code)
    :rtype: ~spinn_machine.Machine
    """
    version = MachineDataView.get_machine_version()
    w_board, h_board = version.board_shape
    # check for edge case
    if width <= w_board and height > h_board:
        width = w_board * 2
    if height <= h_board and width > w_board:
        height = h_board * 2
    width = w_board * math.ceil(width / w_board)
    height = h_board * math.ceil(height / h_board)
    return virtual_machine(width, height, validate)


def virtual_machine_by_cores(n_cores: int, validate: bool = True):
    """
    Create a virtual SpiNNaker machine, used for planning execution.

    Semantic sugar for

    MachineDataView.get_machine_version()

    width, height = version.size_from_n_cores(n_cores)

    return virtual_machine(width, height, validate)

    :param n_cores: Minimum number of user cores
    :param bool validate: if True will call the machine validate function

    :returns: a virtual machine (that cannot execute code)
    :rtype: ~spinn_machine.Machine
    :raises SpinnMachineException:
        If multiple boards are needed but not supported
    """
    version = MachineDataView.get_machine_version()
    width, height = version.size_from_n_cores(n_cores)
    return virtual_machine(width, height, validate)


def virtual_machine_by_boards(n_boards: int, validate: bool = True):
    """
    Create a virtual SpiNNaker machine, used for planning execution.

    semantic sugar for:

    version = MachineDataView.get_machine_version()

    width, height = version.size_from_n_boards(n_boards)

    return virtual_machine(width, height, validate)

    :param n_boards: Minimum number of boards
    :param bool validate: if True will call the machine validate function

    :returns: a virtual machine (that cannot execute code)
    :rtype: ~spinn_machine.Machine
    :raises SpinnMachineException:
        If multiple boards are needed but not supported
    """
    version = MachineDataView.get_machine_version()
    width, height = version.size_from_n_boards(n_boards)
    return virtual_machine(width, height, validate)


class _VirtualMachine(object):
    """
    A Virtual SpiNNaker machine factory
    """

    __slots__ = (
        "_unused_cores",
        "_unused_links",
        "_machine",
        "_with_monitors",
        "_n_router_entries"
    )

    _4_chip_down_links = {
        (0, 0, 3), (0, 0, 4), (0, 1, 3), (0, 1, 4),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
    }

    ORIGIN = "Virtual"

    def __init__(self, width: int, height: int, validate: bool = True):
        version = MachineDataView.get_machine_version()
        version.verify_size(width, height)
        max_cores = version.max_cores_per_chip
        self._n_router_entries = version.n_router_entries
        self._machine = version.create_machine(
            width, height, origin=self.ORIGIN)

        # Store the down items
        unused_chips = []
        for down_chip in IgnoreChip.parse_string(get_config_str_or_none(
                "Machine", "down_chips")):
            if down_chip.ip_address is None:
                unused_chips.append((down_chip.x, down_chip.y))

        self._unused_cores: Dict[XY, Set[int]] = defaultdict(set)
        for down_core in IgnoreCore.parse_string(get_config_str_or_none(
                "Machine", "down_cores")):
            if down_core.ip_address is None:
                self._unused_cores[down_core.x, down_core.y].add(
                    down_core.virtual_p)

        self._unused_links: Set[Tuple[int, int, int]] = set()
        for down_link in IgnoreLink.parse_string(get_config_str_or_none(
                "Machine", "down_links")):
            if down_link.ip_address is None:
                self._unused_links.add(
                    (down_link.x, down_link.y, down_link.link))

        if width == 2:  # Already checked height is now also 2
            self._unused_links.update(_VirtualMachine._4_chip_down_links)

        ethernet_chips = version.get_potential_ethernet_chips(width, height)

        # Compute list of chips that are possible based on configuration
        # If there are no wrap arounds, and the the size is not 2 * 2,
        # the possible chips depend on the 48 chip board's gaps
        configured_chips: Dict[XY, Tuple[XY, int]] = dict()
        for eth in ethernet_chips:
            for (xy, n_cores) in self._machine.get_xy_cores_by_ethernet(
                    *eth):
                if xy not in unused_chips:
                    configured_chips[xy] = (eth, min(n_cores, max_cores))

        # for chip in self._unreachable_outgoing_chips:
        #    configured_chips.remove(chip)
        # for chip in self._unreachable_incoming_chips:
        #    configured_chips.remove(chip)

        for xy in configured_chips:
            if xy in ethernet_chips:
                x, y = xy
                new_chip = self._create_chip(
                    xy, configured_chips, f"127.0.{x}.{y}")
            else:
                new_chip = self._create_chip(xy, configured_chips)
            self._machine.add_chip(new_chip)

        self._machine.add_spinnaker_links()
        self._machine.add_fpga_links()
        if validate:
            self._machine.validate()

    @property
    def machine(self) -> Machine:
        """
        The Machine object created by this Factory

        :rtype: Machine
        """
        return self._machine

    def _create_chip(self, xy: XY, configured_chips: Dict[XY, Tuple[XY, int]],
                     ip_address: Optional[str] = None) -> Chip:
        chip_links = self._calculate_links(xy, configured_chips)
        chip_router = Router(chip_links, self._n_router_entries)

        ((eth_x, eth_y), n_cores) = configured_chips[xy]

        down_cores = self._unused_cores.get(xy, None)
        x, y = xy
        sdram = MachineDataView.get_machine_version().max_sdram_per_chip
        return Chip(
            x, y, n_cores, chip_router, sdram, eth_x, eth_y,
            ip_address, down_cores=down_cores)

    def _calculate_links(
            self, xy: XY, configured_chips: Dict[XY, Tuple[XY, int]]
            ) -> List[Link]:
        """
        Calculate the links needed for a machine structure
        """
        x, y = xy
        links = list()
        for link_id in range(6):
            if (x, y, link_id) not in self._unused_links:
                link_x_y = self._machine.xy_over_link(x, y, link_id)
                if link_x_y in configured_chips:
                    links.append(
                        Link(source_x=x, source_y=y,
                             destination_x=link_x_y[0],
                             destination_y=link_x_y[1],
                             source_link_id=link_id))
        return links
