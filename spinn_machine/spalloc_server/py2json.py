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
from typing import Dict, List

from argparse import ArgumentParser
import json
from collections import defaultdict


from spinn_machine.spalloc_server import configuration, coordinates
from spinn_machine.spalloc_server.configuration import (
    Configuration, MachineConfig)


def _parse_config(config_file_contents: str) -> Dict:
    g: Dict = {}
    g.update(configuration.__dict__)
    g.update(coordinates.__dict__)
    exec(config_file_contents, g)  # pylint: disable=exec-used
    return g


def _validate_config(parsed_config: Dict) -> Configuration:
    new = parsed_config.get("configuration", None)
    if new is None or not isinstance(new, Configuration):
        raise ValueError("Missing configuration object in parsed config")
    return new


def read_config_file(config_filename: str) -> Configuration:
    """
    Read the server configuration.

    :return: The read configuration
    """
    with open(config_filename, "r", encoding="utf-8") as f:
        config_script = f.read()

    parsed_config = _parse_config(config_script)
    return _validate_config(parsed_config)


def gather_links(machine: MachineConfig) -> Dict[str, List[str]]:
    """
    Gather the links for a machine.

    :param machine: The machine to gather links for
    :return: A dictionary of links keyed by their string representation
    """
    links = defaultdict(list)
    for (x, y, z, lnk) in machine.dead_links:
        key = f"[x={x},y={y},z={z}]"
        links[key].append(lnk)
    return links


def convert_config_to_json(config_file: str, output_file: str) -> None:
    """
    Convert the configuration to JSON.

    :param config_file: The configuration file to convert
    :param output_file: The file to write the JSON to
    """
    config = read_config_file(config_file)

    output = {
        "machines": [{
                "name": machine.name,
                "tags": list(machine.tags),
                "width": machine.width,
                "height": machine.height,
                "dead-boards": [
                    {"x": x, "y": y, "z": z}
                    for (x, y, z) in machine.dead_boards],
                "dead-links": gather_links(machine),
                "board-locations": {
                    f"[x:{x},y:{y},z:{z}]": {"c": c, "f": f, "b": b}
                    for (x, y, z), (c, f, b)
                    in machine.board_locations.items()},
                "bmp-ips": {
                    f"[c:{c},f:{f}]": ip
                    for (c, f), ip in machine.bmp_ips.items()},
                "spinnaker-ips": {
                    f"[x:{x},y:{y},z:{z}]": ip
                    for (x, y, z), ip in machine.spinnaker_ips.items()},
            } for machine in config.machines],
        "port": config.port,
        "ip": config.ip_address,
        "timeout-check-interval": config.timeout_check_interval,
        "max-retired-jobs": config.max_retired_jobs,
        "seconds-before-free": config.seconds_before_free}
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(output))


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Read a configuration file and print it as JSON")
    parser.add_argument(
        "config_file", type=str, help="The configuration file to read")
    parser.add_argument(
        "output_file", type=str, help="The file to write the JSON to")

    args = parser.parse_args()
    convert_config_to_json(args.config_file, args.output_file)
