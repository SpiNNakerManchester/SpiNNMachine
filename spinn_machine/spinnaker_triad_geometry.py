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
from typing import Sequence, Optional, Tuple
from typing_extensions import TypeAlias
from spinn_utilities.typing.coords import XY

_Centre: TypeAlias = Tuple[float, float]


class SpiNNakerTriadGeometry(object):
    """
    Geometry of a "triad" of SpiNNaker boards.

    The geometry is defined by the arguments to the constructor; the
    standard arrangement can be obtained from get_spinn5_geometry.

    .. note::
        The geometry defines what a Triad is in terms of the
        dimensions of a triad and where the Ethernet chips occur in the
        triad.
    """
    __slots__ = (
        "_ethernet_offset",
        "_triad_height",
        "_triad_width",
        "_board_height",
        "_board_width",
        "_roots")

    # Stored singleton
    spinn5_triad_geometry: Optional['SpiNNakerTriadGeometry'] = None

    @staticmethod
    def get_spinn5_geometry() -> 'SpiNNakerTriadGeometry':
        """
        Get the geometry object for a SpiNN-5 arrangement of boards

        :return: a :py:class:`SpiNNakerTriadGeometry` object.
        """
        # Note the centres are slightly offset so as to force which edges are
        # included where
        if SpiNNakerTriadGeometry.spinn5_triad_geometry is None:
            SpiNNakerTriadGeometry.spinn5_triad_geometry = \
                SpiNNakerTriadGeometry(
                    12, 12, 8, 8, [(0, 0), (4, 8), (8, 4)], (3.6, 3.4))
        return SpiNNakerTriadGeometry.spinn5_triad_geometry

    def __init__(
            self, triad_width: int, triad_height: int,
            board_width: int, board_height: int,
            roots: Sequence[XY], centre: _Centre):
        """
        :param int triad_width: width of a triad in chips
        :param int triad_height: height of a triad in chips
        :param int board_width: width of a board in chips
        :param int board_height: height of a board in chips
        :param roots: locations of the Ethernet connected chips
        :type roots: list(tuple(int, int))
        :param centre:
            the distance from each Ethernet chip to the centre of the hexagon

            .. note::
                This is the theoretical centre, it might not be an actual chip
        :type centre: tuple(float, float)
        """
        self._triad_width = triad_width
        self._triad_height = triad_height
        self._board_width = board_width
        self._board_height = board_height
        self._roots = roots

        # Copy the Ethernet locations to surrounding triads to make the
        # mathematics easier
        extended_ethernet_chips = [
            (x + x1, y + y1) for (x, y) in roots
            for x1 in (-triad_width, 0, triad_width)
            for y1 in (-triad_height, 0, triad_height)
        ]

        # Find the nearest Ethernet to each chip by hexagonal distance
        nearest_ethernets = (
            (self.__locate_nearest_ethernet(
                (x, y), extended_ethernet_chips, centre)
             for x in range(triad_width))
            for y in range(triad_height)
        )

        # SpiNN-5 Ethernet connected chip lookup.
        # Used by :py:meth:`.local_eth_coord`. Given an x and y
        # chip position return the offset of the chip's position
        # from the board's bottom-left chip.
        # Note: the order of indexes: ``_ethernet_offset[y][x]``!
        self._ethernet_offset = [
            [(x - vx, y - vy) for x, (vx, vy) in enumerate(row)]
            for y, row in enumerate(nearest_ethernets)]

    @staticmethod
    def __hexagonal_metric_distance(xy: XY, centre: _Centre):
        """
        Get the hexagonal metric distance of a point from the centre of
        the hexagon.

        Computes the max of the magnitude of the dot products with the
        normal vectors for the hexagon sides. The normal vectors are
        (1,0), (0,1) and (1,-1); we don't need to be careful with the
        signs of the vectors because we're about to do abs() of them anyway.

        :param int x: The x-coordinate of the chip to get the distance for
        :param int y: The y-coordinate of the chip to get the distance for
        :param float x_centre:
            The x-coordinate of the centre of the hexagon.

            .. note::
                This is the theoretical centre, it might not be an actual chip
        :param float y_centre:
            The y-coordinate of the centre of the hexagon.

            .. note::
                This is the theoretical centre, it might not be an actual chip
        :return: how far the chip is away from the centre of the hexagon
        :rtype: float
        """
        x, y = xy
        x_centre, y_centre = centre
        dx = x - x_centre
        dy = y - y_centre
        return max(abs(dx), abs(dy), abs(dx - dy))

    def __locate_nearest_ethernet(
            self, xy: XY, ethernet_chips: Sequence[XY], centre: _Centre):
        """
        Get the coordinate of the nearest Ethernet chip down and left from
        a given chip.

        :param x: The x-coordinate of the chip to find the nearest Ethernet to
        :param y: The y-coordinate of the chip to find the nearest Ethernet to
        :param ethernet_chips: The locations of the Ethernet chips
        :param centre:
            The distance from the Ethernet chip of the centre of the hexagonal
            board
        :return: The nearest Ethernet coordinates as a tuple of x, y
        """
        x_c, y_c = centre

        def measure(xy0: XY) -> float:
            x0, y0 = xy0
            return self.__hexagonal_metric_distance(xy, (x0 + x_c, y0 + y_c))

        # Find the coordinates of the closest Ethernet chip by measuring
        # the distance to the nominal centre of each board; the closest
        # Ethernet is the one that is on the same board as the one the chip
        # is closest to the centre of
        return min(ethernet_chips, key=measure)

    # pylint: disable=too-many-arguments
    def get_ethernet_chip_coordinates(
            self, x: int, y: int, width: int, height: int,
            root_x: int = 0, root_y: int = 0) -> XY:
        """
        Get the coordinates of a chip's local Ethernet connected chip
        according to this triad geometry object.

        .. warning::
            :py:meth:`.local_eth_coord` will always produce the
            coordinates of the Ethernet-connected SpiNNaker chip on the same
            SpiNN-5 board as the supplied chip.  This chip may not actually
            be working.

        :param int x: x-coordinate of the chip to find the nearest Ethernet of
        :param int y: y-coordinate of the chip to find the nearest Ethernet of
        :param int width:
            width of the SpiNNaker machine (must be a multiple of the triad
            width of this geometry)
        :param int height:
            height of the SpiNNaker machine (must be a multiple of the triad
            height of this geometry)
        :param int root_x:
            x-coordinate of the boot chip (default 0, 0)
        :param int root_y:
            y-coordinate of the boot chip (default 0, 0)
        :return: The coordinates of the closest Ethernet chip
        :rtype: (int, int)
        """
        dx, dy = self.get_local_chip_coordinate(x, y, root_x, root_y)
        return ((x - dx) % width), ((y - dy) % height)

    def get_local_chip_coordinate(
            self, x: int, y: int, root_x: int = 0, root_y: int = 0) -> XY:
        """
        Get the coordinates of a chip on its board of a multi-board system
        relative to the Ethernet chip of the board.

        .. note::
            This function assumes the system is constructed from SpiNN-5 boards

        :param int x: The x-coordinate of the chip to find the location of
        :param int y: The y-coordinate of the chip to find the location of
        :param int root_x: The x-coordinate of the boot chip (default 0, 0)
        :param int root_y: The y-coordinate of the boot chip (default 0, 0)
        :return: the coordinates of the chip relative to its board
        :rtype: (int, int)
        """
        dx = (x - root_x) % self._triad_width
        dy = (y - root_y) % self._triad_height
        return self._ethernet_offset[dy][dx]

    def get_potential_ethernet_chips(
            self, width: int, height: int) -> Sequence[XY]:
        """
        Get the coordinates of chips that should be Ethernet chips

        :param int width: The width of the machine to find the chips in
        :param int height: The height of the machine to find the chips in
        :rtype: list(tuple(int, int))
        """
        if width % self._triad_width == 0:
            eth_width = width
        else:
            eth_width = width - self._board_width + 1
        if height % self._triad_height == 0:
            eth_height = height
        else:
            eth_height = height - self._board_height + 1
        # special case for single boards like the 2,2
        if (eth_width <= 0 or eth_height <= 0):
            return [(0, 0)]
        return [
            (x, y)
            for start_x, start_y in self._roots
            for y in range(start_y, eth_height, self._triad_height)
            for x in range(start_x, eth_width, self._triad_width)]
