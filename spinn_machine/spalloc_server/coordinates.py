# Copyright (c) 2025 The University of Manchester
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
from typing import Tuple
from spinn_machine import SpiNNakerTriadGeometry


def chip_to_board(x: int, y: int, w: int, h: int) -> Tuple[int, int, int]:
    """
    Get the board coordinates from the chip coordinates.

    :param x: The X coordinate of the chip.
    :param y: The Y coordinate of the chip.
    :param w: The width of the machine in chips.
    :param h: The height of the machine in chips.

    :return: The board coordinates (x, y, z) of the chip.
    """
    # Convert to coordinate of chip at the bottom-left-corner of the board
    x, y = map(
        int,
        SpiNNakerTriadGeometry.get_spinn5_geometry()
        .get_ethernet_chip_coordinates(x, y, w, h))

    # The coordinates of the chip within its triad
    tx = x % 12
    ty = y % 12

    x //= 12
    y //= 12

    if tx == ty == 0:
        z = 0
    elif tx == 8 and ty == 4:
        z = 1
    elif tx == 4 and ty == 8:
        z = 2
    else:  # pragma: no cover
        assert False

    return (x, y, z)
