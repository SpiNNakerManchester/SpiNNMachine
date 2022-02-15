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

from .abstract_tag import AbstractTag


class ReverseIPTag(AbstractTag):
    """ Used to hold data that is contained within a Reverse IP tag
    """

    __slots__ = [
        "_destination_x",
        "_destination_y",
        "_destination_p",
        "_sdp_port"
    ]

    # pylint: disable=too-many-arguments
    def __init__(self, board_address, tag, port, destination_x, destination_y,
                 destination_p, sdp_port=1):
        """
        :param board_address:
            The IP address of the board on which the tag is allocated
        :type board_address: str or None
        :param int tag: The tag of the SDP packet
        :param int port:
            The UDP port on which SpiNNaker will listen for packets
        :param int destination_x:
            The x-coordinate of the chip to send packets to
        :param int destination_y:
            The y-coordinate of the chip to send packets to
        :param int destination_p: The ID of the processor to send packets to
        :param int sdp_port:
            The optional port number to use for SDP packets that
            are formed on the machine (default is 1)
        """
        super().__init__(board_address, tag, port)
        self._destination_x = destination_x
        self._destination_y = destination_y
        self._destination_p = destination_p
        self._sdp_port = sdp_port

    @property
    def sdp_port(self):
        """ The SDP port number of the tag that these packets are to be\
            received on for the processor.
        """
        return self._sdp_port

    @property
    def destination_x(self):
        """ The destination x coordinate of a chip in the SpiNNaker machine\
            that packets should be sent to for this reverse IP tag.
        """
        return self._destination_x

    @property
    def destination_y(self):
        """ The destination y coordinate of a chip in the SpiNNaker machine\
            that packets should be sent to for this reverse IP tag.
        """
        return self._destination_y

    @property
    def destination_p(self):
        """ The destination processor ID for the chip at (x,y) that packets\
            should be send to for this reverse IP tag
        """
        return self._destination_p

    def __repr__(self):
        return (
            "ReverseIPTag(board_address={}, tag={}, port={}, destination_x={},"
            " destination_y={}, destination_p={}, sdp_port={})".format(
                self._board_address, self._tag, self._port,
                self._destination_x, self._destination_y,
                self._destination_p, self._sdp_port))
