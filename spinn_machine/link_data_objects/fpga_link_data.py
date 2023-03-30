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
        "_fpga_id"
    )

    # pylint: disable=too-many-arguments
    def __init__(self, fpga_link_id, fpga_id, connected_chip_x,
                 connected_chip_y, connected_link, board_address):
        super().__init__(
            connected_chip_x, connected_chip_y, connected_link, board_address)
        self._fpga_link_id = fpga_link_id
        self._fpga_id = fpga_id

    @property
    def fpga_link_id(self):
        """
        The ID of the link out of the SpiNNaker FPGA.
        """
        return self._fpga_link_id

    @property
    def fpga_id(self):
        """
        The ID of the SpiNNaker FPGA.
        """
        return self._fpga_id

    def __eq__(self, other):
        if not isinstance(other, FPGALinkData):
            return False
        return (self._fpga_id == other.fpga_id and
                self._fpga_link_id == other.fpga_link_id and
                self.connected_chip_x == other.connected_chip_x and
                self.connected_chip_y == other.connected_chip_y and
                self.connected_link == other.connected_link and
                self.board_address == other.board_address)

    def __ne__(self, other):
        if not isinstance(other, FPGALinkData):
            return True
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._fpga_id, self._fpga_link_id,
                     self.connected_chip_x, self.connected_chip_y,
                     self.connected_link, self.board_address))
