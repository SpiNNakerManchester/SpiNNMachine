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

from spinn_utilities.data.data_status import Data_Status
from spinn_utilities.data import UtilsDataView
from spinn_machine import virtual_machine


class _MachineDataModel(object):
    """
    Singleton data model

    This class should not be accessed directly please use the DataView and
    DataWriter classes.
    Accessing or editing the data held here directly is NOT SUPPORTED

    There may be other DataModel classes which sit next to this one and hold
    additional data. The DataView and DataWriter classes will combine these
    as needed.

    What data is held where and how can change without notice.
    """

    __singleton = None

    __slots__ = [
        # Data values cached
        "_machine",
    ]

    def __new__(cls):
        if cls.__singleton:
            return cls.__singleton
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        cls.__singleton = obj
        obj._clear()
        return obj

    def _clear(self):
        """
        Clears out all data
        """
        self._hard_reset()

    def _hard_reset(self):
        """
        Clears out all data that should change after a reset and graph change

        This does NOT clear the machine as it may have been asked for before
        """
        self._soft_reset()
        self._machine = None

    def _soft_reset(self):
        """
        Clears timing and other data that should changed every reset
        """
        # Holder for any later additions


class MachineDataView(UtilsDataView):
    """
    A read only view of the data available at Pacman level

    The objects accessed this way should not be changed or added to.
    Changing or adding to any object accessed if unsupported as bypasses any
    check or updates done in the writer(s).
    Objects returned could be changed to immutable versions without notice!

    The get methods will return either the value if known or a None.
    This is the faster way to access the data but lacks the safety.

    The property methods will either return a valid value or
    raise an Exception if the data is currently not available.
    These are typically semantic sugar around the get methods.

    The has methods will return True is the value is known and False if not.
    Semantically the are the same as checking if the get returns a None.
    They may be faster if the object needs to be generated on the fly or
    protected to be made immutable.

    While how and where the underpinning DataModel(s) store data can change
    without notice, methods in this class can be considered a supported API
    """

    __data = _MachineDataModel()
    __slots__ = []

    # machine methods

    def has_machine(self):
        """
        Reports if a machine is currently set or can be mocked

        :rtype: bool
        """
        return (self.__data._machine is not None or
                self.status == Data_Status.MOCKED)

    @property
    def machine(self):
        """
        The machine description

        :rtype: Machine
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        """
        if self.__data._machine is None:
            if self.status == Data_Status.MOCKED:
                self.__data._machine = virtual_machine(
                    width=8, height=8)
                return self.__data._machine
            raise self._exception("machine")
        return self.__data._machine

    def get_chip_at(self, x, y):
        """
        Gets the chip at x and y

        Semantic sugar for machine.get_chip_at

        :param int x:
        :param int y:
        :rtype: Chip
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        """
        try:
            return self.__data._machine.get_chip_at(x, y)
        except AttributeError:
            # Just in case first bad call or first during mock
            return self.machine.get_chip_at(x, y)
