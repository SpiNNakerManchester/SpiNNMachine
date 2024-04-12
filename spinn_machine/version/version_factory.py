# Copyright (c) 2023 The University of Manchester
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
import logging
import sys
from typing import TYPE_CHECKING
from spinn_utilities.config_holder import (
    get_config_int_or_none, get_config_str_or_none)
from spinn_utilities.log import FormatAdapter
from spinn_machine.exceptions import SpinnMachineException
from .version_strings import VersionStrings
if TYPE_CHECKING:
    from .abstract_version import AbstractVersion

logger = FormatAdapter(logging.getLogger(__name__))

# Constant when wanting a specific version
THREE = 3
FIVE = 5
# New value subject to change
SPIN2_1CHIP = 201

# Flaks to test multiple versions including future ones
ANY_VERSION = -1

FOUR_PLUS_CHIPS = -2

# A Machine which support multiple boards
# Size of boards does not matter
MULTIPLE_BOARDS = -3

# A Machine with at least 8 * 8 including ones typical on a Version 5 board
BIG_MACHINE = -4

# A Machine with multiple boards that could wrap
# Will have hard coded assumption of board size 8 * 8
WRAPPABLE = -5


def version_factory() -> AbstractVersion:
    """
    Creates a Machine Version class based on cfg settings.

    :return: A subclass of AbstractVersion
    :raises SpinnMachineException: If the cfg version is not set correctly
    """
    # Delayed import to avoid circular imports
    # pylint: disable=import-outside-toplevel
    from .version_3 import Version3
    from .version_5 import Version5
    from .version_201 import Version201

    version = get_config_int_or_none("Machine", "version")
    versions = get_config_str_or_none("Machine", "versions")
    if versions is not None:
        if version is not None:
            raise SpinnMachineException(
                f"Both {version=} and {versions=} found in cfg")
        vs = VersionStrings.from_String(versions)
        options = vs.options
        # Use the fact that we run actions against different python versions
        minor = sys.version_info.minor
        version = options[minor % len(options)]

    if version in [2, 3]:
        return Version3()

    if version in [4, 5]:
        return Version5()

    if version == 201:
        return Version201()

    spalloc_server = get_config_str_or_none("Machine", "spalloc_server")
    if spalloc_server is not None:
        return Version5()

    remote_spinnaker_url = get_config_str_or_none(
        "Machine", "remote_spinnaker_url")
    if remote_spinnaker_url is not None:
        return Version5()

    height = get_config_int_or_none("Machine", "height")
    width = get_config_int_or_none("Machine", "width")
    if height is not None and width is not None:
        logger.info("Your cfg file does not have a version")
        if height == width == 2:
            return Version3()
        elif height == width == 1:
            return Version201()
        return Version5()

    if version is None:
        raise SpinnMachineException("cfg [Machine]version {version} is None")

    raise SpinnMachineException(f"Unexpected cfg [Machine]version {version}")
