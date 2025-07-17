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

from enum import IntEnum
from spinn_machine import SpiNNakerTriadGeometry
from .links import Links

link_to_vector = {
    (0, Links.north): (0, 0, 2),
    (0, Links.north_east): (0, 0, 1),
    (0, Links.east): (0, -1, 2),

    (1, Links.north): (1, 1, -1),
    (1, Links.north_east): (1, 0, 1),
    (1, Links.east): (1, 0, -1),

    (2, Links.north): (0, 1, -1),
    (2, Links.north_east): (1, 1, -2),
    (2, Links.east): (0, 0, -1),
}

link_to_vector.update({
    (z + dz, link.opposite): (-dx, -dy, -dz)
    for (z, link), (dx, dy, dz) in link_to_vector.items()
})


def board_down_link(x1, y1, z1, link, width, height):
    # pylint: disable=too-many-arguments
    dx, dy, dz = link_to_vector[(z1, link)]

    x2_ = (x1 + dx)
    y2_ = (y1 + dy)

    x2 = x2_ % width
    y2 = y2_ % height

    z2 = z1 + dz

    wrapped = WrapAround((WrapAround.x if x2_ != x2 else 0) |
                         (WrapAround.y if y2_ != y2 else 0))

    return (x2, y2, z2, wrapped)


def board_to_chip(x, y, z):
    x *= 12
    y *= 12

    if z == 1:
        x += 8
        y += 4
    elif z == 2:
        x += 4
        y += 8

    return (x, y)


def chip_to_board(x, y, w, h):
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


def triad_dimensions_to_chips(w, h, torus):
    w *= 12
    h *= 12

    # If not a torus topology, the pieces of boards which would wrap-around and
    # "tuck in" to the opposing sides of the network will be left poking out.
    # Compensate for this.
    if not (torus & WrapAround.x):
        w += 4
    if not (torus & WrapAround.y):
        h += 4

    return (w, h)


class WrapAround(IntEnum):
    none = 0b00
    """ No wrap-around links.
    """

    x = 0b01
    """ Has wrap around links around X-axis.
    """

    y = 0b10
    """ Has wrap around links around Y-axis.
    """

    both = 0b11
    """ Has wrap around links on X and Y axes.
    """
