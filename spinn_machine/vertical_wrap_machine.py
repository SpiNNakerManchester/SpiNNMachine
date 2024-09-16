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


class VerticalWrapMachine(Machine):
    """
    This is a Machine that uses every single board in at least some columns.

    It will therefore wraps in both the vertical directions.

    This class provides the more complex maths to deal with wraps.
    """

    @overrides(Machine.get_xys_by_ethernet)
    def get_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
        for (x, y) in self._chip_core_map:
            chip_x = (x + ethernet_x)
            chip_y = (y + ethernet_y) % self._height
            yield (chip_x, chip_y)

    @overrides(Machine.get_xy_cores_by_ethernet)
    def get_xy_cores_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[
                Tuple[XY, int]]:
        for (x, y), n_cores in self._chip_core_map.items():
            yield ((x + ethernet_x), (y + ethernet_y) % self._height), n_cores

    @overrides(Machine.get_existing_xys_by_ethernet)
    def get_existing_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
        for (x, y) in self._chip_core_map:
            chip_xy = ((x + ethernet_x),
                       (y + ethernet_y) % self._height)
            if chip_xy in self._chips:
                yield chip_xy

    @overrides(Machine.get_down_xys_by_ethernet)
    def get_down_xys_by_ethernet(
            self, ethernet_x: int, ethernet_y: int) -> Iterable[XY]:
        for (x, y) in self._chip_core_map:
            chip_xy = ((x + ethernet_x),
                       (y + ethernet_y) % self._height)
            if chip_xy not in self._chips:
                yield chip_xy

    @overrides(Machine.xy_over_link)
    def xy_over_link(self, x: int, y: int, link: int) -> XY:
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = x + add_x
        link_y = (y + add_y + self.height) % self.height
        return link_x, link_y

    @overrides(Machine.get_local_xy)
    def get_local_xy(self, chip: Chip) -> XY:
        local_x = chip.x - chip.nearest_ethernet_x
        local_y = ((chip.y - chip.nearest_ethernet_y + self._height)
                   % self._height)
        return local_x, local_y

    @overrides(Machine.get_global_xy)
    def get_global_xy(
            self, local_x: int, local_y: int,
            ethernet_x: int, ethernet_y: int) -> XY:
        global_x = local_x + ethernet_x
        global_y = (local_y + ethernet_y) % self._height
        return global_x, global_y

    @overrides(Machine.get_vector_length)
    def get_vector_length(self, source: XY, destination: XY) -> int:
        # Aliases for convenience
        h = self._height

        x = destination[0] - source[0]
        y_up = (destination[1] - source[1]) % h
        y_down = y_up - h

        if x > 0:
            # positive (x) and positive (y_up) use greater
            if x > y_up:
                len_up = x
            else:
                len_up = y_up
            # positive (x) and negative(y_down) use sum of abs
            len_down = x - y_down
        else:
            # negative (x) and positive (y_up)
            len_up = y_up - x
            # negative (x) and negative(y) use greater abs
            if x > y_down:
                len_down = - y_down
            else:
                len_down = - x
        if len_up < len_down:
            return len_up
        else:
            return len_down

    @overrides(Machine.get_vector)
    def get_vector(self, source: XY, destination: XY) -> Tuple[int, int, int]:
        # Aliases for convenience
        h = self._height

        x = destination[0] - source[0]
        y_up = (destination[1] - source[1]) % h
        y_down = y_up - h

        if x > 0:
            # positive (x) and positive (y_up) use greater
            if x > y_up:
                len_up = x
            else:
                len_up = y_up
            # positive (x) and negative(y_down) use sum of abs
            len_down = x - y_down
        else:
            # negative (x) and positive (y_up)
            len_up = y_up - x
            # negative (x) and negative(y) use greater abs
            if x > y_down:
                len_down = - y_down
            else:
                len_down = - x
        if len_up < len_down:
            return self._minimize_vector(x, y_up)
        else:
            return self._minimize_vector(x, y_down)

    @overrides(Machine.concentric_xys)
    def concentric_xys(self, radius: int, start: XY) -> Iterable[XY]:
        # Aliases for convenience
        h = self._height
        for (x, y) in self._basic_concentric_xys(radius, start):
            yield (x, y % h)

    @property
    @overrides(Machine.wrap)
    def wrap(self) -> str:
        return "VerWrap"
