# Copyright (c) 2017 The University of Manchester
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
from typing import Any, Optional, Set, Union
from typing_extensions import TypeAlias
_Intable: TypeAlias = Union[int, str]


class IgnoreLink(object):
    """
    Represents a link that should be ignored when building a machine.
    """

    __slots__ = ["x", "y", "link", "ip_address"]

    def __init__(self, x: _Intable, y: _Intable, link: _Intable,
                 ip_address: Optional[str] = None):
        """
        :param x: X coordinate of a chip with a link to ignore
        :param y: Y coordinate of a chip with a link to ignore
        :param link: ID of the link to ignore
        :param ip_address: Optional IP address which, if provided, makes
            x and y be local coordinates
        """
        #: X coordinate of the chip with the link to ignore
        self.x = int(x)
        #: Y coordinate of the chip with the link to ignore
        self.y = int(y)
        #: Link ID to ignore
        self.link = int(link)
        #: IP address of the board with the chip; if not ``None``, the
        #: coordinates are local to that board
        self.ip_address = ip_address

    @staticmethod
    def parse_single_string(downed_link: str) -> 'IgnoreLink':
        """
        Converts a string into an :py:class:`IgnoreLink` object.

        The format is::

            <down_link> = <chip_x>,<chip_y>,<link_id>[,<ip>]

        where:

        * ``<chip_x>`` is the x-coordinate of a down chip
        * ``<chip_x>`` is the y-coordinate of a down chip
        * ``<link_id>`` is the link ID
        * ``<ip>`` is an *optional* IP address in the ``127.0.0.0`` format.
          If provided, the ``<chip_x>,<chip_y>`` will be considered local to
          the board with this IP address.

        :param downed_link: representation of one link to ignore
        :return: An IgnoreLink object
        """
        parts = downed_link.split(",")

        if len(parts) == 3:
            return IgnoreLink(parts[0], parts[1], parts[2])
        elif len(parts) == 4:
            return IgnoreLink(parts[0], parts[1], parts[2], parts[3])
        else:
            raise ValueError(
                f"Unexpected downed_link: {downed_link}")

    @staticmethod
    def parse_string(downed_links: Optional[str]) -> Set['IgnoreLink']:
        """
        Converts a string into a (possibly empty) set of
        :py:class:`IgnoreLink` objects

        The format is::

            down_links = <down_link_id>[:<down_link_id]*
            <down_link_id> = <chip_x>,<chip_y>,<link_id>[,<ip>]

        where:

        * ``<chip_x>`` is the x-coordinate of a down chip
        * ``<chip_x>`` is the y-coordinate of a down chip
        * ``<link_id>`` is the link ID
        * ``<ip>`` is an *optional* IP address in the ``127.0.0.0`` format.
          If provided, the ``<chip_x>,<chip_y>`` will be considered local to
          the board with this IP address

        The string ``None`` (case insensitive) is used to represent no ignores

        :param downed_links: representation of zero or chips to ignore
        :return: Set (possibly empty) of IgnoreLinks
        """
        ignored_links: Set['IgnoreLink'] = set()
        if downed_links is None:
            return ignored_links
        if downed_links.lower() == "none":
            return ignored_links
        for downed_chip in downed_links.split(":"):
            ignored_links.add(IgnoreLink.parse_single_string(downed_chip))
        return ignored_links

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IgnoreLink):
            return False
        return (self.x == other.x) and (self.y == other.y) and (
            self.link == other.link) and (self.ip_address == other.ip_address)

    def __hash__(self) -> int:
        return (self.x << 16) | (self.y << 8) | self.link
