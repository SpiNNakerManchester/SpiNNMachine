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

import logging
from spinn_utilities.config_holder import (
    get_config_int_or_none, get_config_str_or_none)
from spinn_utilities.log import FormatAdapter
from spinn_machine.exceptions import SpinnMachineException

logger = FormatAdapter(logging.getLogger(__name__))


def version_factory():
    """
    Creates a Machine Version class based on cfg settings.

    :return: A superclass of AbstractVersion
    :rtype:  ~spinn_machine.version.abstract_version.py
    :raises SpinnMachineException: If the cfg version is not set correctly
    """
    # Delayed import to avoid circular imports
    from .version_3 import Version3
    from .version_5 import Version5

    version = get_config_int_or_none("Machine", "version")
    if version in [2, 3]:
        return Version3()

    if version in [4, 5]:
        return Version5()

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
        if height == width == 2:
            logger.info("Your cfg file does not have a ")
            return Version3()
        return Version5()

    if version is None:
        raise SpinnMachineException("cfg [Machine]version {version} is None")

    raise SpinnMachineException(f"Unexpected cfg [Machine]version {version}")
