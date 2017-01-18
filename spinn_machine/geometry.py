class SpiNNakerGeometry(object):
    def __init__(self, width, height, roots, centre):
        # TODO: make this not assume the basic geometry when generating the offset table.
        self._width = width
        self._height = height
        tiling_roots = [(x+x1, y+y1) for (x,y) in roots \
                  for x1 in (-width,0,width) for y1 in (-height,0,height)]
        def hex_metric(x, y, x_centre, y_centre):
            """Hexagonal metric given coords of chip of consideration and
            ethernet chip.
            
            Computes the max of the magnitude of the dot products with the
            normal vectors for the hexagon sides. The normal vectors are
            (1,0), (0,1) and (1,-1); we don't need to be careful with the
            signs of the vectors because we're about to do abs() of them
            anyway.
            """
            dx = x - x_centre
            dy = y - y_centre
            return max(abs(dx), abs(dy), abs(dx-dy))
        def locate(x, y):
            """Get the coordinate of the ethernet chip for a board that
            contains a particular location, given the overall board tiling.
            """
            # Critical: metric measure function is the hexagonal norm relative to the centre of the hexagon, which is at approximately coordinate (3.5,3.5) relative to the ethernet chip 
            x_c,y_c = centre
            x1,y1,_ = min(
                ((x0,y0, hex_metric(x, y, x0+x_c, y0+y_c))
                    for x0,y0 in tiling_roots),
                key=lambda (x,y,_measure): _measure)
            return (x1,y1)
        tblgen = ((locate(x,y) for x in range(width)) for y in range(height))

        self._ETH_OFFSET = [
            [(x - vx, y - vy) for x, (vx, vy) in enumerate(row)]
            for y, row in enumerate(tblgen)]
        """SpiNN-5 ethernet connected chip lookup.

        Used by :py:func:`.local_eth_coord`. Given an x and y chip position
        modulo 12, return the offset of the chip's position from the board's
        bottom-left chip.

        Note: the order of indexes: ``_ETH_OFFSET[y][x]``!
        """

    def local_eth_coord(self, x, y, w, h, root_x=0, root_y=0):
        """Get the coordinates of a chip's local ethernet connected chip.

        Returns the coordinates of the ethernet connected chip on the same board as
        the supplied chip.

        .. note::
            This function assumes the system is constructed from SpiNN-5 boards

        .. warning::

            In general, applications should interrogate the machine to determine
            which Ethernet connected chip is considered 'local' to a particular
            SpiNNaker chip.

            :py:func:`.local_eth_coord` will always produce the coordinates
            of the Ethernet-connected SpiNNaker chip on the same SpiNN-5 board as
            the supplied chip.

        Parameters
        ----------
        x, y : int
            Chip whose coordinates are of interest.
        w, h : int
            Width and height of the system in chips.
        root_x, root_y : int
            The coordinates of the root chip (i.e. the chip used to boot the
            machine).
        """
        dx, dy = self.chip_coord(x, y, root_x, root_y)
        return (((x - dx) % w), ((y - dy) % h))

    def chip_coord(self, x, y, root_x=0, root_y=0):
        """Get the coordinates of a chip on its board.

        Given the coordinates of a chip in a multi-board system, calculates the
        coordinates of the chip within its board.

        .. note::
            This function assumes the system is constructed from SpiNN-5 boards

        Parameters
        ----------
        x, y : int
            The coordinates of the chip of interest
        root_x, root_y : int
            The coordinates of the root chip (i.e. the chip used to boot the
            machine).
        """
        dy = (y - root_y) % self._height
        dx = (x - root_x) % self._width
        return self._ETH_OFFSET[dy][dy] 

# Note the centres are slightly offset so as to force which edges are included where
Spinn5_geometry = SpiNNakerGeometry(12, 12, [(0,0),(4,8),(8,4)], (3.6,3.4))
"""The geometry of a SpiNN-5 board."""
