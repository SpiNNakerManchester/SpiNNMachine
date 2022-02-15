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

from spinn_utilities.overrides import overrides
from .machine import Machine


class FullWrapMachine(Machine):
    # pylint: disable=useless-super-delegation

    def __init__(self, width, height, chips=None, origin=None):
        """ Creates a fully wrapped machine.

        :param int width: The width of the machine excluding any virtual chips
        :param int height:
            The height of the machine excluding any virtual chips
        :param chips: An iterable of chips in the machine
        :type chips: iterable(~spinn_machine.Chip)
        :param str origin: Extra information about how this machine was
            created to be used in the str method. Example "Virtual" or "Json"
        :raise ~spinn_machine.exceptions.SpinnMachineAlreadyExistsException:
            If any two chips have the same x and y coordinates
        """
        super().__init__(width, height, chips, origin)

    @overrides(Machine.multiple_48_chip_boards)
    def multiple_48_chip_boards(self):
        return self._width % 12 == 0 and self._height % 12 == 0

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_x = (x + ethernet_x) % self._width
            chip_y = (y + ethernet_y) % self._height
            yield (chip_x, chip_y)

    @overrides(Machine.get_xy_cores_by_ethernet)
    def get_xy_cores_by_ethernet(self, ethernet_x, ethernet_y):
        if (self._width == self._height == 2):
            n_cores = Machine.max_cores_per_chip()
            for (x, y) in self._local_xys:
                # if ethernet_x/y != 0 GIGO mode so ignore ethernet
                yield (x, y), n_cores
        else:
            for (x, y), n_cores in self.CHIPS_PER_BOARD.items():
                yield(((x + ethernet_x) % self._width,
                      (y + ethernet_y) % self._height), n_cores)

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = ((x + ethernet_x) % self._width,
                       (y + ethernet_y) % self._height)
            if chip_xy in self._chips and\
                    chip_xy not in self._virtual_chips:
                yield chip_xy

    @overrides(Machine.get_down_xys_by_ethernet)
    def get_down_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = ((x + ethernet_x) % self._width,
                       (y + ethernet_y) % self._height)
            if (chip_xy) not in self._chips:
                yield chip_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = (x + add_x + self._width) % self._width
        link_y = (y + add_y + self.height) % self.height
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip):
        local_x = ((chip.x - chip.nearest_ethernet_x + self._width)
                   % self._width)
        local_y = ((chip.y - chip.nearest_ethernet_y + self._height)
                   % self._height)
        return local_x, local_y

    @overrides(Machine.get_global_xy)
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        global_x = (local_x + ethernet_x) % self._width
        global_y = (local_y + ethernet_y) % self._height
        return global_x, global_y

    @overrides(Machine.get_vector_length)
    def get_vector_length(self, source, destination):
        # Aliases for convenience
        w, h = self._width, self._height

        x_up = (destination[0] - source[0]) % w
        x_down = x_up - w
        y_right = (destination[1] - source[1]) % h
        y_left = y_right - h

        # Both possitve so greater
        length = x_up if x_up > y_right else y_right

        # negative x possitive y so sum of abs
        negative_x = y_right - x_down
        if negative_x < length:
            length = negative_x

        # possitive x negative Y so sum of abs
        negative_y = x_up - y_left
        if negative_y < length:
            length = negative_y

        # both negative so abs smaller (farthest from zero)
        if x_down > y_left:
            negative_xy = - y_left
        else:
            negative_xy = - x_down
        if negative_xy < length:
            return negative_xy
        else:
            return length

    def get_vector(self, source, destination):
        # Aliases for convenience
        w, h = self._width, self._height

        x_up = (destination[0] - source[0]) % w
        x_down = x_up - w
        y_right = (destination[1] - source[1]) % h
        y_left = y_right - h

        # Both possitve so greater
        length = x_up if x_up > y_right else y_right
        dx = x_up
        dy = y_right

        # negative x possitive y so sum of abs
        negative_x = y_right - x_down
        if negative_x < length:
            length = negative_x
            dx = x_down

        # possitive x negative Y so sum of abs
        negative_y = x_up - y_left
        if negative_y < length:
            length = negative_y
            dx = x_up
            dy = y_left

        # both negative so abs smaller (farthest from zero)
        if x_down > y_left:
            negative_xy = - y_left
        else:
            negative_xy = - x_down
        if negative_xy < length:
            return self._minimize_vector(x_down, y_left)
        else:
            return self._minimize_vector(dx, dy)

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "Wrapped"
