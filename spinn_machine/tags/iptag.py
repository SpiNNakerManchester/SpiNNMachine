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

from .abstract_tag import AbstractTag


class IPTag(AbstractTag):
    """
    Used to hold data that is contained within an IP tag.
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
        """
        The IP address to which SDP packets with this tag will be sent.
        """
        return self._ip_address

    @property
    def strip_sdp(self):
        """
        Whether the SDP header is to be stripped.
        """
        return self._strip_sdp

    @property
    def traffic_identifier(self):
        """
        The identifier of traffic using this tag.
        """
        return self._traffic_identifier

    @property
    def destination_x(self):
        """
        The X-coordinate where users of this tag should send packets to.
        """
        return self._destination_x

    @property
    def destination_y(self):
        """
        The Y-coordinate where users of this tag should send packets to.
        """
        return self._destination_y

    def __repr__(self):
        return (
            f"IPTag(board_address={self.board_address}, "
            f"destination_x={self.destination_x}, "
            f"destination_y={self.destination_y},"
            f" tag={self.tag}, port={self.port}, "
            f"ip_address={self.ip_address}, strip_sdp={self.strip_sdp}, "
            f"traffic_identifier={self.traffic_identifier})")

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
