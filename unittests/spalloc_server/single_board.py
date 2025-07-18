# Copyright (c) 2025 The University of Manchester
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

from spinn_machine.spalloc_server.configuration import (
    MachineConfig, Configuration)

m = MachineConfig.single_board("my-board",
                               bmp_ip="192.168.0.2",
                               spinnaker_ip="192.168.0.3")

configuration = Configuration(machines=[m])
