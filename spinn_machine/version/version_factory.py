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

from spinn_utilities.config_holder import get_config_int
from spinn_machine.exceptions import SpinnMachineException
from .version_3 import Version3
from .version_5 import Version5


def version_factory():
    """
    Creates a Machine Version class based on cfg settings.

    :return: A superclass of AbstractVersion
    :rtype:  ~spinn_machine.version.abstract_version.py
    :raises SpinnMachineException: If the cfg version is not set correctly
    """
    version = get_config_int("Machine", "version")
    if version in [2, 3]:
        return Version3()
    elif version in [4, 5]:
        return Version5()
    elif version is None:
        # TODO raise an error once unittest set cfg
        return Version5()
    else:
        return SpinnMachineException("Unexpected cfg [Machine]version")
