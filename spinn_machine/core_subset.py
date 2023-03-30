# Copyright (c) 2016 The University of Manchester
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

from spinn_utilities.ordered_set import OrderedSet


class CoreSubset(object):
    """
    Represents a subset of the cores on a SpiNNaker chip.
    """

    __slots__ = (
        "_x", "_y", "_processor_ids"
    )

    def __init__(self, x, y, processor_ids):
        """
        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :param iterable(int) processor_ids: The processor IDs on the chip
        """
        self._x = x
        self._y = y
        self._processor_ids = OrderedSet()
        for processor_id in processor_ids:
            self.add_processor(processor_id)

    def add_processor(self, processor_id):
        """
        Adds a processor ID to this subset

        :param int processor_id: A processor ID
        """
        self._processor_ids.add(processor_id)

    def __contains__(self, processor_id):
        return processor_id in self._processor_ids

    @property
    def x(self):
        """
        The X-coordinate of the chip

        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """
        The Y-coordinate of the chip

        :rtype: int
        """
        return self._y

    @property
    def processor_ids(self):
        """
        The processor IDs on the chip that in the subset.

        :rtype: iterable(int)
        """
        return iter(self._processor_ids)

    def __repr__(self):
        return f"{self._x}:{self._y}:{self._processor_ids}"

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
        """
        The number of processors in this core subset.
        """
        return len(self._processor_ids)

    def intersect(self, other):
        """
        Returns a new CoreSubset which is an intersect of this and the other.

        :param CoreSubset other:
            A second CoreSubset with possibly overlapping cores
        :return: A new CoreSubset with any overlap
        :rtype: CoreSubset
        """
        result = CoreSubset(self._x, self._y, [])
        for processor_id in self._processor_ids:
            # pylint: disable=protected-access
            if processor_id in other._processor_ids:
                result.add_processor(processor_id)
        return result
