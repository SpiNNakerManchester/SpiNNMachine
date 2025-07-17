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
from os import chdir
import os.path
from spinn_machine.spalloc_server.py2json import (
    read_config_file, convert_config_to_json)
from spinn_machine.spalloc_server.links import Links
import json
import deepdiff


def test_single_board():
    class_file = str(__file__)
    path = os.path.dirname(os.path.abspath(class_file))
    config = read_config_file(os.path.join(path, "single_board.py"))
    assert config.machines is not None
    assert len(config.machines) == 1
    machine = config.machines[0]
    assert machine is not None
    assert machine.name == "my-board"
    assert len(machine.board_locations) == 1
    assert len(machine.bmp_ips) == 1
    assert len(machine.spinnaker_ips) == 1
    assert machine.width == 1
    assert machine.height == 1
    assert machine.dead_boards == {(0, 0, 1), (0, 0, 2)}
    assert machine.bmp_ips[0, 0] == "192.168.0.2"
    assert machine.board_locations[(0, 0, 0)] == (0, 0, 0)
    assert machine.spinnaker_ips[0, 0, 0] == "192.168.0.3"


def test_three_boards():
    class_file = str(__file__)
    path = os.path.dirname(os.path.abspath(class_file))
    config = read_config_file(os.path.join(path, "three_board.py"))
    assert config.machines is not None
    assert len(config.machines) == 1
    machine = config.machines[0]
    assert machine.dead_links == {(0, 0, 0, Links.east)}


def test_from_csv():
    class_file = str(__file__)
    path = os.path.dirname(os.path.abspath(class_file))
    chdir(path)
    config = read_config_file(os.path.join(path, "from_csv.py"))
    assert config.machines is not None
    assert len(config.machines) == 1
    machine = config.machines[0]
    assert machine is not None
    assert machine.name == "SpiNNaker1M"
    assert machine.width == 1
    assert machine.height == 1
    assert len(machine.board_locations) == 3
    assert machine.board_locations == {
        (0, 0, 0): (0, 0, 0),
        (0, 0, 1): (0, 0, 2),
        (0, 0, 2): (0, 0, 1)}
    assert len(machine.bmp_ips) == 1
    assert machine.spinnaker_ips == {
        (0, 0, 0): "10.11.193.1",
        (0, 0, 1): "10.11.193.17",
        (0, 0, 2): "10.11.193.9"}


def test_to_json():
    class_file = str(__file__)
    path = os.path.dirname(os.path.abspath(class_file))
    config_file = os.path.join(path, "single_board.py")
    output_file = os.path.join(path, "single_board.json")
    convert_config_to_json(config_file, output_file)

    expected_file = os.path.join(path, "expected.json")
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_output = json.load(f)
    with open(output_file, "r", encoding="utf-8") as f:
        actual_output = json.load(f)
    diff = deepdiff.DeepDiff(expected_output, actual_output)
    assert diff.get('values_changed', {}) == {}
