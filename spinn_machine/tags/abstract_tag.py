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


class AbstractTag(object):
    """ Common properties of SpiNNaker IP tags and reverse IP tags.
    """

    __slots__ = [
        # the board address associated with this tag
        "_board_address",

        # the tag ID associated with this tag
        "_tag",

        # the port number associated with this tag
        "_port"
    ]

    def __init__(self, board_address, tag, port):
        self._board_address = board_address
        self._tag = tag
        self._port = port

    @property
    def board_address(self):
        """ The board address of the tag
        """
        return self._board_address

    @property
    def tag(self):
        """ The tag ID of the tag
        """
        return self._tag

    @property
    def port(self):
        """ The port of the tag
        """
        return self._port

    @port.setter
    def port(self, port):
        """ Set the port; will fail if the port is already set
        """
        if self._port is not None:
            raise RuntimeError("Port cannot be set more than once")
        self._port = port
