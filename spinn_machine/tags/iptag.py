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

from typing import Any
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

    def __init__(
            self, board_address: str, destination_x: int,
            destination_y: int, tag: int, ip_address: str,
            port: int, strip_sdp: bool = False,
            traffic_identifier: str = "DEFAULT"):
        """
        :param board_address:
            The IP address of the board on which the tag is allocated
        :param destination_x:
            The x-coordinate where users of this tag should send packets to
        :param destination_y:
            The y-coordinate where users of this tag should send packets to
        :param tag: The tag of the SDP packet
        :param ip_address:
            The IP address to which SDP packets with the tag will be sent
        :param port:
            The port to which the SDP packets with the tag will be sent, or
        :param strip_sdp:
            Indicates whether the SDP header should be removed
        :param traffic_identifier:
            The identifier for traffic transmitted using this tag
        """
        super().__init__(board_address, tag, port)
        self._ip_address = ip_address
        self._strip_sdp = strip_sdp
        self._traffic_identifier = traffic_identifier
        self._destination_x = destination_x
        self._destination_y = destination_y

    @property
    def ip_address(self) -> str:
        """
        The IP address to which SDP packets with this tag will be sent.
        """
        return self._ip_address

    @property
    def strip_sdp(self) -> bool:
        """
        Whether the SDP header is to be stripped.
        """
        return self._strip_sdp

    @property
    def traffic_identifier(self) -> str:
        """
        The identifier of traffic using this tag.
        """
        return self._traffic_identifier

    @property
    def destination_x(self) -> int:
        """
        The X-coordinate where users of this tag should send packets to.
        """
        return self._destination_x

    @property
    def destination_y(self) -> int:
        """
        The Y-coordinate where users of this tag should send packets to.
        """
        return self._destination_y

    def __repr__(self) -> str:
        return (
            f"IPTag(board_address={self.board_address}, "
            f"destination_x={self.destination_x}, "
            f"destination_y={self.destination_y},"
            f" tag={self.tag}, port={self.port}, "
            f"ip_address={self.ip_address}, strip_sdp={self.strip_sdp}, "
            f"traffic_identifier={self.traffic_identifier})")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IPTag):
            return False
        return (self._ip_address == other.ip_address and
                self._strip_sdp == other.strip_sdp and
                self._board_address == other.board_address and
                self._port == other.port and
                self._tag == other.tag and
                self._traffic_identifier == other.traffic_identifier)

    def __hash__(self) -> int:
        return hash((self._ip_address, self._strip_sdp, self._board_address,
                     self._port, self._tag, self._traffic_identifier))

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)
