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
        "_machine_generator",
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
        self._hard_reset()
        self._machine_generator = None

    def _hard_reset(self):
        """
        Clears out all data that should change after a reset and graph change

        This does NOT clear the machine as it may have been asked for before
        """
        self._soft_reset()
        self._machine = None
        self._user_accessed_machine = False

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

        In Mock mode will create and return a virtual 8 * 8 board if needed

        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        :rtype: ~spinn_machine.Machine
        :
        """
        if cls.is_user_mode():
            if cls.is_soft_reset():
                cls.__data._machine = None
            cls.__data._user_accessed_machine = True
        if cls.__data._machine is None:
            if cls.__data._machine_generator:
                cls.__data._machine_generator()
                return cls.__data._machine
            raise cls._exception("machine")
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
        return cls.get_machine()._chips[(x, y)]

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
        :trype: tuple(int, int)
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
            Therefore a call to this method will trigger a hard reset

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
            Therefore a call to this method will trigger a hard reset

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
    def get_user_accessed_machine(cls):
        return cls.__data._user_accessed_machine
