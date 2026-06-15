# Copyright (c) 2026 The University of Manchester
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

"""
FPGA Links on a SpiNNaker machine
"""
import logging
from typing import Iterator, Optional, TypeAlias, Union

from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY

from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.link_data_objects import SpinnakerLinkData
from spinn_machine.version.version_spin1 import VersionSpin1

logger = FormatAdapter(logging.getLogger(__name__))

_SpinLinkKey: TypeAlias = tuple[str | XY, int]


class SpinnakerLinks(object):
    """
    Represents the spinnaker links associated with the Machine

    The use case is
    spinnaker_links = View.get_fpga_links()
    spinnaker_links.get_fpga_link_with_id
    This requires a Machine to exist or be creatable


    A fail fast test to see if Fpga links are supported is
    FpgaLinks.get_fpga_version()
    This call works as soon as cfg data read in. No Machine needed.
    """

    __slots__ = (
        "_spinnaker_links")

    @staticmethod
    def get_spinnaker_version() -> VersionSpin1:
        """
        Checks the version supports spinnaker links

        :return: A Version that supports Spinnaker links
        :raises SpinnMachineException: If Spinnaker links not supported
         """
        version = MachineDataView.get_machine_version()
        if isinstance(version, VersionSpin1):
            return version
        else:
            raise SpinnMachineException(
                f"{version=} does not support Spinnaker links")

    def __init__(self) -> None:
        version = self.get_spinnaker_version()
        # The dictionary of SpiNNaker links by board address and "ID" (int)
        self._spinnaker_links: dict[_SpinLinkKey, SpinnakerLinkData] = dict()

        machine = MachineDataView.get_machine()
        for ethernet in machine.ethernet_connected_chips:
            ip = ethernet.ip_address
            assert ip is not None
            for (s_id, (local_x, local_y, link)) in enumerate(
                    version.spinnaker_links()):
                global_x, global_y = machine.get_global_xy(
                    local_x, local_y, ethernet.x, ethernet.y)
                chip = machine.get_chip_at(global_x, global_y)
                if chip is not None and not chip.router.is_link(link):
                    self._add_spinnaker_link(
                        s_id, global_x, global_y, link, ip)

    @property
    def spinnaker_links(self) -> Iterator[
            tuple[_SpinLinkKey, SpinnakerLinkData]]:
        """
        The set of SpiNNaker links in the machine.
        """
        return iter(self._spinnaker_links.items())

    def get_spinnaker_link_with_id(
            self, spinnaker_link_id: int, board_address: Optional[str] = None,
            chip_coords: Optional[XY] = None) -> SpinnakerLinkData:
        """
        Get a SpiNNaker link with a given ID.

        :param spinnaker_link_id: The ID of the link
        :param board_address:
            optional board address that this SpiNNaker link is associated with.
            This is ignored if chip_coords is not `None`.
            If this is `None` and chip_coords is `None`,
            the boot board will be assumed.
        :param chip_coords:
            optional chip coordinates that this SpiNNaker link is associated
            with. If this is `None` and board_address is `None`, the boot board
            will be assumed.
        :return: The SpiNNaker link data
        """
        # Try chip coordinates first
        if chip_coords is not None:
            if board_address is not None:
                logger.warning(
                    "Board address will be ignored because chip coordinates"
                    " are specified")
            c_key = (chip_coords, spinnaker_link_id)
            link_data = self._spinnaker_links.get(c_key, None)
            if link_data is not None:
                return link_data
            machine = MachineDataView.get_machine()
            if chip_coords not in machine._chips:
                raise KeyError(f"No chip {chip_coords} found!")
            raise KeyError(
                f"SpiNNaker link {spinnaker_link_id} not found"
                f" on chip {chip_coords}")

        # Otherwise try board address.
        if board_address is None:
            machine = MachineDataView.get_machine()
            board_address = machine.boot_chip.ip_address
            assert board_address is not None
        a_key = (board_address, spinnaker_link_id)
        if a_key not in self._spinnaker_links:
            raise KeyError(
                f"SpiNNaker Link {spinnaker_link_id} does not exist on board"
                f" {board_address}")
        return self._spinnaker_links[a_key]

    def _add_spinnaker_link(
            self, spinnaker_link_id: int, x: int, y: int, link: int,
            board_address: str) -> None:
        link_data = SpinnakerLinkData(
            spinnaker_link_id, x, y, link, board_address)
        self._spinnaker_links[board_address, spinnaker_link_id] = link_data
        self._spinnaker_links[(x, y), spinnaker_link_id] = link_data

    def __str__(self) -> str:
        return f"{len(self._spinnaker_links)} Spinnaker Links"

    def __repr__(self) -> str:
        return self.__str__()
