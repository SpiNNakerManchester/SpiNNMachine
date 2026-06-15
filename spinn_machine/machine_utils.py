# Copyright (c) 2026 The University of Manchester
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
# limitations under the L

from typing import Optional
from spinn_utilities.config_holder import get_config_str_or_none
from spinn_machine.data import MachineDataView
from spinn_machine.version.version_spin2 import VersionSpin2


SPINNAKERTEAM = "spinnakerusers@googlegroups.com"
SPINNCLOUD = "info@spinncloud.com"


def _contact_email_by_cfg(option: str) -> Optional[str]:
    config = get_config_str_or_none("Machine", option)
    if config:
        if "man.ac.uk" in config:
            return SPINNAKERTEAM
        if "manchester.ac.uk" in config:
            return SPINNAKERTEAM
    return None


def contact_email() -> str:
    """
    The best contact email address depending on the cfg settings

    :return: the best email or emails for users to contact
    """
    email = _contact_email_by_cfg("spalloc_server")
    if email:
        return email
    email = _contact_email_by_cfg("remote_spinnaker_url")
    if email:
        return email

    try:
        version = MachineDataView.get_machine_version()
        if isinstance(version, VersionSpin2):
            return SPINNCLOUD
        else:
            return SPINNAKERTEAM
    except Exception:
        return SPINNAKERTEAM + " or " + SPINNCLOUD
