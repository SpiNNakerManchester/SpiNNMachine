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
from typing import Optional, TypeAlias

from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY

from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.link_data_objects import FPGALinkData
from spinn_machine.version.version_5 import Version5

logger = FormatAdapter(logging.getLogger(__name__))

_FpgaLinkKey: TypeAlias = tuple[str | XY, int, int]


class FPGALinks(object):
    """
    Represents the FPGA links associated with the Machine

    The use case is
    fpga_links = View.get_fpga_links()
    fpga_links.get_fpga_link_with_id
    This requires a Machine to exist or be creatable


    A fail fast test to see if FPGA links are supported is
    FPGALinks.get_fpga_version()
    This call works as soon as cfg data read in. No Machine needed.
    """

    __slots__ = (
        "_fpga_links")

    @staticmethod
    def get_fpga_version() -> Version5:
        """
        Checks the version supports FPGA links

        :return: A Version that supports FPGA links
        :raises SpinnMachineException: If FPGA links not supported
         """
        version = MachineDataView.get_machine_version()
        if isinstance(version, Version5):
            return version
        else:
            raise SpinnMachineException(
                f"{version=} does not support FPGA links")

    def __init__(self) -> None:
        version = self.get_fpga_version()
        self._fpga_links: dict[_FpgaLinkKey, FPGALinkData] = dict()

        machine = MachineDataView.get_machine()
        for ethernet in machine._ethernet_connected_chips:
            ip = ethernet.ip_address
            assert ip is not None
            for (local_x, local_y, link, fpga_id, fpga_link) in \
                    version.fpga_links():
                global_x, global_y = machine.get_global_xy(
                    local_x, local_y, ethernet.x, ethernet.y)
                chip = machine.get_chip_at(global_x, global_y)
                if chip is not None:
                    self._add_fpga_link(fpga_id, fpga_link, chip.x, chip.y,
                                        link, ip, ethernet.x, ethernet.y)

    def _add_fpga_link(
            self, fpga_id: int, fpga_link: int, x: int, y: int, link: int,
            board_address: str, ex: int, ey: int) -> None:
        link_data = FPGALinkData(
            fpga_link_id=fpga_link, fpga_id=fpga_id,
            connected_chip_x=x, connected_chip_y=y,
            connected_link=link, board_address=board_address)
        self._fpga_links[board_address, fpga_id, fpga_link] = link_data
        # Add for the exact chip coordinates
        self._fpga_links[(x, y), fpga_id, fpga_link] = link_data
        # Add for the Ethernet chip coordinates to allow this to work too
        self._fpga_links[(ex, ey), fpga_id, fpga_link] = link_data

    @staticmethod
    def _next_fpga_link(fpga_id: int, fpga_link: int) -> tuple[int, int]:
        if fpga_link == 15:
            return fpga_id + 1, 0
        return fpga_id, fpga_link + 1

    def get_fpga_link_with_id(
            self, fpga_id: int, fpga_link_id: int,
            board_address: Optional[str] = None,
            chip_coords: Optional[XY] = None) -> FPGALinkData:
        """
        Get an FPGA link data item that corresponds to the FPGA and FPGA
        link for a given board address.

        :param fpga_id:
            the ID of the FPGA that the data is going through.  Refer to
            technical document located here for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :param fpga_link_id:
            the link ID of the FPGA. Refer to technical document located here
            for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :param board_address:
            optional board address that this FPGA link is associated with.
            This is ignored if chip_coords is not `None`.
            If this is `None` and chip_coords is `None`, the boot board will be
            assumed.
        :param chip_coords:
            optional chip coordinates that this FPGA link is associated with.
            If this is `None` and board_address is `None`, the boot board
            will be assumed.
        :return: the given FPGA link object
        """
        # Try chip coordinates first
        if chip_coords is not None:
            if board_address is not None:
                logger.warning(
                    "Board address will be ignored because chip coordinates"
                    " are specified")
            c_key = (chip_coords, fpga_id, fpga_link_id)
            link_data = self._fpga_links.get(c_key, None)
            if link_data is not None:
                return link_data
            machine = MachineDataView.get_machine()
            x, y = chip_coords
            if not machine.is_chip_at(x, y):
                raise KeyError(f"No chip {x=} {y=} found!")
            raise KeyError(
                f"FPGA {fpga_id}, link {fpga_link_id} not found"
                f" on chip {chip_coords}")

        # Otherwise try board address
        machine = MachineDataView.get_machine()
        if board_address is None:
            board_address = machine.boot_chip.ip_address
            assert board_address is not None
        b_key = (board_address, fpga_id, fpga_link_id)
        if b_key not in self._fpga_links:
            raise KeyError(
                f"FPGA Link {fpga_id}:{fpga_link_id} does not exist on board"
                f" {board_address}")
        return self._fpga_links[b_key]

    @property
    def n_fpga_links(self) -> int:
        """
        The number of FPGA links in the machine.
        """
        return len(self._fpga_links)

    def __str__(self) -> str:
        return f"{self.n_fpga_links} FPGA Links"

    def __repr__(self) -> str:
        return self.__str__()
