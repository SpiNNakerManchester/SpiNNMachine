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

TYPICAL_PHYSICAL_VIRTUAL_MAP = {
    0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 0, 11: 12,
    12: 13, 13: 14, 14: 15, 15: 16, 16: 17, 17: 18}


class IgnoreCore(object):

    __slots__ = ["x", "y", "p", "ip_address"]

    def __init__(self, x, y, p, ip_address=None):
        """

        :param x: X coorridate of a Chip to ignore
        :type x: int or str
        :param y: Y coorridate of a Chip to ignore
        :type y: int or str
        :param p: P The virtual core ID of a core if > 0\
            or the phsical core if <= 0
        :type p: int or str
        :param ip_address: Optional ip_address which if provided make\
            x and y local coordinates
        :type ip_address: str or None
        """
        self.x = int(x)
        self.y = int(y)
        self.p = int(p)
        self.ip_address = ip_address

    @property
    def virtual_p(self):
        if self.p > 0:
            return self.p
        else:
            return TYPICAL_PHYSICAL_VIRTUAL_MAP[0-self.p]

    @staticmethod
    def parse_single_string(downed_core):
        """
        Converts a Sting into an IgnoreChip object

        format is:
            <down_core> = <chip_x>,<chip_y>,<core_id>[,<ip>]
        where:
            <chip_x> is the x-coordinate of a down chip
            <chip_x> is the y-coordinate of a down chip
            <core_id> is the virtual core ID of a core if > 0
            or the phsical core if <= 0
            <ip> is an OPTIONAL ip address in the 127.0.0.0 format.
        If provided the <chip_x> <chip_y> will be considered local to the\
            board with this ip address

        :param downed_core: String representation of one chip to ignore
        :type downed_core: str
        :return: An IgnoreChip Object
        """
        parts = downed_core.split(",")

        if len(parts) == 3:
            return IgnoreCore(parts[0], parts[1], parts[2])
        elif len(parts) == 4:
            return IgnoreCore(parts[0], parts[1], parts[2], parts[3])
        else:
            raise Exception(
                "Unexpected downed_core: {}".format(downed_core))

    @staticmethod
    def parse_string(downed_cores):
        """
        Converts a Sting into a (possibly empty) set of IgnoreChip objects

        format is:
            down_cores = <down_core_id>[:<down_core_id]*
            <down_core_id> = <chip_x>,<chip_y>[,<ip>]
        where:
            <chip_x> is the x-coordinate of a down chip
            <chip_x> is the y-coordinate of a down chip
            <core_id> is the virtual core ID of a core if > 0
            or the phsical core if <= 0
            <ip> is an OPTIONAL ip address in the 127.0.0.0 format.
        If provided the <chip_x> <chip_y> will be considered local to the\
            board with this ip address

        The string None (case insentitive) is used to represent no ignores

        :param downed_cores: String representation of zero or chips to ignore
        :type downed_cores: str
        :return:  Set (possibly empty) of IgnoreChips
        """
        ignored_chips = set()
        if downed_cores is None:
            return ignored_chips
        if downed_cores.lower() == "none":
            return ignored_chips
        for downed_chip in downed_cores.split(":"):
            ignored_chips.add(IgnoreCore.parse_single_string(downed_chip))
        return ignored_chips
