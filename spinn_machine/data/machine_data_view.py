# Copyright (c) 2021-2022 The University of Manchester
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

from spinn_utilities.data import UtilsDataView
from spinn_machine import virtual_machine
# pylint: disable=protected-access


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
        "_fixed_machine",
        "_machine",
        "_user_accessed_machine"
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
        self._fixed_machine = False
        self._hard_reset()
        self._machine = None

    def _hard_reset(self):
        """
        Clears out all data that should change after a reset and graph change

        This does NOT clear the machine as it may have been asked for before
        """
        self._soft_reset()
        if not self._fixed_machine:
            self._machine = None
        self._user_accessed_machine = False

    def _soft_reset(self):
        """
        Clears timing and other data that should changed every reset
        """
        # Holder for any later additions


class MachineDataView(UtilsDataView):
    """
    Adds the extra Methods to the View for Machine level.

    See UtilsDataView for a more detailed description.

    This class is designed to only be used directly within the SpiNNMachine
    repository as all methods are available to subclasses
    """

    __data = _MachineDataModel()
    __slots__ = []

    # machine methods

    @classmethod
    def has_machine(cls):
        """
        Reports if a machine is currently set or can be mocked

        :rtype: bool
        """
        return (cls.__data._machine is not None or
                cls._is_mocked())

    @classmethod
    def get_machine(cls):
        """
        Returns the Machine if it has been set

        In Mock mode will create and return a virtual 8 * 8 board

        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        :rtype: ~spinn_machine.Machine
        """
        if cls.__data._machine is None:
            if cls._is_mocked():
                cls.__data._machine = virtual_machine(width=8, height=8)
                cls.__data._fixed_machine = True
            else:
                raise cls._exception("machine")
        if cls.is_user_mode():
            if not cls.__data._fixed_machine:
                if cls.is_reset_last():
                    # After a reset user may not access none fixed machine!
                    raise cls._exception("machine")
                cls.__data._user_accessed_machine = True
        return cls.__data._machine

    @classmethod
    def get_chip_at(cls, x, y):
        """
        Gets the chip at x and y

        Almost Semantic sugar for machine.get_chip_at

        The method however does not return None but rather raises a KeyError
        if the chip is not known

        :param int x:
        :param int y:
        :rtype: Chip
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        :raises KeyError: If the chip does not exist but the machine does
        """
        if cls.__data._machine is None:
            cls.get_machine()
        return cls.__data._machine._chips[(x, y)]

    @classmethod
    def get_nearest_ethernet(cls, x, y):
        """
        Gets the nearest ethernet x and y for the chip at x, y if it exists

        If there is no machine or no chip at (x, y) this method,
        or any other issue will just return x,y

        .. Note:
            This method will never request a new machine.
            Therefore a call to this method will not trigger a hard reset

        :param int x:
        :param int y:
        :return: Chip(x,y)'s nearest_ethernet info
            or if that is not available just x, and y
        :rtype: tuple(int, int)
        """
        try:
            chip = cls.__data._machine._chips[(x, y)]
            return chip.nearest_ethernet_x, chip.nearest_ethernet_y
        except Exception:  # pylint: disable=broad-except
            if cls.__data._machine is None:
                return x, y
            return x, y

    @classmethod
    def where_is_xy(cls, x, y):
        """
        Gets a string saying where chip at x and y is if possible

        Almost Semantic sugar for get_machine.where_is_xy

        The method does not raise an exception rather returns a String of the
        exception

        .. Note:
            This method will never request a new machine.
            Therefore a call to this method will not trigger a hard reset

        :param int x:
        :param int y:
        :rtype: str
        """
        try:
            return cls.__data._machine.where_is_xy(x, y)
        except Exception as ex:  # pylint: disable=broad-except
            if cls.__data._machine is None:
                return "No Machine created yet"
            return str(ex)

    @classmethod
    def where_is_chip(cls, chip):
        """
        Gets a string saying where chip is if possible

        Almost Semantic sugar for get_machine.where_is_xy

        The method does not raise an exception rather returns a String of the
        exception

        .. Note:
            This method will never request a new machine.
            Therefore a call to this method will not trigger a hard reset

        :param int x:
        :param int y:
        :rtype: str
        """
        try:
            return cls.__data._machine.where_is_chip(chip)
        except Exception as ex:  # pylint: disable=broad-except
            if cls.__data._machine is None:
                return "Chip is from a previous machine"
            return str(ex)

    @classmethod
    def has_fixed_machine(cls):
        """
        Detects if a fixed machine has been registered

        :return: If and only if there is a Machine AND it has been set fixed
        """
        return cls.__data._fixed_machine
