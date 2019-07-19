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

from spinn_machine.machine import Machine


class SpiNNakerTriadGeometry(object):
    """ Geometry of a "triad" of SpiNNaker boards

        The geometry is defined by the arguments to the constructor; the\
        standard arrangement can be obtained from get_spinn5_geometry

        Note that the geometry defines what a Triad is in terms of the\
        dimensions of a triad and where the Ethernet chips occur in the\
        triad
    """
    __slots__ = [
        "_ethernet_offset",
        "_triad_height",
        "_triad_width",
        "_roots"]

    # Stored singleton
    spinn5_triad_geometry = None

    @staticmethod
    def get_spinn5_geometry():
        """ Get the geometry object for a SpiNN-5 arrangement of boards

        :return: a :py:class:`SpiNNakerTriadGeometry` object.
        """

        # Note the centres are slightly offset so as to force which edges are
        # included where
        if SpiNNakerTriadGeometry.spinn5_triad_geometry is None:
            SpiNNakerTriadGeometry.spinn5_triad_geometry = \
                SpiNNakerTriadGeometry(
                    12, 12, [(0, 0), (4, 8), (8, 4)], (3.6, 3.4))
        return SpiNNakerTriadGeometry.spinn5_triad_geometry

    def __init__(self, triad_width, triad_height, roots, centre):
        """

        :param triad_width: width of a triad in chips
        :type triad_width: int
        :param triad_height: height of a triad in chips
        :type triad_height: int
        :param roots: locations of the Ethernet connected chips
        :type roots: list of (int, int)
        :param centre:\
            the distance from each Ethernet chip to the centre of the hexagon
        :type centre: (float, float)
        """

        self._triad_width = triad_width
        self._triad_height = triad_height
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
            (self._locate_nearest_ethernet(
                x, y, extended_ethernet_chips, centre)
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
    def _hexagonal_metric_distance(x, y, x_centre, y_centre):
        """ Get the hexagonal metric distance of a point from the centre of\
            the hexagon

            Computes the max of the magnitude of the dot products with the\
            normal vectors for the hexagon sides. The normal vectors are\
            (1,0), (0,1) and (1,-1); we don't need to be careful with the\
            signs of the vectors because we're about to do abs() of them\
            anyway.

        :param x: The x-coordinate of the chip to get the distance for
        :type x: int
        :param y: The y-coordinate of the chip to get the distance for
        :type y: int
        :param x_centre:\
            The x-coordinate of the centre of the hexagon.  Note that this is\
            the theoretical centre, it might not be an actual chip
        :type x_centre: float
        :param y_centre:\
            The y-coordinate of the centre of the hexagon.  Note that this is\
            the theoretical centre, it might not be an actual chip
        :type y_centre: float
        :return: how far the chip is away from the centre of the hexagon
        :rtype: float
        """
        dx = x - x_centre
        dy = y - y_centre
        return max(abs(dx), abs(dy), abs(dx - dy))

    def _locate_nearest_ethernet(self, x, y, ethernet_chips, centre):
        """ Get the coordinate of the nearest Ethernet chip down and left from\
            a given chip

        :param x: The x-coordinate of the chip to find the nearest Ethernet to
        :param y: The y-coordinate of the chip to find the nearest Ethernet to
        :param ethernet_chips: The locations of the Ethernet chips
        :param centre:\
            The distance from the Ethernet chip of the centre of the hexagonal\
            board
        :return: The nearest Ethernet coordinates as a tuple of x, y
        """
        x_c, y_c = centre

        # Find the coordinates of the closest Ethernet chip by measuring
        # the distance to the nominal centre of each board; the closest
        # Ethernet is the one that is on the same board as the one the chip
        # is closest to the centre of
        x1, y1, _ = min(
            ((x0, y0, self._hexagonal_metric_distance(
                x, y, x0 + x_c, y0 + y_c))
             for x0, y0 in ethernet_chips),
            key=lambda tupl: tupl[2])
        return (x1, y1)

    # pylint: disable=too-many-arguments
    def get_ethernet_chip_coordinates(
            self, x, y, width, height, root_x=0, root_y=0):
        """ Get the coordinates of a chip's local Ethernet connected chip\
            according to this triad geometry object

        .. warning::
            :py:meth:`.local_eth_coord` will always produce the\
            coordinates of the Ethernet-connected SpiNNaker chip on the same\
            SpiNN-5 board as the supplied chip.  This chip may not actually\
            be working.

        :param x: x-coordinate of the chip to find the nearest Ethernet of
        :type x: int
        :param y: y-coordinate of the chip to find the nearest Ethernet of
        :type y: int
        :param width:\
            width of the SpiNNaker machine (must be a multiple of the triad\
            width of this geometry)
        :type width: int
        :param height:\
            height of the SpiNNaker machine (must be a multiple of the triad\
            height of this geometry)
        :type height: int
        :param root_x: x-coordinate of the boot chip (default 0, 0)
        :type root_x: int
        :param root_y: y-coordinate of the boot chip (default 0, 0)
        :type root_y: int
        :return: The coordinates of the closest Ethernet chip
        :rtype: (int, int)
        """
        dx, dy = self.get_local_chip_coordinate(x, y, root_x, root_y)
        return ((x - dx) % width), ((y - dy) % height)

    def get_local_chip_coordinate(self, x, y, root_x=0, root_y=0):
        """ Get the coordinates of a chip on its board of a multi-board system\
            relative to the Ethernet chip of the board.

        .. note::
            This function assumes the system is constructed from SpiNN-5 boards

        :param x: The x-coordinate of the chip to find the location of
        :type x: int
        :param y: The y-coordinate of the chip to find the location of
        :type y: int
        :param root_x: The x-coordinate of the boot chip (default 0, 0)
        :type root_x: int
        :param root_y: The y-coordinate of the boot chip (default 0, 0)
        :type root_y: int
        :return: the coordinates of the chip relative to its board
        :rtype: (int, int)
        """
        dx = (x - root_x) % self._triad_width
        dy = (y - root_y) % self._triad_height
        return self._ethernet_offset[dy][dx]

    def get_potential_ethernet_chips(self, width, height):
        """ Get the coordinates of chips that should be Ethernet chips

        :param width: The width of the machine to find the chips in
        :param height: The height of the machine to find the chips in
        """
        if width % self._triad_width == 0:
            eth_width = width
        else:
            eth_width = width - Machine.SIZE_X_OF_ONE_BOARD + 1
        if height % self._triad_height == 0:
            eth_height = height
        else:
            eth_height = height - Machine.SIZE_Y_OF_ONE_BOARD + 1
        # special case for single boards like the 2,2
        if (eth_width <= 0 or eth_height <= 0):
            return [(0, 0)]
        return [
            (x, y)
            for start_x, start_y in self._roots
            for y in range(start_y, eth_height, self._triad_height)
            for x in range(start_x, eth_width, self._triad_width)]
