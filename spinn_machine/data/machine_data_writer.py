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
from spinn_utilities.data.utils_data_writer import UtilsDataWriter
from spinn_utilities.overrides import overrides
from spinn_utilities.log import FormatAdapter
from spinn_machine import Machine, virtual_machine
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
    __slots__ = []

    @overrides(UtilsDataWriter._mock)
    def _mock(self):
        UtilsDataWriter._mock(self)
        self.__data._clear()
        self.__data._machine_generator = self._mock_machine

    def _mock_machine(self):
        """
        Method to create a virtual machine in mock mode.
        """
        self.set_machine(virtual_machine(width=8, height=8))

    @overrides(UtilsDataWriter._setup)
    def _setup(self):
        UtilsDataWriter._setup(self)
        self.__data._clear()

    @overrides(UtilsDataWriter._hard_reset)
    def _hard_reset(self):
        UtilsDataWriter._hard_reset(self)
        self.__data._hard_reset()

    @overrides(UtilsDataWriter._soft_reset)
    def _soft_reset(self):
        UtilsDataWriter._soft_reset(self)
        self.__data._soft_reset()

    def get_user_accessed_machine(self):
        """
        Reports if `...View.get_machine` has been called outside of `sim.run`.

        Designed to only be used from ASB. Any other use is not supported
        """
        return self.__data._user_accessed_machine

    def set_machine(self, machine):
        """
        Sets the machine.

        :param Machine machine:
        :raises TypeError: it the machine is not a Machine
        """
        if not isinstance(machine, Machine):
            raise TypeError("machine should be a Machine")
        self.__data._machine = machine

    def clear_machine(self):
        """
        Clears any previously set machine.

        .. warning::
            Designed to only be used by ASB to remove a max machine before
            allocating an actual one.  Any other use is not supported.
            Will be removed without notice if `max_machine` is no longer done.
        """
        self.__data._machine = None

    def set_machine_generator(self, machine_generator):
        """
        Registers a function that can be called to give a machine.

        :param function machine_generator:
        """
        if not callable(machine_generator):
            raise TypeError("machine_generator must be callable")
        self.__data._machine_generator = machine_generator
