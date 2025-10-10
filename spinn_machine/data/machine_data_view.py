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
from __future__ import annotations
from typing import Dict, Optional, Tuple, TYPE_CHECKING, Union
from spinn_utilities.typing.coords import XY
from spinn_utilities.data import UtilsDataView
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.version.version_factory import version_factory
if TYPE_CHECKING:
    from spinn_machine.chip import Chip
    from spinn_machine.machine import Machine
    from spinn_machine.version.abstract_version import AbstractVersion
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

    __singleton: Optional['_MachineDataModel'] = None

    __slots__ = [
        # Data values cached
        "_all_monitor_cores",
        "_ethernet_monitor_cores",
        "_machine",
        "_machine_version",
        "_n_boards_required",
        "_n_chips_required",
        "_n_chips_in_graph",
        "_quad_map",
        "_user_accessed_machine",
        "_v_to_p_map"
    ]

    def __new__(cls) -> '_MachineDataModel':
        if cls.__singleton is not None:
            return cls.__singleton
        obj = object.__new__(cls)
        cls.__singleton = obj
        obj._clear()
        return obj

    def _clear(self) -> None:
        """
        Clears out all data
        """
        self._hard_reset()
        self._machine_version: Optional[AbstractVersion] = None
        self._n_boards_required: Optional[int] = None
        self._n_chips_required: Optional[int] = None
        self._quad_map: Optional[Dict[int, Tuple[int, int, int]]] = None

    def _hard_reset(self) -> None:
        """
        Clears out all data that should change after a reset and graph change

        This does NOT clear the machine as it may have been asked for before
        """
        self._soft_reset()
        self._all_monitor_cores: int = 0
        self._ethernet_monitor_cores: int = 0
        self._machine: Optional[Machine] = None
        self._n_chips_in_graph: Optional[int] = None
        self._v_to_p_map: Optional[Dict[XY, bytes]] = None
        self._user_accessed_machine = False

    def _soft_reset(self) -> None:
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
    __slots__ = ()

    # machine methods

    @classmethod
    def has_machine(cls) -> bool:
        """
        Reports if a machine is currently set or can be mocked.

        Unlike has_existing_machine for unit tests this will return True even
        if a Machine has not yet been created

        :returns: True if a Machine is available.
           (Already read Physically or can be Mocked if needed)
        """
        return (cls.__data._machine is not None or cls._is_mocked())

    @classmethod
    def has_existing_machine(cls) -> bool:
        """
        Reports if a machine is currently already created.

        Unlike has_machine this method returns false if a machine could be
        mocked

        :returns: True if a Machine has already been created.
        """
        return cls.__data._machine is not None

    @classmethod
    def get_machine(cls) -> Machine:
        """
        Returns the Machine if it has been set.

        In Mock mode will create and return a virtual 8 * 8 board

        ..note::
            Unlike `sim.get_machine` this method does not protect against
            inconstancy of Machine if reset has or will be called.

        :returns: The already existing Machine or Virtual 8 * 8 Machine.
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        """
        if cls.is_user_mode():
            if cls.is_soft_reset():
                raise cls._exception("machine after a soft reset")
        if cls.__data._machine is None:
            if cls._is_mocked():
                # delayed import due to circular dependencies
                # pylint: disable=import-outside-toplevel
                from spinn_machine.virtual_machine import \
                    virtual_machine_by_boards
                cls.__data._machine = virtual_machine_by_boards(1)
            if cls.__data._machine is None:
                raise cls._exception("machine")
        return cls.__data._machine

    @classmethod
    def get_chip_at(cls, x: int, y: int) -> Chip:
        """
        Gets the chip at (`x`, `y`).

        Almost Semantic sugar for `get_machine()[x, y]`

        The method however does not return `None` but rather raises a KeyError
        if the chip is not known

        :param x:
        :param y:
        :returns: The Chip or bust
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        :raises KeyError: If the chip does not exist but the machine does
        """
        return cls.get_machine()._chips[x, y]

    @classmethod
    def get_nearest_ethernet(cls, x: int, y: int) -> XY:
        """
        Gets the nearest Ethernet-enabled chip (`x`, `y`) for the chip at
        (`x`, `y`) if it exists.

        If there is no machine or no chip at (`x`, `y`) this method,
        or any other issue will just return (`x`, `y`)

        .. note::
            This method will never request a new machine.
            Therefore a call to this method will not trigger a hard reset

        :param x: Chip X coordinate
        :param y: Chip Y coordinate
        :return: Chip (`x`,`y`)'s nearest_ethernet info
            or if that is not available just (`x`, `y`)
        """
        try:
            m = cls.__data._machine
            if m is not None:
                chip = m._chips[(x, y)]
                return chip.nearest_ethernet_x, chip.nearest_ethernet_y
        except Exception:  # pylint: disable=broad-except
            pass
        return x, y

    @classmethod
    def where_is_xy(cls, x: int, y: int) -> str:
        """
        Gets a string saying where chip at x and y is if possible.

        Almost Semantic sugar for `get_machine().where_is_xy()`

        The method does not raise an exception rather returns a String of the
        exception

        .. note::
            This method will never request a new machine.
            Therefore a call to this method will not trigger a hard reset

        :param x:
        :param y:
        :return: A human-readable description of the location of a chip.
        """
        try:
            m = cls.__data._machine
            if m is not None:
                return m.where_is_xy(x, y)
            return "No Machine created yet"
        except Exception as ex:  # pylint: disable=broad-except
            if cls.__data._machine is None:
                return "No Machine created yet"
            return str(ex)

    @classmethod
    def where_is_chip(cls, chip: Chip) -> str:
        """
        Gets a string saying where chip is if possible.

        Almost Semantic sugar for `get_machine().where_is_chip()`

        The method does not raise an exception rather returns a String of the
        exception

        .. note::
            This method will never request a new machine.
            Therefore a call to this method will not trigger a hard reset

        :param chip:
        :return: A human-readable description of the location of a chip.
        """
        try:
            m = cls.__data._machine
            if m is not None:
                return m.where_is_chip(chip)
        except Exception as ex:  # pylint: disable=broad-except
            if cls.__data._machine is not None:
                return str(ex)
        return "Chip is from a previous machine"

    @classmethod
    def get_machine_version(cls) -> AbstractVersion:
        """
        Returns the Machine Version if it has or can be set.

        May call version_factory to create the version.

        :return: A superclass of AbstractVersion
        :raises SpinnMachineException: If the cfg version is not set correctly
        """
        if cls.__data._machine_version is None:
            cls.__data._machine_version = version_factory()
            cls.__data._quad_map = cls.__data._machine_version.quads_maps()
            if cls.__data._quad_map and cls.__data._v_to_p_map:
                raise SpinnMachineException(
                    "Can not have both quad_map and v_to_p_map")
        return cls.__data._machine_version

    @classmethod
    def set_v_to_p_map(cls, v_to_p_map: Dict[XY, bytes]) -> None:
        """
        Registers the mapping from Virtual to int physical core ids

        Note: Only expected to be used in Version 1

        :param v_to_p_map:
        """
        if cls.__data._quad_map:
            raise SpinnMachineException(
                "Can not have both quad_map and v_to_p_map")
        if cls.__data._v_to_p_map is None:
            cls.__data._v_to_p_map = v_to_p_map
        else:
            raise SpinnMachineException(
                "Unexpected second call to set_v_to_p_map")

    @classmethod
    def get_physical_core_id(cls, xy: XY, virtual_p: int) -> int:
        """
        Get the physical core ID from a virtual core ID.

        Note: This call only works for Version 1

        :param xy: The Chip or its XY coordinates
        :param virtual_p: The virtual core ID
        :return: The physical ID for the core on machine
        :raises SpiNNUtilsException: If v_to_p map not set,
            including if the MachineVersion does not support v_to_p_map
        :raises KeyError: If xy not in the v_to_p_map
        :raises IndexError: If virtual_p not in the v_to_p_map[xy]
        """
        if cls.__data._v_to_p_map is None:
            raise cls._exception("v_to_p map")
        return cls.__data._v_to_p_map[xy][virtual_p]

    @classmethod
    def get_physical_quad(cls, virtual_p: int) -> Tuple[int, int, int]:
        """
        Returns the quad qx, qy and qp for this virtual id

        Does not include XY so does not check if the Core exists on a Chip

        :param virtual_p:
        :raises SpiNNUtilsException: If quad_map map not set,
            MachineVersion does not support quad_map
        :raises KeyError: If virtual_p not in the quad_map
        :return: A report / debug representation of the Chip and physical quad
        """
        if cls.__data._quad_map is None:
            # Try to get the version which should load it
            cls.get_machine_version()
            if cls.__data._quad_map is None:
                raise cls._exception("quad_map")
        return cls.__data._quad_map[virtual_p]

    @classmethod
    def get_physical_string(cls, xy: XY, virtual_p: int) -> str:
        """
        Returns a String representing the physical core

        :param xy: The Chip or its XY coordinates
        :param virtual_p: The virtual (python) id for the core
        :return: A report / debug representation of the Chip and physical core
        """
        physical_p: Union[int, Tuple[int, int, int]]
        try:
            if cls.__data._v_to_p_map is not None:
                physical_p = cls.get_physical_core_id(xy, virtual_p)
                return f" (ph: {physical_p})"
            elif cls.__data._quad_map is not None:
                qx, qy, qp = cls.get_physical_quad(virtual_p)
                return f" (qpe:{qx}, {qy}, {qp})"
            else:
                return ""
        except Exception:  # pylint: disable=broad-except
            return ""

    @classmethod
    def get_all_monitor_cores(cls) -> int:
        """
        The number of cores on every chip reported to be used by \
        monitor vertices.

        Ethernet-enabled chips may have more.

        Does not include the system core reserved by the machine/ scamp.

        :return: The number of core that will be allocated for special
            monitor on each none Ethernet Chip
        """
        return cls.__data._all_monitor_cores

    @classmethod
    def get_ethernet_monitor_cores(cls) -> int:
        """
        The number of cores on every Ethernet chip reported to be used by \
        monitor vertices.

        This includes the one returned by get_all_monitor_cores unless for
        some reason these are not on Ethernet chips.

        Does not include the system core reserved by the machine/ scamp.

        :return: The number of core that will be allocated for special
            monitor on each Ethernet Chip
        """
        return cls.__data._ethernet_monitor_cores

    # n_boards/chips required

    @classmethod
    def has_n_boards_required(cls) -> bool:
        """
        Reports if a user has sets the number of boards requested during setup.

        :return: True if the user has sets the number of boards requested
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If n_boards_required is not set or set to `None`
        """
        return cls.__data._n_boards_required is not None

    @classmethod
    def get_n_boards_required(cls) -> int:
        """
        Gets the number of boards requested by the user during setup if known.

        Guaranteed to be positive

        :returns: The number of boards requested by the user
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the n_boards_required is currently unavailable
        """
        if cls.__data._n_boards_required is None:
            raise cls._exception("n_boards_requiredr")
        return cls.__data._n_boards_required

    @classmethod
    def get_n_chips_needed(cls) -> int:
        """
        Gets the number of chips needed, if set.

        This will be the number of chips requested by the user during setup,
        even if this is less that what the partitioner reported.

        If the partitioner has run and the user has not specified a number,
        this will be what the partitioner requested.

        Guaranteed to be positive if set

        :returns: the number of chips needed
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If data for n_chips_needed is not available
        """
        if cls.__data._n_chips_required:
            return cls.__data._n_chips_required
        if cls.__data._n_chips_in_graph:
            return cls.__data._n_chips_in_graph
        raise cls._exception("n_chips_requiredr")

    @classmethod
    def has_n_chips_needed(cls) -> bool:
        """
        Detects if the number of chips needed has been set.

        This will be the number of chips requested by the use during setup or
        what the partitioner requested.

        :returns: True if the number of required chips is known
        """
        if cls.__data._n_chips_required is not None:
            return True
        return cls.__data._n_chips_in_graph is not None

    @classmethod
    def get_chips_boards_required_str(cls) -> str:
        """
        :returns: a String to say what was required
        """
        if cls.__data._n_boards_required:
            return (f"Setup asked for "
                    f"{cls.__data._n_boards_required} Boards")
        if cls.__data._n_chips_required:
            return (f"Setup asked for "
                    f"{cls.__data._n_chips_required} Chips")
        if cls.__data._n_chips_in_graph:
            return (f"Graph requires "
                    f"{cls.__data._n_chips_in_graph} Chips")
        return "No requirements known"
