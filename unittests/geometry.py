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

"""General-purpose SpiNNaker-related geometry functions.
From https://github.com/project-rig/rig/blob/master/rig/geometry.py
"""

import random


def to_xyz(xy):
    """Convert a two-tuple (x, y) coordinate into an (x, y, 0) coordinate."""
    x, y = xy
    return (x, y, 0)


def minimise_xyz(xyz):
    """Minimise an (x, y, z) coordinate."""
    x, y, z = xyz
    m = max(min(x, y), min(max(x, y), z))
    return (x-m, y-m, z-m)


def shortest_mesh_path_length(source, destination):
    """Get the length of a shortest path from source to destination without
    using wrap-around links.

    Parameters
    ----------
    source : (x, y, z)
    destination : (x, y, z)

    Returns
    -------
    int
    """
    x = destination[0] - source[0]
    y = destination[1] - source[1]
    z = destination[2] - source[2]

    # When vectors are minimised, (1,1,1) is added or subtracted from them.
    # This process does not change the range of numbers in the vector. When a
    # vector is minimal, it is easy to see that the range of numbers gives the
    # magnitude since there are at most two non-zero numbers (with opposite
    # signs) and the sum of their magnitudes will also be their range.
    #
    # Though ideally this code would be written::
    #
    #     >>> return max(x, y, z) - min(x, y, z)
    #
    # Unfortunately the min/max functions are very slow (as of CPython 3.5) so
    # this expression is unrolled as IF/else statements.

    # max(x, y, z)
    maximum = x
    if y > maximum:
        maximum = y
    if z > maximum:
        maximum = z

    # min(x, y, z)
    minimum = x
    if y < minimum:
        minimum = y
    if z < minimum:
        minimum = z

    return maximum - minimum


def shortest_mesh_path(source, destination):
    """Calculate the shortest vector from source to destination without using
    wrap-around links.

    Parameters
    ----------
    source : (x, y, z)
    destination : (x, y, z)

    Returns
    -------
    (x, y, z)
    """
    return minimise_xyz(d - s for s, d in zip(source, destination))


def shortest_torus_path_length(source, destination, width, height):
    """Get the length of a shortest path from source to destination using
    wrap-around links.

    See http://jhnet.co.uk/articles/torus_paths for an explanation of how this
    method works.

    Parameters
    ----------
    source : (x, y, z)
    destination : (x, y, z)
    width : int
    height : int

    Returns
    -------
    int
    """
    # Aliases for convenience
    w, h = width, height

    # Get (non-wrapping) x, y vector from source to destination as if the
    # source was at (0, 0).
    x = destination[0] - source[0]
    y = destination[1] - source[1]
    z = destination[2] - source[2]
    x, y = x - z, y - z
    x %= w
    y %= h

    # Calculate the shortest path length.
    #
    # In an ideal world, the following code would be used::
    #
    #     >>> return min(max(x, y),      # No wrap
    #     ...            w - x + y,      # Wrap X
    #     ...            x + h - y,      # Wrap Y
    #     ...            max(w-x, h-y))  # Wrap X and Y
    #
    # Unfortunately, however, the min/max functions are shockingly slow as of
    # CPython 3.5. Since this function may appear in some hot code paths (e.g.
    # the router), the above statement is unwrapped as a series of
    # faster-executing IF statements for performance.

    # No wrap
    length = x if x > y else y

    # Wrap X
    wrap_x = w - x + y
    if wrap_x < length:
        length = wrap_x

    # Wrap Y
    wrap_y = x + h - y
    if wrap_y < length:
        length = wrap_y

    # Wrap X and Y
    dx = w - x
    dy = h - y
    wrap_xy = dx if dx > dy else dy
    if wrap_xy < length:
        return wrap_xy
    else:
        return length


def shortest_torus_path(source, destination, width, height):
    """Calculate the shortest vector from source to destination using
    wrap-around links.

    See http://jhnet.co.uk/articles/torus_paths for an explanation of how this
    method works.

    Note that when multiple shortest paths exist, one will be chosen at random
    with uniform probability.

    Parameters
    ----------
    source : (x, y, z)
    destination : (x, y, z)
    width : int
    height : int

    Returns
    -------
    (x, y, z)
    """
    # Aliases for convenience
    w, h = width, height

    # Convert to (x,y,0) form
    sx, sy, sz = source
    sx, sy = sx - sz, sy - sz

    # Translate destination as if source was at (0,0,0) and convert to (x,y,0)
    # form where both x and y are not -ve.
    dx, dy, dz = destination
    dx, dy = (dx - dz - sx) % w, (dy - dz - sy) % h

    # The four possible vectors: [(distance, vector), ...]
    approaches = [(max(dx, dy), (dx, dy, 0)),                # No wrap
                  (w-dx+dy, (-(w-dx), dy, 0)),               # Wrap X only
                  (dx+h-dy, (dx, -(h-dy), 0)),               # Wrap Y only
                  (max(w-dx, h-dy), (-(w-dx), -(h-dy), 0))]  # Wrap X and Y

    # Select a minimal approach at random
    _, vector = min(approaches, key=(lambda a: a[0]+random.random()))
    x, y, z = minimise_xyz(vector)

    # Transform to include a random number of 'spirals' on Z axis where
    # possible.
    if abs(x) >= height:
        max_spirals = (x + height - 1 if x < 0 else x) // height
        d = random.randint(min(0, max_spirals), max(0, max_spirals)) * height
        x -= d
        z -= d
    elif abs(y) >= width:
        max_spirals = (y + width - 1 if y < 0 else y) // width
        d = random.randint(min(0, max_spirals), max(0, max_spirals)) * width
        y -= d
        z -= d

    return (x, y, z)
