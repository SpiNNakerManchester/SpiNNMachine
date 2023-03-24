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

from collections import defaultdict
import logging
from spinn_utilities.config_holder import get_config_int, get_config_str
from spinn_utilities.log import FormatAdapter
from .chip import Chip
from .exceptions import SpinnMachineInvalidParameterException
from .router import Router
from .sdram import SDRAM
from .link import Link
from .spinnaker_triad_geometry import SpiNNakerTriadGeometry
from .machine_factory import machine_from_size
from spinn_machine.ignores import IgnoreChip, IgnoreCore, IgnoreLink

logger = FormatAdapter(logging.getLogger(__name__))


def _verify_width_height(width, height):
    try:
        if width < 0 or height < 0:
            raise SpinnMachineInvalidParameterException(
                "width or height", f"{width} and {height}",
                "Negative dimensions are not supported")
    except TypeError as original:
        if width is None or height is None:
            raise SpinnMachineInvalidParameterException(
                "width or height", f"{width} and {height}",
                "parameter required") from original
        raise

    if width == height == 2:
        return
    if width == height == 8:
        return
    if width % 12 != 0 and (width - 4) % 12 != 0:
        raise SpinnMachineInvalidParameterException(
            "width", width,
            "A virtual machine must have a width that is divisible by 12 or "
            "width - 4 that is divisible by 12")
    if height % 12 != 0 and (height - 4) % 12 != 0:
        raise SpinnMachineInvalidParameterException(
            "height", height,
            "A virtual machine must have a height that is divisible by 12 or "
            "height - 4 that is divisible by 12")


def virtual_machine(
        width, height, n_cpus_per_chip=None, validate=True):
    """
    Create a virtual SpiNNaker machine, used for planning execution.

    :param int width: the width of the virtual machine in chips
    :param int height: the height of the virtual machine in chips
    :param int n_cpus_per_chip: The number of CPUs to put on each chip
    :param bool validate: if True will call the machine validate function
    :returns: a virtual machine (that cannot execute code)
    :rtype: Machine
    """

    factory = _VirtualMachine(width, height, n_cpus_per_chip, validate)
    return factory.machine


class _VirtualMachine(object):
    """
    A Virtual SpiNNaker machine factory
    """

    __slots__ = (
        "_unused_cores",
        "_unused_links",
        "_machine",
        "_sdram_per_chip",
        "_with_monitors")

    _4_chip_down_links = {
        (0, 0, 3), (0, 0, 4), (0, 1, 3), (0, 1, 4),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
    }

    ORIGIN = "Virtual"

    def __init__(
            self, width, height, n_cpus_per_chip=None, validate=True):

        _verify_width_height(width, height)
        self._machine = machine_from_size(width, height, origin=self.ORIGIN)

        # Store the details
        self._sdram_per_chip = get_config_int(
            "Machine", "max_sdram_allowed_per_chip")

        # Store the down items
        unused_chips = []
        for down_chip in IgnoreChip.parse_string(get_config_str(
                "Machine", "down_chips")):
            if isinstance(down_chip, IgnoreChip):
                if down_chip.ip_address is None:
                    unused_chips.append((down_chip.x, down_chip.y))
            else:
                unused_chips.append((down_chip[0], down_chip[1]))

        self._unused_cores = defaultdict(set)
        for down_core in IgnoreCore.parse_string(get_config_str(
                "Machine", "down_cores")):
            if isinstance(down_core, IgnoreCore):
                if down_core.ip_address is None:
                    self._unused_cores[(down_core.x, down_core.y)].add(
                        down_core.virtual_p)
            else:
                self._unused_cores[(down_core[0], down_core[1])].add(
                    down_core[2])

        self._unused_links = set()
        for down_link in IgnoreLink.parse_string(get_config_str(
                "Machine", "down_links")):
            if isinstance(down_link, IgnoreLink):
                if down_link.ip_address is None:
                    self._unused_links.add(
                        (down_link.x, down_link.y, down_link.link))
            else:
                self._unused_links.add(
                    (down_link[0], down_link[1], down_link[2]))

        if width == 2:  # Already checked height is now also 2
            self._unused_links.update(_VirtualMachine._4_chip_down_links)

        # Calculate the Ethernet connections in the machine, assuming 48-node
        # boards
        geometry = SpiNNakerTriadGeometry.get_spinn5_geometry()
        ethernet_chips = geometry.get_potential_ethernet_chips(width, height)

        # Compute list of chips that are possible based on configuration
        # If there are no wrap arounds, and the the size is not 2 * 2,
        # the possible chips depend on the 48 chip board's gaps
        configured_chips = dict()
        if n_cpus_per_chip is None:
            for (eth_x, eth_y) in ethernet_chips:
                for (x_y, n_cores) in self._machine.get_xy_cores_by_ethernet(
                        eth_x, eth_y):
                    if x_y not in unused_chips:
                        configured_chips[x_y] = (eth_x, eth_y, n_cores)
        else:
            for (eth_x, eth_y) in ethernet_chips:
                for x_y in self._machine.get_xys_by_ethernet(eth_x, eth_y):
                    if x_y not in unused_chips:
                        configured_chips[x_y] = (eth_x, eth_y, n_cpus_per_chip)

        # for chip in self._unreachable_outgoing_chips:
        #    configured_chips.remove(chip)
        # for chip in self._unreachable_incoming_chips:
        #    configured_chips.remove(chip)

        for x_y in configured_chips:
            x, y = x_y
            if x_y in ethernet_chips:
                new_chip = self._create_chip(
                    x, y, configured_chips, f"127.0.{x}.{y}")
            else:
                new_chip = self._create_chip(x, y, configured_chips)
            self._machine.add_chip(new_chip)

        self._machine.add_spinnaker_links()
        self._machine.add_fpga_links()
        if validate:
            self._machine.validate()

    @property
    def machine(self):
        return self._machine

    def _create_chip(self, x, y, configured_chips, ip_address=None):
        chip_links = self._calculate_links(x, y, configured_chips)
        chip_router = Router(
            chip_links)
        if self._sdram_per_chip is None:
            sdram = SDRAM()
        else:
            sdram = SDRAM(self._sdram_per_chip)

        (eth_x, eth_y, n_cores) = configured_chips[(x, y)]

        down_cores = self._unused_cores.get((x, y), None)
        return Chip(
            x, y, n_cores, chip_router, sdram, eth_x, eth_y,
            ip_address, down_cores=down_cores)

    def _calculate_links(self, x, y, configured_chips):
        """
        Calculate the links needed for a machine structure
        """
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
