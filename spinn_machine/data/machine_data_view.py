# Copyright (c) 2021 The University of Manchester
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

from spinn_utilities.data import UtilsDataView
# pylint: disable=protected-access


class _MachineDataModel(object):
    """
    Singleton data model.

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
    Adds the extra Methods to the View for Machine level.

    See :py:class:`~spinn_utilities.data.UtilsDataView` for a more detailed
    description.

    This class is designed to only be used directly within the SpiNNMachine
    repository as all methods are available to subclasses
    """

    __data = _MachineDataModel()
    __slots__ = []

    # machine methods

    @classmethod
    def has_machine(cls):
        """
        Reports if a machine is currently set or can be mocked.

        :rtype: bool
        """
        return (cls.__data._machine is not None or
                cls._is_mocked())

    @classmethod
    def get_machine(cls):
        """
        Returns the Machine if it has been set.

        In Mock mode will create and return a virtual 8 * 8 board

        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        :rtype: ~spinn_machine.Machine
        """
        if cls.is_user_mode():
            if cls.is_soft_reset():
                cls.__data._machine = None
            cls.__data._user_accessed_machine = True
        if cls.__data._machine is None:
            if cls.__data._machine_generator:
                # pylint: disable=not-callable
                cls.__data._machine_generator()
                return cls.__data._machine
            raise cls._exception("machine")
        return cls.__data._machine

    @classmethod
    def get_chip_at(cls, x, y):
        """
        Gets the chip at (`x`, `y`).

        Almost Semantic sugar for `get_machine().get_chip_at()`

        The method however does not return `None` but rather raises a KeyError
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
        Gets the nearest Ethernet-enabled chip (`x`, `y`) for the chip at
        (`x`, `y`) if it exists.

        If there is no machine or no chip at (`x`, `y`) this method,
        or any other issue will just return (`x`, `y`)

        .. note::
            This method will never request a new machine.
            Therefore a call to this method will not trigger a hard reset

        :param int x: Chip X coordinate
        :param int y: Chip Y coordinate
        :return: Chip (`x`,`y`)'s nearest_ethernet info
            or if that is not available just (`x`, `y`)
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
        Gets a string saying where chip at x and y is if possible.

        Almost Semantic sugar for `get_machine().where_is_xy()`

        The method does not raise an exception rather returns a String of the
        exception

        .. note::
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
        Gets a string saying where chip is if possible.

        Almost Semantic sugar for `get_machine().where_is_chip()`

        The method does not raise an exception rather returns a String of the
        exception

        .. note::
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
