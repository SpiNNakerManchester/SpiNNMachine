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

from spinn_machine.spalloc_server.configuration import Machine, Configuration
from spinn_machine.spalloc_server.links import Links

m = Machine(name="my-three-board-machine",
            board_locations={
                # X  Y  Z    C  F  B
                (0, 0, 0): (0, 0, 0),
                (0, 0, 1): (0, 0, 2),
                (0, 0, 2): (0, 0, 5),
            },
            # Just one BMP
            bmp_ips={
                # C  F
                (0, 0): "192.168.240.0",
            },
            # Each SpiNNaker board has an IP
            spinnaker_ips={
                # X  Y  Z
                (0, 0, 0): "192.168.240.1",
                (0, 0, 1): "192.168.240.17",
                (0, 0, 2): "192.168.240.41",
            },
            dead_links=frozenset([
                # X  Y  Z  Direction
                (0, 0, 0, Links.east)
            ]))
configuration = Configuration(machines=[m])
