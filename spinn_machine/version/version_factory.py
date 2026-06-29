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
from typing import Optional, TYPE_CHECKING
import os

from typing_extensions import Never

from spinn_utilities.config_holder import (
    check_user_cfg, get_config_bool, get_config_int_or_none,
    get_config_str_or_none, has_config_option)
from spinn_utilities.log import FormatAdapter
from spinn_machine.exceptions import SpinnMachineException
from .spin1_gen import Spin1Gen
from .spin2_gen import Spin2Gen

if TYPE_CHECKING:
    from .abstract_version import AbstractVersion

logger = FormatAdapter(logging.getLogger(__name__))

ALL_BOARD_TYPES = [["THREE", str(Spin1Gen.THREE.value)],
                   ["FIVE", str(Spin1Gen.FIVE.value)],
                   ["SPIN2_1CHIP", str(Spin2Gen.SPIN2_1CHIP.value)],
                   ["SPIN2_48CHIP", str(Spin2Gen.SPIN2_48CHIP.value)]]
FOUR_PLUS_BOARD_TYPES = [["THREE", str(Spin1Gen.THREE.value)],
                         ["FIVE", str(Spin1Gen.FIVE.value)],
                         ["SPIN2_48CHIP", str(Spin2Gen.SPIN2_48CHIP.value)]]
BIG_BOARD_TYPES = [["FIVE", str(Spin1Gen.FIVE.value)],
                   ["SPIN2_48CHIP", str(Spin2Gen.SPIN2_48CHIP.value)]]
FPGA_BOARD_TYPES = [["FIVE", str(Spin1Gen.FIVE.value)]]
if os.environ.get("SPINNAKER_TEST_ALL") == "true":
    MANY_BOARD_TYPES = ALL_BOARD_TYPES
else:
    MANY_BOARD_TYPES = BIG_BOARD_TYPES


def version_factory() -> AbstractVersion:
    """
    Creates a Machine Version class based on cfg settings.

    :return: A subclass of AbstractVersion
    :raises SpinnMachineException: If the cfg version is not set correctly
    """
    cfg_version = _get_cfg_version()
    url_version = _get_url_version()
    size_version = _get_size_version()

    version: Optional[AbstractVersion] = None
    if cfg_version is None:
        if url_version is None:
            version = None
        else:
            version = _number_to_version(url_version)
    else:
        if url_version is None:
            version = _number_to_version(cfg_version)
        else:
            version_cfg = _number_to_version(cfg_version)
            version_url = _number_to_version(url_version)
            if version_cfg == version_url:
                version = version_cfg
            else:
                raise_version_error("Incorrect version", cfg_version)

    if size_version is None:
        if version is None:
            raise_version_error("No version", None)
        else:
            return version
    else:
        if version is None:
            logger.warning("Please add a version to your cfg file.")
            return _number_to_version(size_version)
        else:
            version_sized = _number_to_version(size_version)
            if version == version_sized:
                return version
            else:
                raise SpinnMachineException(
                    "cfg width and height do not match other cfg setting.")
    raise SpinnMachineException("Should not get here")


def _get_cfg_version() -> Optional[int]:
    version = get_config_int_or_none("Machine", "version")
    if has_config_option("Machine", "versions"):
        raise SpinnMachineException(
            "versions in cfg is no longer supported.")
    if version is None:
        logger.warning(
            "The cfg has no version. This is deprecated! Please add a version")
    return version


def _get_url_version() -> Optional[int]:
    spalloc_server = get_config_str_or_none("Machine", "spalloc_server")
    remote_spinnaker_url = get_config_str_or_none(
        "Machine", "remote_spinnaker_url")
    machine_name = get_config_str_or_none("Machine", "machine_name")
    virtual_board = get_config_bool("Machine", "virtual_board")

    if spalloc_server is not None:
        if remote_spinnaker_url is not None:
            raise SpinnMachineException(
                "Both spalloc_server and remote_spinnaker_url "
                "specified in cfg")
        if machine_name is not None:
            raise SpinnMachineException(
                "Both spalloc_server and machine_name specified in cfg")
        if virtual_board:
            raise SpinnMachineException(
                "Both spalloc_server and virtual_board specified in cfg")
        return 5

    if remote_spinnaker_url is not None:
        if machine_name is not None:
            raise SpinnMachineException(
                "Both remote_spinnaker_url and machine_name specified in cfg")
        if virtual_board:
            raise SpinnMachineException(
                "Both remote_spinnaker_url and virtual_board specified in cfg")
        return 5

    if machine_name is not None:
        if virtual_board:
            raise SpinnMachineException(
                "Both machine_name and virtual_board specified in cfg")

    return None


def _get_size_version() -> Optional[int]:
    height = get_config_int_or_none("Machine", "height")
    width = get_config_int_or_none("Machine", "width")
    if height is None:
        if width is None:
            return None
        else:
            raise SpinnMachineException("cfg has width but not height")
    else:
        if width is None:
            raise SpinnMachineException("cfg has height but not width")
        else:
            if height == width == 2:
                return 3
            elif height == width == 1:
                return 201
            # if width and height are valid checked later
            return 5


def _number_to_version(version: int) -> AbstractVersion:
    # Delayed import to avoid circular imports
    # pylint: disable=import-outside-toplevel
    from .version_3 import Version3
    from .version_5 import Version5
    from .version_201 import Version201
    from .version_248 import Version248

    if version in [2, Spin1Gen.THREE.value]:
        return Version3()

    if version in [4, Spin1Gen.FIVE.value]:
        return Version5()

    if version == Spin2Gen.SPIN2_1CHIP.value:
        return Version201()

    if version == Spin2Gen.SPIN2_48CHIP.value:
        return Version248()

    raise SpinnMachineException(f"Unexpected cfg [Machine]version {version}")


def raise_version_error(error: str, version: Optional[int]) -> Never:
    """
    Collects main cfg values and raises an exception

    :param error: message for the exception
    :param version: version claimed
    :raises SpinnMachineException: Always!
    """
    check_user_cfg()
    height = get_config_int_or_none("Machine", "height")
    width = get_config_int_or_none("Machine", "width")

    spalloc_server = get_config_str_or_none("Machine",
                                            "spalloc_server")
    remote_spinnaker_url = get_config_str_or_none(
        "Machine", "remote_spinnaker_url")
    machine_name = get_config_str_or_none("Machine", "machine_name")
    virtual_board = get_config_bool("Machine", "virtual_board")
    raise SpinnMachineException(
        f"{error} with cfg [Machine] values {version=}, "
        f"{machine_name=}, {spalloc_server=}, {remote_spinnaker_url=}, "
        f"{virtual_board=}, {width=}, and {height=}")
