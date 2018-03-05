from collections import OrderedDict
from six import itervalues
from .core_subset import CoreSubset


class CoreSubsets(object):
    """ Represents a group of CoreSubsets, with a maximum of one per chip
    """

    __slots__ = ("_core_subsets", )

    def __init__(self, core_subsets=None):
        """
        :param core_subsets: An iterable of cores for each desired chip
        :type core_subsets: iterable of\
            :py:class:`spinn_machine.CoreSubset`
        """
        self._core_subsets = OrderedDict()
        if core_subsets is not None:
            for core_subset in core_subsets:
                self.add_core_subset(core_subset)

    def add_core_subset(self, core_subset):
        """ Add a core subset to the set

        :param core_subset: The core subset to add
        :type core_subset: :py:class:`spinn_machine.CoreSubset`
        :return: Nothing is returned
        :rtype: None
        """
        xy = (core_subset.x, core_subset.y)
        if xy not in self._core_subsets:
            self._core_subsets[xy] = core_subset
        else:
            for processor_id in core_subset.processor_ids:
                self._core_subsets[xy].add_processor(processor_id)

    def add_processor(self, x, y, processor_id):
        """ Add a processor on a given chip to the set

        :param x: The x-coordinate of the chip
        :type x: int
        :param y: The y-coordinate of the chip
        :type y: int
        :param processor_id: A processor id
        :type processor_id: int
        :return: Nothing is returned
        :rtype: None
        """
        xy = (x, y)
        if xy not in self._core_subsets:
            self.add_core_subset(CoreSubset(x, y, []))
        self._core_subsets[xy].add_processor(processor_id)

    def is_chip(self, x, y):
        """ Determine if the chip with coordinates (x, y) is in the subset

        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :return: True if the chip with coordinates (x, y) is in the subset
        :rtype: bool
        """
        return (x, y) in self._core_subsets

    def is_core(self, x, y, processor_id):
        """ Determine if there is a chip with coordinates (x, y) in the\
            subset, which has a core with the given id in the subset

        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :param processor_id: The id of a core
        :type processor_id: int
        :return: Whether there is a chip with coordinates (x, y) in the\
            subset, which has a core with the given id in the subset
        """
        xy = (x, y)
        if xy not in self._core_subsets:
            return False
        return processor_id in self._core_subsets[xy]

    @property
    def core_subsets(self):
        """ The one-per-chip subsets

        :return: Iterable of core subsets
        :rtype: iterable of :py:class:`spinn_machine.CoreSubset`
        """
        return itervalues(self._core_subsets)

    def get_core_subset_for_chip(self, x, y):
        """ Get the core subset for a chip

        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :return: The core subset of a chip, which will be empty if not added
        :rtype: :py:class:`spinn_machine.CoreSubset`
        """
        xy = (x, y)
        if xy not in self._core_subsets:
            return CoreSubset(x, y, [])
        return self._core_subsets[xy]

    def __iter__(self):
        """ Iterable of core_subsets
        """
        return itervalues(self._core_subsets)

    def __len__(self):
        """ The total number of processors that are in these core subsets
        """
        return sum(len(subset) for subset in itervalues(self._core_subsets))

    def __contains__(self, x_y_tuple):
        """ True if the given coordinates are in the set

        :param x_y_tuple:\
            Either a 2-tuple of x, y coordinates or a 3-tuple or x, y,\
            processor_id coordinates
        """
        if len(x_y_tuple) == 2:
            return self.is_chip(*x_y_tuple)
        return self.is_core(*x_y_tuple)

    def __getitem__(self, x_y_tuple):
        """ The core subset for the given x, y tuple
        """
        return self._core_subsets[x_y_tuple]

    def __repr__(self):
        """ Human-readable version of the object

        :return: string representation of the CoreSubsets
        """
        output = ""
        for xy in self._core_subsets:
            output += str(xy)
        return output
