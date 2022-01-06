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

import logging
from spinn_utilities.data.utils_data_writer import UtilsDataWriter
from spinn_utilities.overrides import overrides
from spinn_utilities.log import FormatAdapter
from spinn_machine import Machine
from .machine_data_view import MachineDataView, _MachineDataModel

logger = FormatAdapter(logging.getLogger(__name__))
__temp_dir = None

REPORTS_DIRNAME = "reports"


class MachineDataWriter(UtilsDataWriter, MachineDataView):
    """
    Writer class for the Fec Data

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

    @overrides(UtilsDataWriter.hard_reset)
    def hard_reset(self):
        UtilsDataWriter.hard_reset(self)
        self.__data._hard_reset()

    @overrides(UtilsDataWriter.soft_reset)
    def soft_reset(self):
        UtilsDataWriter.soft_reset(self)
        self.__data._soft_reset()

    def set_machine(self, machine):
        if not isinstance(machine, Machine):
            raise TypeError("machine should be a Machine")
        self.__data._machine = machine

    def clear_machine(self):
        self.__data._machine = None
