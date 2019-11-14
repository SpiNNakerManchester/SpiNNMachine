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

    __slots__ = ["x", "y", "ip_address"]

    def __init__(self, x, y, ip_address=None):
        """

        :param x: X coorridate of a Chip to ignore
        :type x: int or str
        :param y: Y coorridate of a Chip to ignore
        :type y: int or str
        :param ip_address: Optional ip_address which if provided make\
            x and y local coordinates
        :type ip_address: str or None
        """
        self.x = int(x)
        self.y = int(y)
        self.ip_address = ip_address

    @staticmethod
    def parse_single_string(downed_chip):
        """
        Converts a Sting into an IgnoreChip object

        format is:
            <down_chip_id> = <chip_x>,<chip_y>[,<ip>]
        where:
            <chip_x> is the x-coordinate of a down chip
            <chip_x> is the y-coordinate of a down chip
            <ip> is an OPTIONAL ip address in the 127.0.0.0 format.
        If provided the <chip_x> <chip_y> will be considered local to the\
            board with this ip address

        :param downed_chip: String representation of one chip to ignore
        :type downed_chip: str
        :return: An IgnoreChip Object
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
        """
        Converts a Sting into a (possibly empty) set of IgnoreChip objects

        format is:
            down_chips = <down_chip_id>[:<down_chip_id]*
            <down_chip_id> = <chip_x>,<chip_y>[,<ip>]
        where:
            <chip_x> is the x-coordinate of a down chip
            <chip_x> is the y-coordinate of a down chip
            <ip> is an OPTIONAL ip address in the 127.0.0.0 format.
        If provided the <chip_x> <chip_y> will be considered local to the\
        board with this ip address

        The string None (case insentitive) is used to represent no ignores

        :param downed_chips: String representation of zero or chips to ignore
        :type downed_chips: str
        :return:  Set (possibly empty) of IgnoreChips
        """
        ignored_chips = set()
        if downed_chips is None:
            return ignored_chips
        if downed_chips.lower() == "none":
            return ignored_chips
        for downed_chip in downed_chips.split(":"):
            ignored_chips.add(IgnoreChip.parse_single_string(downed_chip))
        return ignored_chips
