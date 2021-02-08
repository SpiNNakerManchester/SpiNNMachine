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


class IgnoreLink(object):
    """ Represents a link that should be ignored when building a machine.
    """

    __slots__ = ["x", "y", "link", "ip_address"]

    def __init__(self, x, y, link, ip_address=None):
        """
        :param x: X coordinate of a chip with a link to ignore
        :type x: int or str
        :param y: Y coorridate of a chip with a link to ignore
        :type y: int or str
        :param link: ID of the link to ignore
        :type link: int or str
        :param ip_address: Optional IP address which, if provided, makes
            x and y be local coordinates
        :type ip_address: str or None
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
    def parse_single_string(downed_link):
        """ Converts a string into an :py:class:`IgnoreLink` object

        The format is::

            <down_link> = <chip_x>,<chip_y>,<link_id>[,<ip>]

        where:

        * ``<chip_x>`` is the x-coordinate of a down chip
        * ``<chip_x>`` is the y-coordinate of a down chip
        * ``<link_id>`` is the link ID
        * ``<ip>`` is an *optional* IP address in the ``127.0.0.0`` format.
          If provided, the ``<chip_x>,<chip_y>`` will be considered local to
          the board with this IP address.

        :param str downed_link: representation of one link to ignore
        :return: An IgnoreLink object
        :rtype: IgnoreLink
        """
        parts = downed_link.split(",")

        if len(parts) == 3:
            return IgnoreLink(parts[0], parts[1], parts[2])
        elif len(parts) == 4:
            return IgnoreLink(parts[0], parts[1], parts[2], parts[3])
        else:
            raise Exception(
                "Unexpected downed_link: {}".format(downed_link))

    @staticmethod
    def parse_string(downed_links):
        """ Converts a string into a (possibly empty) set of \
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

        :param str downed_cores: representation of zero or chips to ignore
        :return: Set (possibly empty) of IgnoreLinks
        :rtype: set(IgnoreLink)
        """
        ignored_links = set()
        if downed_links is None:
            return ignored_links
        if downed_links.lower() == "none":
            return ignored_links
        for downed_chip in downed_links.split(":"):
            ignored_links.add(IgnoreLink.parse_single_string(downed_chip))
        return ignored_links
