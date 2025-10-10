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
from typing import Optional
from spinn_utilities.data.utils_data_writer import UtilsDataWriter
from spinn_utilities.overrides import overrides
from spinn_utilities.log import FormatAdapter
from spinn_machine import Machine

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

        :returns:
            True if get_machine has been called other than by the run process
        """
        return self.__data._user_accessed_machine

    def set_user_accessed_machine(self) -> None:
        """
        Reports if `...View.get_machine` has been called outside of `sim.run`.

        Designed to only be used from ASB. Any other use is not supported

        :returns:
            True if get_machine has been called other than by the run process
        """
        self.__data._user_accessed_machine = True

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
        Clears any previously set machine and any data related to the Machine

        .. warning::
            Designed to only be used by ASB to remove a machine when something
            went wrong before it could be returned from get machine
        """
        self.__data._machine = None
        self.__data._quad_map = None
        self.__data._v_to_p_map = None

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

    def set_n_required(self, n_boards_required: Optional[int],
                       n_chips_required: Optional[int]) -> None:
        """
        Sets (if not `None`) the number of boards/chips requested by the user.

        :param n_boards_required:
            `None` or the number of boards requested by the user
        :param n_chips_required:
            `None` or the number of chips requested by the user
        """
        if n_boards_required is None:
            if n_chips_required is None:
                return
            elif not isinstance(n_chips_required, int):
                raise TypeError("n_chips_required must be an int (or None)")
            if n_chips_required <= 0:
                raise ValueError(
                    "n_chips_required must be positive and not "
                    f"{n_chips_required}")
        else:
            if n_chips_required is not None:
                raise ValueError(
                    "Illegal call with both both param provided as "
                    f"{n_boards_required}, {n_chips_required}")
            if not isinstance(n_boards_required, int):
                raise TypeError("n_boards_required must be an int (or None)")
            if n_boards_required <= 0:
                raise ValueError(
                    "n_boards_required must be positive and not "
                    f"{n_boards_required}")
        if self.__data._n_boards_required is not None or \
                self.__data._n_chips_required is not None:
            raise ValueError(
                "Illegal second call to set_n_required")
        self.__data._n_boards_required = n_boards_required
        self.__data._n_chips_required = n_chips_required

    def set_n_chips_in_graph(self, n_chips_in_graph: int) -> None:
        """
        Sets the number of chips needed by the graph.
        """
        if not isinstance(n_chips_in_graph, int):
            raise TypeError("n_chips_in_graph must be an int (or None)")
        if n_chips_in_graph <= 0:
            raise ValueError(
                "n_chips_in_graph must be positive and not "
                f"{n_chips_in_graph}")
        self.__data._n_chips_in_graph = n_chips_in_graph
