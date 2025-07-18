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
from collections import namedtuple
import re
import csv
from itertools import chain
from typing import List, Set, Optional, Tuple, Dict, FrozenSet
from .links import Links
from .coordinates import chip_to_board


class Configuration(namedtuple(
        "Configuration", "machines,port,ip_address,timeout_check_interval,"
                         "max_retired_jobs,seconds_before_free")):
    """
    A configuration for the spalloc server, containing a list of machines and
    various parameters for the server.
    """

    def __new__(cls, machines: Optional[List["MachineConfig"]] = None,
                port: int = 22244, ip_address: str = "",
                timeout_check_interval: float = 5.0,
                max_retired_jobs: int = 1200,
                seconds_before_free: int = 30) -> "Configuration":
        """

        :param machines: A list of Machine objects describing the machines
        :param port: The port on which the server will listen
        :param ip_address: The IP address on which the server will listen
        :param timeout_check_interval: How often to check for timeouts
        :param max_retired_jobs: The maximum number of retired jobs to keep
        :param seconds_before_free: How long to wait before freeing an idle job
        """
        # pylint: disable=too-many-arguments

        # Validate machine definitions
        used_names: Set[str] = set()
        used_bmp_ips: Set[str] = set()
        used_spinnaker_ips: Set[str] = set()
        machines = list([] if machines is None else machines)
        for m in machines:
            if not isinstance(m, MachineConfig):
                raise TypeError("All machines must be of type Machine.")

            # Machine names must be unique
            if m.name in used_names:
                raise ValueError(
                    f"Machine name '{m.name}' used multiple times.")
            used_names.add(m.name)

            # All BMP IPs must be unique
            for bmp_ip in m.bmp_ips.values():
                if bmp_ip in used_bmp_ips:
                    raise ValueError(f"BMP IP '{bmp_ip}' used multiple times.")
                used_bmp_ips.add(bmp_ip)

            # All SpiNNaker IPs must be unique
            for spinnaker_ip in m.spinnaker_ips.values():
                if spinnaker_ip in used_spinnaker_ips:
                    raise ValueError(
                        f"SpiNNaker IP '{spinnaker_ip}' used multiple times.")
                used_spinnaker_ips.add(spinnaker_ip)

        return super(Configuration, cls).__new__(
            cls, machines, port, ip_address, timeout_check_interval,
            max_retired_jobs, seconds_before_free)


class MachineConfig(namedtuple(
        "MachineConfig", "name,tags,width,height,dead_boards,dead_links,"
                         "board_locations,bmp_ips,spinnaker_ips")):
    """
    A description of a machine, including its dimensions, dead boards and
    links, board locations, and IP addresses for the BMPs and SpiNNaker boards.
    """
    def __new__(
            cls, name: str, tags: FrozenSet[str] = frozenset(["default"]),
            width: Optional[int] = None, height: Optional[int] = None,
            dead_boards: FrozenSet[Tuple[int, int, int]] = frozenset(),
            dead_links: FrozenSet[Tuple[int, int, int, Links]] = frozenset(),
            board_locations: Optional[Dict[Tuple[int, int, int],
                                           Tuple[int, int, int]]] = None,
            bmp_ips: Optional[Dict[Tuple[int, int], str]] = None,
            spinnaker_ips: Optional[Dict[Tuple[int, int, int], str]] = None
            ) -> "MachineConfig":
        """

        :param name: The name of the machine
        :param tags: A set of tags for the machine, used for filtering
        :param width: The width of the machine in triads
        :param height: The height of the machine in triads
        :param dead_boards: A set of dead boards in the machine, given as
            tuples of (x, y, z) coordinates.
        :param dead_links: A set of dead links in the machine, given as
            tuples of (x, y, z, link_type)
        :param board_locations: A dictionary mapping board coordinates
            (x, y, z) to their locations (cabinet, frame, board).
        :param bmp_ips: A dictionary mapping (cabinet, frame) to the BMP IP
            address for that cabinet and frame.
        :param spinnaker_ips: A dictionary mapping (x, y, z) coordinates to
            the SpiNNaker IP address for that board.
        """
        # pylint: disable=too-many-arguments

        # Make sure the set-type arguments are the correct type...
        if not isinstance(tags, (set, frozenset)):
            raise TypeError("tags should be a set.")
        if not isinstance(dead_boards, (set, frozenset)):
            raise TypeError("dead_boards should be a set.")
        if not isinstance(dead_links, (set, frozenset)):
            raise TypeError("dead_links should be a set.")

        board_locations = dict(board_locations) if board_locations else {}
        bmp_ips = dict(bmp_ips) if bmp_ips else {}
        spinnaker_ips = dict(spinnaker_ips) if spinnaker_ips else {}

        # If not specified, infer the dimensions of the system
        if width is None and height is None:
            width, height, _ = map(max, zip(*chain(board_locations,
                                                   dead_boards)))
            width += 1
            height += 1
        if width is None or height is None:
            raise TypeError(
                "Both or neither of width and height must be specified.")

        # All dead boards and links should be within the size of the system
        for x, y, z in dead_boards:
            if not (0 <= x < width and
                    0 <= y < height and
                    0 <= z < 3):
                raise ValueError(f"Dead board ({x}, {y}, {z}) outside system.")
        for x, y, z, _ in dead_links:
            if not (0 <= x < width and
                    0 <= y < height and
                    0 <= z < 3):
                raise ValueError(f"Dead link ({x}, {y}, {z}) outside system.")

        # All board locations must be sensible
        locations = set()
        for (x, y, z), (c, f, b) in board_locations.items():
            # Board should be within system
            if not (0 <= x < width and
                    0 <= y < height and
                    0 <= z < 3):
                raise ValueError("Board location given for board "
                                 f"not in system ({x}, {y}, {z}).")
            # No two boards should be in the same location
            if (c, f, b) in locations:
                raise ValueError("Multiple boards given location "
                                 f"c:{c}, f:{f}, b:{b}.")
            locations.add((c, f, b))

        # All boards must have their locations specified, unless they are
        # dead (in which case this is optional)
        live_bords = set((x, y, z)
                         for x in range(width)
                         for y in range(height)
                         for z in range(3)
                         if (x, y, z) not in dead_boards)
        missing_boards = live_bords - set(board_locations)
        if missing_boards:
            raise ValueError(
                f"Board locations missing for {missing_boards}")

        # BMP IPs should be given for all frames which have been used
        missing_bmp_ips = set((c, f) for c, f, _ in locations) - set(bmp_ips)
        if missing_bmp_ips:
            raise ValueError(
                f"BMP IPs not given for frames {missing_bmp_ips}")

        # SpiNNaker IPs should be given for all live boards
        missing_ips = live_bords - set(spinnaker_ips)
        if missing_ips:
            raise ValueError(
                f"SpiNNaker IPs not given for boards {missing_ips}")

        return super(MachineConfig, cls).__new__(
            cls, name, tags, width, height, frozenset(dead_boards),
            frozenset(dead_links), board_locations, bmp_ips, spinnaker_ips)

    @classmethod
    def single_board(
            cls, name: str, tags: FrozenSet[str] = frozenset(["default"]),
            bmp_ip: Optional[str] = None,
            spinnaker_ip: Optional[str] = None) -> "MachineConfig":
        """
        Create a machine with a single board, with the given BMP and
        SpiNNaker IP addresses.

        :param name: The name of the machine
        :param tags: A set of tags for the machine, used for filtering
        :param bmp_ip: The IP address of the BMP for this machine
        :param spinnaker_ip: The IP address of the SpiNNaker board for this
            machine

        :return: A Machine object representing a single board machine
        """
        if bmp_ip is None:
            raise TypeError("bmp_ip must be given.")
        if spinnaker_ip is None:
            raise TypeError("spinnaker_ip must be given.")

        return cls(
            name, tags, 1, 1, dead_boards=frozenset([(0, 0, 1), (0, 0, 2)]),
            dead_links=frozenset(), board_locations={(0, 0, 0): (0, 0, 0)},
            bmp_ips={(0, 0): bmp_ip}, spinnaker_ips={(0, 0, 0): spinnaker_ip})

    @classmethod
    def with_standard_ips(
            cls, name: str, tags: FrozenSet[str] = frozenset(["default"]),
            width: Optional[int] = None, height: Optional[int] = None,
            dead_boards: FrozenSet[Tuple[int, int, int]] = frozenset(),
            dead_links: FrozenSet[Tuple[int, int, int, Links]] = frozenset(),
            board_locations: Optional[Dict[Tuple[int, int, int],
                                           Tuple[int, int, int]]] = None,
            base_ip: str = "192.168.0.0",
            cabinet_stride: str = "0.0.5.0",
            frame_stride: str = "0.0.1.0",
            board_stride: str = "0.0.0.8",
            bmp_offset: str = "0.0.0.0",
            spinnaker_offset: str = "0.0.0.1") -> "MachineConfig":
        """
        Create a machine with standard IP addresses based on the given
        parameters. The base IP is the starting point for the IP addresses,
        and the other parameters define how the IPs for cabinets, frames,
        boards, BMPs, and SpiNNaker boards are calculated.

        :param name: The name of the machine
        :param tags: A set of tags for the machine, used for filtering
        :param width: The width of the machine in triads
        :param height: The height of the machine in triads
        :param dead_boards: A set of dead boards in the machine, given as
            tuples of (x, y, z) coordinates.
        :param dead_links: A set of dead links in the machine, given as
            tuples of (x, y, z, link_type)
        :param board_locations: A dictionary mapping board coordinates
            (x, y, z) to their locations (cabinet, frame, board).
        :param base_ip: The base IP address for the machine, in dotted decimal
        :param cabinet_stride: The stride for cabinets, in dotted decimal
        :param frame_stride: The stride for frames, in dotted decimal
        :param board_stride: The stride for boards, in dotted decimal
        :param bmp_offset: The offset for BMPs, in dotted decimal
        :param spinnaker_offset: The offset for SpiNNaker boards, in dotted
            decimal
        :return: A Machine object with the specified parameters
        """
        # pylint: disable=too-many-arguments

        def ip_to_int(ip_address: str) -> int:
            """ Convert from string-based IP to a 32-bit integer.

            :param ip_address: The IP address in dotted decimal format
            :return: The IP address as a 32-bit integer
            """
            match = re.match(r"^(\d+).(\d+).(\d+).(\d+)$", ip_address)
            if not match:
                raise ValueError(f"Malformed IPv4 address '{ip_address}'")

            ip_int = 0
            for group in map(int, match.groups()):
                if group & ~0xFF:
                    raise ValueError(f"Malformed IPv4 address '{ip_address}'")
                ip_int <<= 8
                ip_int |= group

            return ip_int

        def int_to_ip(ip_int: int) -> str:
            """ Convert from 32-bit integer to string-based IP address.

            :param ip_int: The IP address as a 32-bit integer
            :return: The IP address in dotted decimal format
            """
            return ".".join(str((ip_int >> b) & 0xFF)
                            for b in range(24, -8, -8))

        base_ip_int = ip_to_int(base_ip)
        cabinet_stride_int = ip_to_int(cabinet_stride)
        frame_stride_int = ip_to_int(frame_stride)
        board_stride_int = ip_to_int(board_stride)
        bmp_offset_int = ip_to_int(bmp_offset)
        spinnaker_offset_int = ip_to_int(spinnaker_offset)
        board_locations = dict(board_locations) if board_locations else {}

        # Generate IP addresses for BMPs
        cabinets_and_frames = set(
            (c, f) for c, f, _ in board_locations.values())
        bmp_ips = {
            (c, f): int_to_ip(base_ip_int + (cabinet_stride_int * c) +
                              (frame_stride_int * f) + bmp_offset_int)
            for (c, f) in cabinets_and_frames}

        # Generate IP addresses for SpiNNaker boards
        spinnaker_ips = {
            (x, y, z): int_to_ip(base_ip_int + (cabinet_stride_int * c) +
                                 (frame_stride_int * f) +
                                 (board_stride_int * b) +
                                 spinnaker_offset_int)
            for (x, y, z), (c, f, b) in board_locations.items()}

        return cls(name, tags, width, height, dead_boards=dead_boards,
                   dead_links=dead_links, board_locations=board_locations,
                   bmp_ips=bmp_ips, spinnaker_ips=spinnaker_ips)


def board_locations_from_spinner(filename: str) -> Dict[Tuple[int, int, int],
                                                        Tuple[int, int, int]]:
    """
    Extract board locations from a CSV file containing Ethernet connected
    chips and their locations.

    :param filename: The path to the CSV file containing the chip locations
    :return: A dictionary mapping board coordinates (x, y, z) to their
             locations (cabinet, frame, board).
    """
    # Extract lookup from Ethernet connected chips to locations
    chip_locations: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
    with open(filename, "r", encoding='utf8') as f:
        for entry in csv.DictReader(f):
            cfb: Tuple[int, int, int] = (
                int(entry["cabinet"]), int(entry["frame"]),
                int(entry["board"]))

            chip_xy: Tuple[int, int] = (int(entry["x"]), int(entry["y"]))

            assert chip_xy not in chip_locations
            chip_locations[chip_xy] = cfb

    # Infer machine dimensions
    max_x, max_y = map(max, zip(*chip_locations))
    width_triads = (max_x // 12) + 1
    height_triads = (max_y // 12) + 1

    # Convert from chip to board coordinates
    return {
        chip_to_board(chip_x, chip_y, width_triads * 12, height_triads * 12):
        cfb
        for (chip_x, chip_y), cfb in chip_locations.items()
    }
