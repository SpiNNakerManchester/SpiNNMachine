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

import logging
from typing import Callable
from spinn_utilities.data.utils_data_writer import UtilsDataWriter
from spinn_utilities.overrides import overrides
from spinn_utilities.log import FormatAdapter
from spinn_machine import Machine
from spinn_machine.virtual_machine import virtual_machine_by_boards
from .machine_data_view import MachineDataView, _MachineDataModel
logger = FormatAdapter(logging.getLogger(__name__))
__temp_dir = None

REPORTS_DIRNAME = "reports"
# pylint: disable=protected-access


class MachineDataWriter(UtilsDataWriter, MachineDataView):
    """
    See UtilsDataWriter.

    This class is designed to only be used directly within the SpiNNMachine
    repository unit tests as all methods are available to subclasses.
    """
    __data = _MachineDataModel()
    __slots__ = ()

    @overrides(UtilsDataWriter._mock)
    def _mock(self) -> None:
        UtilsDataWriter._mock(self)
        self.__data._clear()
        self.__data._machine_generator = self._mock_machine

    def _mock_machine(self) -> None:
        """
        Method to create a virtual machine in mock mode.
        """
        self.set_machine(virtual_machine_by_boards(1))

    @overrides(UtilsDataWriter._setup)
    def _setup(self) -> None:
        UtilsDataWriter._setup(self)
        self.__data._clear()

    @overrides(UtilsDataWriter._hard_reset)
    def _hard_reset(self) -> None:
        UtilsDataWriter._hard_reset(self)
        self.__data._hard_reset()

    @overrides(UtilsDataWriter._soft_reset)
    def _soft_reset(self) -> None:
        UtilsDataWriter._soft_reset(self)
        self.__data._soft_reset()

    def get_user_accessed_machine(self) -> bool:
        """
        Reports if `...View.get_machine` has been called outside of `sim.run`.

        Designed to only be used from ASB. Any other use is not supported
        """
        return self.__data._user_accessed_machine

    def set_machine(self, machine: Machine) -> None:
        """
        Sets the machine.

        :param machine:
        :raises TypeError: it the machine is not a Machine
        """
        if not isinstance(machine, Machine):
            raise TypeError("machine should be a Machine")
        self.__data._machine = machine

    def clear_machine(self) -> None:
        """
        Clears any previously set machine.

        .. warning::
            Designed to only be used by ASB to remove a max machine before
            allocating an actual one.  Any other use is not supported.
            Will be removed without notice if `max_machine` is no longer done.
        """
        self.__data._machine = None

    def set_machine_generator(
            self, machine_generator: Callable[[], None]) -> None:
        """
        Registers a function that can be called to give a machine. Note that
        if the function does not actually register a machine when called, an
        exception will be thrown.

        :param machine_generator:
        """
        if not callable(machine_generator):
            raise TypeError("machine_generator must be callable")
        self.__data._machine_generator = machine_generator

    def add_monitor_core(self, all_chips: bool) -> None:
        """
        Accepts a simple of the monitor cores to be added.

        Called by PacmanDataWriter add_sample_monitor_vertex.

        Only affect is to change the numbers reported by the
        get_all/ethernet_monitor methods.

        :param all_chips:
            If True assumes that this Vertex will be placed on all chips
            including Ethernet ones.
            If False assumes that this Vertex type will only be placed on
            Ethernet Vertices
        """
        self.__data._ethernet_monitor_cores += 1
        if all_chips:
            self.__data._all_monitor_cores += 1
