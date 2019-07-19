# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .abstract_link_data import AbstractLinkData


class FPGALinkData(AbstractLinkData):
    """ Data object for FPGA links
    """

    __slots__ = (
        "_fpga_link_id",
        "_fpga_id"
    )

    # pylint: disable=too-many-arguments
    def __init__(self, fpga_link_id, fpga_id, connected_chip_x,
                 connected_chip_y, connected_link, board_address):
        super(FPGALinkData, self).__init__(
            connected_chip_x, connected_chip_y, connected_link, board_address)
        self._fpga_link_id = fpga_link_id
        self._fpga_id = fpga_id

    @property
    def fpga_link_id(self):
        """ The ID of the link out of the SpiNNaker FPGA.
        """
        return self._fpga_link_id

    @property
    def fpga_id(self):
        """ The ID of the SpiNNaker FPGA.
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
