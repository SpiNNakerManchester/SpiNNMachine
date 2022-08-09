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
    See UtilsDataWriter

    This class is designed to only be used directly within the SpiNNMachine
    repository unittests as all methods are available to subclasses
    """
    __data = _MachineDataModel()
    __slots__ = []

    @overrides(UtilsDataWriter._mock)
    def _mock(self):
        UtilsDataWriter._mock(self)
        self.__data._clear()

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
        if (self.__data._user_accessed_machine and
                not self.__data._fixed_machine):
            self.hard_reset()
        else:
            UtilsDataWriter._soft_reset(self)
            self.__data._soft_reset()

    def set_machine(self, machine, fixed=False):
        """
        Sets the machine

        :param Machine machine:
        :param bool fixed: Flag to say if machine is a fixed size.
        :raises TypeError: it the machine is not a Machine
        """
        if not isinstance(machine, Machine):
            raise TypeError("machine should be a Machine")
        self.__data._machine = machine
        self.__data._fixed_machine = fixed
        self.__data._user_accessed_machine = False
