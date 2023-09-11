# Copyright (c) 2015 The University of Manchester
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


class AbstractLinkData(object):
    """
    Data object for SpiNNaker links.
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
        """
        The IP address of the board that this link data is about.
        """
        return self._board_address

    @property
    def connected_chip_x(self):
        """
        The X coordinate of the chip on the board that the link is
        connected to.
        """
        return self._connected_chip_x

    @property
    def connected_chip_y(self):
        """
        The Y coordinate of the chip on the board that the link is
        connected to.
        """
        return self._connected_chip_y

    @property
    def connected_link(self):
        """
        The ID of the link on the source chip that this is data about.
        """
        return self._connected_link
