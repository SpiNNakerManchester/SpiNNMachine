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
from typing import Iterable, Tuple
from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XY
from .machine import Machine
from .chip import Chip


class NoWrapMachine(Machine):
    """
    This is a Machine that uses a subsection of the whole Machine.

    It will therefore have no wrap in either directions.

    This class provides the simpler maths that do not deal with wraps.
    """

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
        for (x, y) in self._chip_core_map:
            yield (x + ethernet_x, y + ethernet_y)

    @overrides(Machine.get_xy_cores_by_ethernet)
    def get_xy_cores_by_ethernet(
            self, ethernet_x: int, ethernet_y: int
            ) -> Iterable[Tuple[XY, int]]:
        for (x, y), n_cores in self._chip_core_map.items():
            # if Ethernet_x/y != 0 GIGO mode so ignore Ethernet
            yield ((x + ethernet_x, y + ethernet_y), n_cores)

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
        for (x, y) in self._chip_core_map:
            chip_xy = (x + ethernet_x, y + ethernet_y)
            if chip_xy in self._chips:
                yield chip_xy

    @overrides(Machine.get_down_xys_by_ethernet)
    def get_down_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
        for (x, y) in self._chip_core_map:
            chip_xy = ((x + ethernet_x), (y + ethernet_y))
            if chip_xy not in self._chips:
                yield chip_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x: int, y: int, link: int) -> XY:
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = x + add_x
        link_y = y + add_y
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip: Chip) -> XY:
        local_x = chip.x - chip.nearest_ethernet_x
        local_y = chip.y - chip.nearest_ethernet_y
        return local_x, local_y

    @overrides(Machine.get_global_xy)
    def get_global_xy(
            self, local_x: int, local_y: int,
            ethernet_x: int, ethernet_y: int) -> XY:
        global_x = local_x + ethernet_x
        global_y = local_y + ethernet_y
        return global_x, global_y

    @overrides(Machine.get_vector_length)
    def get_vector_length(self, source: XY, destination: XY) -> int:
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
        # An x and y having the same sign they can be replaced with a z
        #     I.E. Replace a North and an East with a NorthEast
        # So the length is the greater absolute value of x or y
        # If the are opposite use the sum of the absolute values

        if x > 0:
            if y > 0:
                # the greater abs
                if x > y:
                    return x
                else:
                    return y
            else:
                # abs(positive x) + abs(negative y)
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
    def get_vector(self, source: XY, destination: XY) -> Tuple[int, int, int]:
        return self._minimize_vector(
            destination[0]-source[0], destination[1]-source[1])

    @overrides(Machine.concentric_xys)
    def concentric_xys(self, radius: int, start: XY) -> Iterable[XY]:
        # Aliases for convenience
        return self._basic_concentric_xys(radius, start)

    @property
    @overrides(Machine.wrap)
    def wrap(self) -> str:
        return "NoWrap"
