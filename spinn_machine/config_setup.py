# Copyright (c) 2017 The University of Manchester
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
import os
from spinn_utilities.config_holder import (
    add_default_cfg, clear_cfg_files)
from spinn_utilities.config_holder import get_config_int, set_config
from spinn_utilities.config_setup import add_spinn_utilities_cfg
from spinn_utilities.log import FormatAdapter
from spinn_machine.data import MachineDataView
from spinn_machine.data.machine_data_writer import MachineDataWriter
from spinn_machine.exceptions import SpinnMachineException

BASE_CONFIG_FILE = "spinn_machine.cfg"

__SPIN1_SDRAM = 123469792

# TODO FIX with correct values. These are INCORRECT
__SPIN2_SDRAM = 1234567890

logger = FormatAdapter(logging.getLogger(__name__))


def unittest_setup():
    """
    Resets the configurations so only the local default configuration is
    included.

    .. note::
        This file should only be called from `SpiNNMachine/unittests`
    """
    clear_cfg_files(True)
    add_spinn_machine_cfg()
    MachineDataWriter.mock()


def add_spinn_machine_cfg():
    """
    Add the local configuration and all dependent configuration files.
    """
    add_spinn_utilities_cfg()
    add_default_cfg(os.path.join(os.path.dirname(__file__), BASE_CONFIG_FILE))


def __setup_spin(board_type, sdram):
    """
    Changes any board type settings to the Values required for a Spin1 board

    :raises SpinnMachineException: If called after a Machine has been created
    """
    if MachineDataView.has_actual_machine():
        raise SpinnMachineException("Illegal call once a Machine exists")
    cfg_sdram = get_config_int("Machine", "max_sdram_allowed_per_chip")
    if cfg_sdram is None:
        set_config("Machine", "max_sdram_allowed_per_chip", sdram)
    else:
        if sdram != cfg_sdram:
            logger.warning(
                "Using sdram {cfg_sdram} from cfg which is different to "
                f"the expected sdram of {sdram} for a {board_type} board.")


def setup_spin1():
    """
    Changes any board type settings to the Values required for a Spin1 board

    :raises SpinnMachineException: If called after a Machine has been created
    """
    __setup_spin("spin 1", __SPIN1_SDRAM)


def setup_spin2():
    """
    Changes any board type settings to the Values required for a Spin2 board

    :raises SpinnMachineException: If called after a Machine has been created
    """
    __setup_spin("spin_2", __SPIN2_SDRAM)
