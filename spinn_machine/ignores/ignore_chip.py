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


class IgnoreChip(object):
    """ Represents a chip to be ignored when building a machine. This is \
        typically because it has a fault in the SpiNNaker router.
    """

    __slots__ = ["x", "y", "ip_address"]

    def __init__(self, x, y, ip_address=None):
        """
        :param x: X coordinate of a Chip to ignore
        :type x: int or str
        :param y: Y coordinate of a Chip to ignore
        :type y: int or str
        :param ip_address: Optional IP address which, if provided, make
            x and y local coordinates
        :type ip_address: str or None
        """
        #: X coordinate of the chip to ignore
        self.x = int(x)
        #: Y coordinate of the chip to ignore
        self.y = int(y)
        #: IP address of the board with the chip; if not ``None``, the
        #: coordinates are local to that board
        self.ip_address = ip_address

    @staticmethod
    def parse_single_string(downed_chip):
        """ Converts a string into an :py:class:`IgnoreChip` object

        The supported format is::

            <down_chip_id> = <chip_x>,<chip_y>[,<ip>]

        where:

        * ``<chip_x>`` is the x-coordinate of a down chip
        * ``<chip_x>`` is the y-coordinate of a down chip
        * ``<ip>`` is an *optional* IP address in the ``127.0.0.0`` format.
          If provided, the ``<chip_x>,<chip_y>`` will be considered local to
          the board with this IP address.

        Two examples::

            4,7
            6,5,10.11.12.13

        :param str downed_chip: representation of one chip to ignore
        :return: An IgnoreChip Object
        :rtype: IgnoreChip
        """
        parts = downed_chip.split(",")

        if len(parts) == 2:
            return IgnoreChip(parts[0], parts[1])
        elif len(parts) == 3:
            return IgnoreChip(parts[0], parts[1], parts[2])
        else:
            raise Exception(
                "Unexpected downed_chip: {}".format(downed_chip))

    @staticmethod
    def parse_string(downed_chips):
        """ Converts a string into a (possibly empty) set of \
            :py:class:`IgnoreChip` objects

        format is::

            down_chips = <down_chip_id>[:<down_chip_id]*
            <down_chip_id> = <chip_x>,<chip_y>[,<ip>]

        where:

        * ``<chip_x>`` is the x-coordinate of a down chip
        * ``<chip_y>`` is the y-coordinate of a down chip
        * ``<ip>`` is an *optional** IP address in the ``127.0.0.0`` format.
          If provided, the ``<chip_x>,<chip_y>`` will be considered local to
          the board with this IP address.

        The string ``None`` (case-insensitive) is used to represent no ignores

        An example::

            4,7:6,5,10.11.12.13

        :param str downed_chips: representation of zero or chips to ignore
        :return: Set (possibly empty) of IgnoreChips
        :rtype: set(IgnoreChip)
        """
        ignored_chips = set()
        if downed_chips is None:
            return ignored_chips
        if downed_chips.lower() == "none":
            return ignored_chips
        for downed_chip in downed_chips.split(":"):
            ignored_chips.add(IgnoreChip.parse_single_string(downed_chip))
        return ignored_chips
