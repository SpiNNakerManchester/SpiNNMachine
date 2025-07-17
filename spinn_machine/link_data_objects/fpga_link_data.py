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

from .abstract_link_data import AbstractLinkData


class FPGALinkData(AbstractLinkData):
    """
    Data object for FPGA links.
    """

    __slots__ = (
        "_fpga_link_id",
        "_fpga_id")

    def __init__(self, fpga_link_id: int, fpga_id: int, connected_chip_x: int,
                 connected_chip_y: int, connected_link: int,
                 board_address: str):
        """
        :param fpga_link_id: The ID of the link out of the SpiNNaker FPGA.
        :param fpga_id: The ID of the SpiNNaker FPGA.
        :param connected_chip_x:
            The X coordinate of the chip on the board that the link is
            connected to.
        :param connected_chip_y:
            The Y coordinate of the chip on the board that the link is
            connected to.
        :param connected_link:
            The ID of the link on the source chip that this is data about.
        :param board_address:
            The IP address of the board that this link data is about.
        """
        super().__init__(
            connected_chip_x, connected_chip_y, connected_link, board_address)
        self._fpga_link_id = fpga_link_id
        self._fpga_id = fpga_id

    @property
    def fpga_link_id(self) -> int:
        """
        The ID of the link out of the SpiNNaker FPGA.
        """
        return self._fpga_link_id

    @property
    def fpga_id(self) -> int:
        """
        The ID of the SpiNNaker FPGA.
        """
        return self._fpga_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FPGALinkData):
            return False
        return (self._fpga_id == other.fpga_id and
                self._fpga_link_id == other.fpga_link_id and
                self.connected_chip_x == other.connected_chip_x and
                self.connected_chip_y == other.connected_chip_y and
                self.connected_link == other.connected_link and
                self.board_address == other.board_address)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, FPGALinkData):
            return True
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self._fpga_id, self._fpga_link_id,
                     self.connected_chip_x, self.connected_chip_y,
                     self.connected_link, self.board_address))
