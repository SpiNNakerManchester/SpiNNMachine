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


class IPTag(AbstractTag):
    """ Used to hold data that is contained within an IP tag
    """

    __slots__ = [
        "_ip_address",
        # Indicates whether the SDP header should be removed
        "_strip_sdp",
        "_traffic_identifier",
        "_destination_x",
        "_destination_y"
    ]

    # pylint: disable=too-many-arguments
    def __init__(
            self, board_address, destination_x, destination_y, tag, ip_address,
            port=None, strip_sdp=False, traffic_identifier="DEFAULT"):
        """
        :param board_address:
            The IP address of the board on which the tag is allocated
        :type board_address: str or None
        :param int destination_x:
            The x-coordinate where users of this tag should send packets to
        :param int destination_y:
            The y-coordinate where users of this tag should send packets to
        :param int tag: The tag of the SDP packet
        :param str ip_address:
            The IP address to which SDP packets with the tag will be sent
        :param port:
            The port to which the SDP packets with the tag will be sent, or
            ``None`` if not yet assigned
        :type port: int or None
        :param bool strip_sdp:
            Indicates whether the SDP header should be removed
        :param str traffic_identifier:
            The identifier for traffic transmitted using this tag
        """
        super().__init__(board_address, tag, port)
        self._ip_address = ip_address
        self._strip_sdp = strip_sdp
        self._traffic_identifier = traffic_identifier
        self._destination_x = destination_x
        self._destination_y = destination_y

    @property
    def ip_address(self):
        """ The IP address to which SDP packets with this tag will be sent.
        """
        return self._ip_address

    @property
    def strip_sdp(self):
        """ Return if the SDP header is to be stripped
        """
        return self._strip_sdp

    @property
    def traffic_identifier(self):
        """ The identifier of traffic using this tag
        """
        return self._traffic_identifier

    @property
    def destination_x(self):
        """ The x-coordinate where users of this tag should send packets to
        """
        return self._destination_x

    @property
    def destination_y(self):
        """ The y-coordinate where users of this tag should send packets to
        """
        return self._destination_y

    def __repr__(self):
        return (
            "IPTag(board_address={}, destination_x={}, destination_y={},"
            " tag={}, port={}, ip_address={}, strip_sdp={},"
            " traffic_identifier={})".format(
                self.board_address, self.destination_x, self.destination_y,
                self.tag, self.port, self.ip_address, self.strip_sdp,
                self.traffic_identifier))

    def __eq__(self, other):
        if not isinstance(other, IPTag):
            return False
        return (self._ip_address == other.ip_address and
                self._strip_sdp == other.strip_sdp and
                self._board_address == other.board_address and
                self._port == other.port and
                self._tag == other.tag and
                self._traffic_identifier == other.traffic_identifier)

    def __hash__(self):
        return hash((self._ip_address, self._strip_sdp, self._board_address,
                     self._port, self._tag, self._traffic_identifier))

    def __ne__(self, other):
        return not self.__eq__(other)
