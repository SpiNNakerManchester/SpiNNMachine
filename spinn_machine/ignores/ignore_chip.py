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


class IgnoreChip(object):
    """
    Represents a chip to be ignored when building a machine. This is
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
        """
        Converts a string into an :py:class:`IgnoreChip` object.

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
            raise ValueError(
                f"Unexpected downed_chip: {downed_chip}")

    @staticmethod
    def parse_string(downed_chips):
        """
        Converts a string into a (possibly empty) set of
        :py:class:`IgnoreChip` objects.

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
