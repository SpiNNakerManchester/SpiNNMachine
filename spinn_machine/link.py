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
        "_source_y")

    def __init__(
            self, source_x: int, source_y: int, source_link_id: int,
            destination_x: int, destination_y: int):
        """
        :param source_x: The x-coordinate of the source chip of the link
        :param source_y: The y-coordinate of the source chip of the link
        :param source_link_id: The ID of the link in the source chip
        :param destination_x:
            The x-coordinate of the destination chip of the link
        :param destination_y:
            The y-coordinate of the destination chip of the link
        """
        self._source_x = source_x
        self._source_y = source_y
        self._source_link_id = source_link_id
        self._destination_x = destination_x
        self._destination_y = destination_y

    @property
    def source_x(self) -> int:
        """
        The X-coordinate of the source chip of this link.
        """
        return self._source_x

    @property
    def source_y(self) -> int:
        """
        The Y-coordinate of the source chip of this link.
        """
        return self._source_y

    @property
    def source_link_id(self) -> int:
        """
        The ID of the link on the source chip.
        """
        return self._source_link_id

    @property
    def destination_x(self) -> int:
        """
        The X-coordinate of the destination chip of this link.
        """
        return self._destination_x

    @property
    def destination_y(self) -> int:
        """
        The Y-coordinate of the destination chip of this link.
        """
        return self._destination_y

    def __str__(self) -> str:
        return (
            f"[Link: source_x={self._source_x}, source_y={self._source_y}, "
            f"source_link_id={self._source_link_id}, "
            f"destination_x={self._destination_x}, "
            f"destination_y={self._destination_y}]")

    def __repr__(self) -> str:
        return self.__str__()
