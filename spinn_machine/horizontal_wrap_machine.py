# Copyright (c) 2019 The University of Manchester
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

from spinn_utilities.overrides import overrides
from .machine import Machine


class HorizontalWrapMachine(Machine):

    @overrides(Machine.multiple_48_chip_boards)
    def multiple_48_chip_boards(self):
        return self._width % 12 == 0 and (self._height - 4) % 12 == 0

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_x = (x + ethernet_x) % self._width
            chip_y = (y + ethernet_y)
            yield (chip_x, chip_y)

    @overrides(Machine.get_xy_cores_by_ethernet)
    def get_xy_cores_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y), n_cores in self.CHIPS_PER_BOARD.items():
            yield ((x + ethernet_x) % self._width, (y + ethernet_y)), n_cores

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = ((x + ethernet_x) % self._width,
                       (y + ethernet_y))
            if chip_xy in self._chips:
                yield chip_xy

    @overrides(Machine.get_down_xys_by_ethernet)
    def get_down_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = ((x + ethernet_x) % self._width,
                       (y + ethernet_y))
            if (chip_xy) not in self._chips:
                yield chip_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x, y, link):
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = (x + add_x + self._width) % self._width
        link_y = y + add_y
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip):
        local_x = (chip.x - chip.nearest_ethernet_x + self._width) \
                   % self._width
        local_y = chip.y - chip.nearest_ethernet_y
        return local_x, local_y

    @overrides(Machine.get_global_xy)
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        global_x = (local_x + ethernet_x) % self._width
        global_y = local_y + ethernet_y
        return global_x, global_y

    @overrides(Machine.get_vector_length)
    def get_vector_length(self, source, destination):
        # Aliases for convenience
        w = self._width

        x_right = (destination[0] - source[0]) % w
        x_left = x_right - w
        y = destination[1] - source[1]

        if y > 0:
            # Positive (x_right) + positive(y) use greater
            if x_right > y:
                len_right = x_right
            else:
                len_right = y
            # Negative (x_left) and positive(y) sum of abs
            len_left = y - x_left
        else:
            # Positive (x_right) + negative(y) use sum of  abs
            len_right = x_right - y
            # Negative (x_left) + negative(y) use greater abs
            if x_left > y:
                len_left = - y
            else:
                len_left = - x_left
        if len_right < len_left:
            return len_right
        else:
            return len_left

    @overrides(Machine.get_vector)
    def get_vector(self, source, destination):
        # Aliases for convenience
        w = self._width

        x_right = (destination[0] - source[0]) % w
        x_left = x_right - w
        y = destination[1] - source[1]

        if y > 0:
            # Positive (x_right) + positive(y) use greater
            if x_right > y:
                len_right = x_right
            else:
                len_right = y
            # Negative (x_left) and positive(y) sum of abs
            len_left = y - x_left
        else:
            # Positive (x_right) + negative(y) use sum of  abs
            len_right = x_right - y
            # Negative (x_left) + negative(y) use greater abs
            if x_left > y:
                len_left = - y
            else:
                len_left = - x_left
        if len_right < len_left:
            return self._minimize_vector(x_right, y)
        else:
            return self._minimize_vector(x_left, y)

    @overrides(Machine.concentric_xys)
    def concentric_xys(self, radius, start):
        # Aliases for convenience
        w = self._width
        for (x, y) in self._basic_concentric_xys(radius, start):
            yield (x % w, y)

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "HorWrap"
