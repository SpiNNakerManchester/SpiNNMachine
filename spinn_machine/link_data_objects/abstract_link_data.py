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


class AbstractLinkData(object):
    """ Data object for SpiNNaker links
    """

    __slots__ = (
        "_board_address",
        "_connected_chip_x",
        "_connected_chip_y",
        "_connected_link"
    )

    def __init__(self, connected_chip_x, connected_chip_y, connected_link,
                 board_address):
        self._board_address = board_address
        self._connected_chip_x = connected_chip_x
        self._connected_chip_y = connected_chip_y
        self._connected_link = connected_link

    @property
    def board_address(self):
        """ The IP address of the board that this link data is about.
        """
        return self._board_address

    @property
    def connected_chip_x(self):
        """ The X coordinate of the chip on the board that the link is\
            connected to.
        """
        return self._connected_chip_x

    @property
    def connected_chip_y(self):
        """ The Y coordinate of the chip on the board that the link is\
            connected to.
        """
        return self._connected_chip_y

    @property
    def connected_link(self):
        """ The ID of the link on the source chip that this is data about.
        """
        return self._connected_link
