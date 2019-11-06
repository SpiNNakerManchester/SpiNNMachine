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

from spinn_utilities.ordered_set import OrderedSet


class CoreSubset(object):
    """ Represents a subset of the cores on a SpiNNaker chip.
    """

    __slots__ = (
        "_x", "_y", "_processor_ids"
    )

    def __init__(self, x, y, processor_ids):
        """
        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param processor_ids: The processor IDs on the chip
        :type processor_ids: iterable(int)
        """
        self._x = x
        self._y = y
        self._processor_ids = OrderedSet()
        for processor_id in processor_ids:
            self.add_processor(processor_id)

    def add_processor(self, processor_id):
        """ Adds a processor ID to this subset

        :param processor_id: A processor ID
        :type processor_id: int
        :return: Nothing is returned
        :rtype: None
        """
        self._processor_ids.add(processor_id)

    def __contains__(self, processor_id):
        return processor_id in self._processor_ids

    @property
    def x(self):
        """ The x-coordinate of the chip

        :return: The x-coordinate
        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip

        :return: The y-coordinate
        :rtype: int
        """
        return self._y

    @property
    def processor_ids(self):
        """ The subset of processor IDs on the chip

        :return: An iterable of processor IDs
        :rtype: iterable(int)
        """
        return iter(self._processor_ids)

    def __repr__(self):
        return "{}:{}:{}".format(self._x, self._y, self._processor_ids)

    def __eq__(self, other):
        if not isinstance(other, CoreSubset):
            return False
        return self.x == other.x and self._y == other.y and \
            self._processor_ids == other.processor_ids

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        processors = frozenset(self._processor_ids)
        return (self._x, self._y, processors).__hash__()

    def __len__(self):
        """ The number of processors in this core subset
        """
        return len(self._processor_ids)

    def intersect(self, other):
        """ Returns a new CoreSubset which is an intersect of this and the\
            other.

        :param other: A second CoreSubset with possibly overlapping cores
        :type other: CoreSubset
        :return: A new CoreSubset with any overlap
        :rtype: CoreSubset
        """
        result = CoreSubset(self._x, self._y, [])
        for processor_id in self._processor_ids:
            if processor_id in other._processor_ids:
                result.add_processor(processor_id)
        return result
