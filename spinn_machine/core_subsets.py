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

from collections import OrderedDict
from .core_subset import CoreSubset


class CoreSubsets(object):
    """ Represents a group of CoreSubsets, with a maximum of one per\
        SpiNNaker chip.
    """

    __slots__ = ("_core_subsets", )

    def __init__(self, core_subsets=None):
        """
        :param iterable(CoreSubset) core_subsets:
            The cores for each desired chip
        """
        self._core_subsets = OrderedDict()
        if core_subsets is not None:
            for core_subset in core_subsets:
                self.add_core_subset(core_subset)

    def add_core_subset(self, core_subset):
        """ Add a core subset to the set

        :param CoreSubset core_subset: The core subset to add
        """
        x = core_subset.x
        y = core_subset.y
        for processor_id in core_subset.processor_ids:
            self.add_processor(x, y, processor_id)

    def add_core_subsets(self, core_subsets):
        """ Merges a core subsets into this one.

        :param iterable(CoreSubset) core_subsets: the core subsets to add
        """
        for core_subset in core_subsets:
            self.add_core_subset(core_subset)

    def add_processor(self, x, y, processor_id):
        """ Add a processor on a given chip to the set.

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :param int processor_id: A processor ID
        """
        xy = (x, y)
        if xy not in self._core_subsets:
            self._core_subsets[xy] = CoreSubset(x, y, [processor_id])
        else:
            self._core_subsets[xy].add_processor(processor_id)

    def is_chip(self, x, y):
        """ Determine if the chip with coordinates (x, y) is in the subset

        :param int x: The x-coordinate of a chip
        :param int y: The y-coordinate of a chip
        :return: True if the chip with coordinates (x, y) is in the subset
        :rtype: bool
        """
        return (x, y) in self._core_subsets

    def is_core(self, x, y, processor_id):
        """ Determine if there is a chip with coordinates (x, y) in the\
            subset, which has a core with the given ID in the subset

        :param int x: The x-coordinate of a chip
        :param int y: The y-coordinate of a chip
        :param int processor_id: The ID of a core
        :return: Whether there is a chip with coordinates (x, y) in the\
            subset, which has a core with the given ID in the subset
        :rtype: bool
        """
        xy = (x, y)
        if xy not in self._core_subsets:
            return False
        return processor_id in self._core_subsets[xy]

    @property
    def core_subsets(self):
        """ The one-per-chip subsets.

        :return: Iterable of core subsets
        :rtype: iterable(CoreSubset)
        """
        return iter(self._core_subsets.values())

    def get_core_subset_for_chip(self, x, y):
        """ Get the core subset for a chip.

        :param int x: The x-coordinate of a chip
        :param int y: The y-coordinate of a chip
        :return: The core subset of a chip, which will be empty if not added
        :rtype: CoreSubset
        """
        xy = (x, y)
        if xy not in self._core_subsets:
            return CoreSubset(x, y, [])
        return self._core_subsets[xy]

    def __iter__(self):
        """ Iterable of core_subsets

        :rtype: iterable(CoreSubset)
        """
        return iter(self._core_subsets.values())

    def __len__(self):
        """ The total number of processors that are in these core subsets

        :rtype: int
        """
        return sum(len(subset) for subset in self._core_subsets.values())

    def __contains__(self, x_y_tuple):
        """ True if the given coordinates are in the set

        :param x_y_tuple:
            Either a 2-tuple of x, y coordinates or a 3-tuple or x, y,
            processor_id coordinates
        :type x_y_tuple: tuple(int,int) or tuple(int,int,int)
        :rtype: bool
        """
        if len(x_y_tuple) == 2:
            return self.is_chip(*x_y_tuple)
        return self.is_core(*x_y_tuple)

    def __getitem__(self, x_y_tuple):
        """ The core subset for the given x, y tuple

        :param tuple(int,int) x_y_tuple:
        :rtype: CoreSubset
        """
        return self._core_subsets[x_y_tuple]

    def __repr__(self):
        """ Human-readable version of the object.

        :return: string representation of the CoreSubsets
        """
        output = ""
        for xy in self._core_subsets:
            output += str(xy)
        return output

    def intersect(self, other):
        """ Returns a new CoreSubsets which is an intersect of this and the\
            other.

        :param other: A second CoreSubsets with possibly overlapping cores
        :type other: CoreSubsets
        :return: A new CoreSubsets with any overlap
        :rtype: CoreSubsets
        """
        result = CoreSubsets()
        for xy in self._core_subsets:
            if xy in other._core_subsets:
                subset = self._core_subsets[xy].intersect(
                    other._core_subsets[xy])
                if subset:
                    result._core_subsets[xy] = subset
        return result

    def values(self):
        """
        :rtype: iterable(CoreSubset)
        """
        return self._core_subsets.values()
