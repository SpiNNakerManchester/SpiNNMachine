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


class AbstractTag(object):
    """
    Common properties of SpiNNaker IP tags and reverse IP tags.
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
        """
        The board address of the tag.
        """
        return self._board_address

    @property
    def tag(self):
        """
        The tag ID of the tag.
        """
        return self._tag

    @property
    def port(self):
        """
        The port of the tag.
        """
        return self._port

    @port.setter
    def port(self, port):
        """
        Set the port; will fail if the port is already set.
        """
        if self._port is not None:
            raise RuntimeError("Port cannot be set more than once")
        self._port = port
