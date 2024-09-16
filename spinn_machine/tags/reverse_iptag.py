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


class ReverseIPTag(AbstractTag):
    """
    Used to hold data that is contained within a Reverse IP tag.
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
        """
        The SDP port number of the tag that these packets are to be
        received on for the processor.
        """
        return self._sdp_port

    @property
    def destination_x(self):
        """
        The destination x coordinate of a chip in the SpiNNaker machine
        that packets should be sent to for this reverse IP tag.
        """
        return self._destination_x

    @property
    def destination_y(self):
        """
        The destination y coordinate of a chip in the SpiNNaker machine
        that packets should be sent to for this reverse IP tag.
        """
        return self._destination_y

    @property
    def destination_p(self):
        """
        The destination processor ID for the chip at (x,y) that packets
        should be send to for this reverse IP tag.
        """
        return self._destination_p

    def __repr__(self):
        return (
            f"ReverseIPTag(board_address={self._board_address}, "
            f"tag={self._tag}, port={self._port}, "
            f"destination_x={self._destination_x}, "
            f"destination_y={self._destination_y}, "
            f"destination_p={self._destination_p}, sdp_port={self._sdp_port})")
