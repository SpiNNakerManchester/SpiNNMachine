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

from .machine import Machine
from spinn_utilities.overrides import overrides


class NoWrapMachine(Machine):

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
                yield ((x, y), n_cores)

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(self, ethernet_x, ethernet_y):
        for (x, y) in self._local_xys:
            chip_xy = (x + ethernet_x, y + ethernet_y)
            if chip_xy in self._chips:
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

    @overrides(Machine.concentric_xys)
    def concentric_xys(self, radius, start):
        # Aliases for convenience
        return self._basic_concentric_xys(radius, start)

    @property
    @overrides(Machine.wrap)
    def wrap(self):
        return "NoWrap"
