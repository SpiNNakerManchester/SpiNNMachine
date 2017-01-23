class SpiNNakerGeometry(object):
    """Geometry of a tiled group of SpiNNaker boards.
    
    The geometry is defined by the arguments to the constructor; the standard
    arrangement is in the :py:data:`Spinn5_geometry` object.
    """

    Spinn5_geometry = None

    @classmethod
    def get_spinn5_geometry(cls):
        """ creates a system for coping with systems corresponding to sets
        of spinn-5 boards

        :return: a SpiNNakerGeometry object.
        """

        # Note the centres are slightly offset so as to force which edges are
        # included where
        if SpiNNakerGeometry.Spinn5_geometry is None:
            SpiNNakerGeometry.Spinn5_geometry = SpiNNakerGeometry(
                12, 12, [(0, 0), (4, 8), (8, 4)], (3.6, 3.4))
        return SpiNNakerGeometry.Spinn5_geometry

    def __init__(self, width, height, roots, centre):
        """ the constructor for the geometry functions

        :param width:  width of the spinnaker triad
        :param height: height of the spinnaker triad
        :param roots: locations coords of the ethernet connected chips
        :param centre: offset coords of the hexagon situated at 0,0
        :type width: int
        :type height: int
        :type roots: list of pairs of ints
        :type centre: pair of floats.
        """

        self._width = width
        self._height = height

        tiling_roots = [
            (x + x1, y + y1) for (x, y) in roots
            for x1 in (-width, 0, width) for y1 in (-height, 0, height)]

        table_gen = ((self._locate(x, y, tiling_roots, centre)
                      for x in range(width)) for y in range(height))

        # SpiNN-5 ethernet connected chip lookup.

        # Used by :py:meth:`.local_eth_coord`. Given an x and y
        # chip position modulo 12, return the offset of the chip's position
        # from the board's bottom-left chip.

        # Note: the order of indexes: ``_ethernet_offset[y][x]``!

        self._ethernet_offset = [
            [(x - vx, y - vy) for x, (vx, vy) in enumerate(row)]
            for y, row in enumerate(table_gen)]

    @staticmethod
    def _hex_metric(x, y, x_centre, y_centre):
        """ Hexagonal metric given coords of chip of consideration and
        ethernet chip.

        Computes the max of the magnitude of the dot products with the
        normal vectors for the hexagon sides. The normal vectors are
        (1,0), (0,1) and (1,-1); we don't need to be careful with the
        signs of the vectors because we're about to do abs() of them
        anyway.
        
        :param x: chip x coord
        :param y: chip y coord
        :param x_centre: hexagon centre x
        :param y_centre: hexagon centre y
        :type x: int
        :type y: int
        :type x_centre: float
        :type y_centre: float
        :return: distance in the metric space.
        (how far the chip is away from the centre of the hexagon)
        :rtype: float
        """
        dx = x - x_centre
        dy = y - y_centre
        return max(abs(dx), abs(dy), abs(dx - dy))

    def _locate(self, x, y, tiling_roots, centre):
        """Get the coordinate of the ethernet chip for a board that
        contains a particular location, given the overall board tiling.

        :param x: chip coord in x axis
        :param y: chip coord in y axis
        :param tiling_roots: information about the locations of the centres
        of the hexagons
        :param centre: the location of the centre of the relative hexagon.
        :return nearest ethernet coords as a tuple of x,y
        """

        # Critical: metric measure function is the hexagonal norm relative
        #  to the centre of the hexagon, which is at approximately coordinate
        #  (3.5,3.5) relative to the ethernet chip
        x_c, y_c = centre
        x1, y1, _ = min(
            ((x0, y0, self._hex_metric(x, y, x0 + x_c, y0 + y_c))
             for x0, y0 in tiling_roots),
            key=lambda (_, __, _measure): _measure)
        return (x1, y1)

    def local_eth_coord(self, x, y, width, height, root_x=0, root_y=0):
        """Get the coordinates of a chip's local ethernet connected chip.

        Returns the coordinates of the ethernet connected chip on the same
        board as the supplied chip.

        .. note::
            This function assumes the system is constructed from SpiNN-5 boards

        .. warning::

            In general, applications should interrogate the machine to
            determine which Ethernet connected chip is considered 'local' to
             a particular SpiNNaker chip.

            :py:meth:`.local_eth_coord` will always produce the
            coordinates of the Ethernet-connected SpiNNaker chip on the same
            SpiNN-5 board as the supplied chip.

        :param x: chip coord in x axis
        :param y: chip coord in y axis
        :param width: width of the spinnaker machine
         (should be a multiple of 12)
        :param height: height of the spinnaker machine
        (should be a multiple of 12)
        :param root_x: the chip x coord for the boot chip (default 0,0)
        :param root_y: the chip y coord for the boot chip (default 0,0)
        :type x: int
        :type y: int
        :type width: int
        :type height: int
        :type root_x: int
        :type root_y: int
        :return: the ethernet connected chip assocated with the chip coords
        given
        :rtype: (int, int)
        """
        dx, dy = self.chip_coord(x, y, root_x, root_y)
        return ((x - dx) % width), ((y - dy) % height)

    def chip_coord(self, x, y, root_x=0, root_y=0):
        """Get the coordinates of a chip on its board.

        Given the coordinates of a chip in a multi-board system, calculates the
        coordinates of the chip within its board.

        .. note::
            This function assumes the system is constructed from SpiNN-5 boards

        :param x: chip coord in x axis
        :param y: chip coord in y axis
        :param root_x: the chip x coord for the boot chip (default 0,0)
        :param root_y: the chip y coord for the boot chip (default 0,0)
        :type x: int
        :type y: int
        :type root_x: int
        :type root_y: int
        :return the coords of the chip relative to its board
        :rtype: (int, int)
        """
        dx = (x - root_x) % self._width
        dy = (y - root_y) % self._height
        return self._ethernet_offset[dy][dx]


# Note this must stay down here as python cares about order of file.
Spinn5_geometry = SpiNNakerGeometry.get_spinn5_geometry()
"""The geometry of a SpiNN-5 board."""
