# Copyright (c) 2014 The University of Manchester
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

"""
a Link in a SpiNNaker machine
"""


class Link(object):
    """
    Represents a directional link between SpiNNaker chips in the machine.
    """

    __slots__ = (
        "_destination_x", "_destination_y", "_source_link_id", "_source_x",
        "_source_y"
    )

    # pylint: disable=too-many-arguments
    def __init__(self, source_x, source_y, source_link_id, destination_x,
                 destination_y):
        """
        :param int source_x: The x-coordinate of the source chip of the link
        :param int source_y: The y-coordinate of the source chip of the link
        :param int source_link_id: The ID of the link in the source chip
        :param int destination_x:
            The x-coordinate of the destination chip of the link
        :param int destination_y:
            The y-coordinate of the destination chip of the link
        """
        self._source_x = source_x
        self._source_y = source_y
        self._source_link_id = source_link_id
        self._destination_x = destination_x
        self._destination_y = destination_y

    @property
    def source_x(self):
        """
        The X-coordinate of the source chip of this link.

        :rtype: int
        """
        return self._source_x

    @property
    def source_y(self):
        """
        The Y-coordinate of the source chip of this link.

        :rtype: int
        """
        return self._source_y

    @property
    def source_link_id(self):
        """
        The ID of the link on the source chip.

        :rtype: int
        """
        return self._source_link_id

    @property
    def destination_x(self):
        """
        The X-coordinate of the destination chip of this link.

        :rtype: int
        """
        return self._destination_x

    @property
    def destination_y(self):
        """
        The Y-coordinate of the destination chip of this link.

        :rtype: int
        """
        return self._destination_y

    def __str__(self):
        return (
            f"[Link: source_x={self._source_x}, source_y={self._source_y}, "
            f"source_link_id={self._source_link_id}, "
            f"destination_x={self._destination_x}, "
            f"destination_y={self._destination_y}]")

    def __repr__(self):
        return self.__str__()
