# Copyright (c) 2019 The University of Manchester
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

from .machine import Machine
from spinn_utilities.overrides import overrides


class NoWrapMachine(Machine):
    # pylint: disable=useless-super-delegation
    def __init__(self, width, height, chips=None, origin=None):
        """ Creates an machine without wrap-arounds.

        :param width: The width of the machine excluding any virtual chips
        :param height: The height of the machine excluding any virtual chips
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`~spinn_machine.Chip`
        :param origin: Extra information about how this mnachine was created \
            to be used in the str method. Example "Virtual" or "Json"
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """
        super(NoWrapMachine, self).__init__(width, height, chips, origin)

    @overrides(Machine.multiple_48_chip_boards)
    def multiple_48_chip_boards(self):
        return (self._width - 4) % 12 == 0 and (self._height - 4) % 12 == 0

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            yield (x + ethernet_x, y + ethernet_y)

    @overrides(Machine.get_xy_cores_by_ethernet)
    def get_xy_cores_by_ethernet(self, ethernet_x, ethernet_y):
        if (self._width == self._height == 8) or \
                self.multiple_48_chip_boards():
            for (x, y), n_cores in self.CHIPS_PER_BOARD.items():
                # if ethernet_x/y != 0 GIGO mode so ignore ethernet
                yield ((x + ethernet_x, y + ethernet_y), n_cores)
        else:
            # covers weird sizes
            n_cores = Machine.max_cores_per_chip()
            for (x, y) in self._local_xys:
                yield((x, y), n_cores)

    @overrides(Machine.get_chips_by_ethernet)
    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (x + ethernet_x, y + ethernet_y)
            if (chip_xy) in self._chips:
                yield self._chips[chip_xy]

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (x + ethernet_x, y + ethernet_y)
            if (chip_xy) in self._chips:
                yield chip_xy

    @overrides(Machine.get_down_xys_by_ethernet)
    def get_down_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = ((x + ethernet_x),
                       (y + ethernet_y))
            if (chip_xy) not in self._chips:
                yield chip_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = x + add_x
        link_y = y + add_y
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip):
        local_x = chip.x - chip.nearest_ethernet_x
        local_y = chip.y - chip.nearest_ethernet_y
        return local_x, local_y

    @overrides(Machine.get_global_xy)
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        global_x = local_x + ethernet_x
        global_y = local_y + ethernet_y
        return global_x, global_y

    @overrides(Machine.get_vector_length)
    def get_vector_length(self, source, destination):
        x = destination[0] - source[0]
        y = destination[1] - source[1]

        # When vectors are minimised, (1,1,1) is added or subtracted from them.
        # This process does not change the range of numbers in the vector.
        # When a vector is minimal,
        # it is easy to see that the range of numbers gives the
        # magnitude since there are at most two non-zero numbers (with opposite
        # signs) and the sum of their magnitudes will also be their range.
        #
        # Though ideally this code would be written::
        #
        #     >>> return max(x, y, z) - min(x, y, z)

        # This can be farther optimised with then knowledge that z is always 0
        # An x and y having the samne sign they can be replaced with a z
        #     IE: Replace a North and an East with a NorthEast
        # So the length is the greater absolutule value of x or y
        # If the are opossite use the sum of the absolute values

        if x > 0:
            if y > 0:
                # the greater abs
                if x > y:
                    return x
                else:
                    return y
            else:
                # abs(positve x) + abs(negative y)
                return x - y
        else:
            if y > 0:
                return y - x
            else:
                # the greater abs
                if x > y:
                    return - y
                else:
                    return - x

    @overrides(Machine.get_vector)
    def get_vector(self, source, destination):
        return self._minimize_vector(
            destination[0]-source[0], destination[1]-source[1])

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "NoWrap"
