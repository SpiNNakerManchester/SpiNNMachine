# Copyright (c) 2017 The University of Manchester
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
from .coordinates import chip_to_board


def _empty_default_dict(d):
    return dict(d) if d is not None else {}


class Configuration(namedtuple("Configuration",
                               "machines,port,ip,timeout_check_interval,"
                               "max_retired_jobs,seconds_before_free")):
    def __new__(cls, machines=None, port=22244, ip="",
                timeout_check_interval=5.0,
                max_retired_jobs=1200,
                seconds_before_free=30):
        # pylint: disable=too-many-arguments

        # Validate machine definitions
        used_names = set()
        used_bmp_ips = set()
        used_spinnaker_ips = set()
        machines = list([] if machines is None else machines)
        for m in machines:
            # Typecheck...
            if not isinstance(m, Machine):
                raise TypeError("All machines must be of type Machine.")

            # Machine names must be unique
            if m.name in used_names:
                raise ValueError("Machine name '{}' used multiple "
                                 "times.".format(m.name))
            used_names.add(m.name)

            # All BMP IPs must be unique
            for bmp_ip in m.bmp_ips.values():
                if bmp_ip in used_bmp_ips:
                    raise ValueError("BMP IP '{}' used multiple "
                                     "times.".format(bmp_ip))
                used_bmp_ips.add(bmp_ip)

            # All SpiNNaker IPs must be unique
            for spinnaker_ip in m.spinnaker_ips.values():
                if spinnaker_ip in used_spinnaker_ips:
                    raise ValueError("SpiNNaker IP '{}' used multiple "
                                     "times.".format(spinnaker_ip))
                used_spinnaker_ips.add(spinnaker_ip)

        return super(Configuration, cls).__new__(
            cls, machines, port, ip, timeout_check_interval, max_retired_jobs,
            seconds_before_free)


class Machine(namedtuple("Machine", "name,tags,width,height,"
                                    "dead_boards,dead_links,"
                                    "board_locations,"
                                    "bmp_ips,spinnaker_ips")):
    def __new__(cls, name, tags=frozenset(["default"]),
                width=None, height=None,
                dead_boards=frozenset(), dead_links=frozenset(),
                board_locations=None, bmp_ips=None, spinnaker_ips=None):
        # pylint: disable=too-many-arguments

        # Make sure the set-type arguments are the correct type...
        if not isinstance(tags, (set, frozenset)):
            raise TypeError("tags should be a set.")
        if not isinstance(dead_boards, (set, frozenset)):
            raise TypeError("dead_boards should be a set.")
        if not isinstance(dead_links, (set, frozenset)):
            raise TypeError("dead_links should be a set.")

        board_locations = _empty_default_dict(board_locations)
        bmp_ips = _empty_default_dict(bmp_ips)
        spinnaker_ips = _empty_default_dict(spinnaker_ips)

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
                raise ValueError("Dead board ({}, {}, {}) "
                                 "outside system.".format(x, y, z))
        for x, y, z, _ in dead_links:
            if not (0 <= x < width and
                    0 <= y < height and
                    0 <= z < 3):
                raise ValueError("Dead link ({}, {}, {}) "
                                 "outside system.".format(x, y, z))

        # All board locations must be sensible
        locations = set()
        for (x, y, z), (c, f, b) in board_locations.items():
            # Board should be within system
            if not (0 <= x < width and
                    0 <= y < height and
                    0 <= z < 3):
                raise ValueError("Board location given for board "
                                 "not in system ({}, {}, {}).".format(x, y, z))
            # No two boards should be in the same location
            if (c, f, b) in locations:
                raise ValueError("Multiple boards given location "
                                 "c:{}, f:{}, b:{}.".format(c, f, b))
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
                "Board locations missing for {}".format(missing_boards))

        # BMP IPs should be given for all frames which have been used
        missing_bmp_ips = set((c, f) for c, f, _ in locations) - set(bmp_ips)
        if missing_bmp_ips:
            raise ValueError(
                "BMP IPs not given for frames {}".format(missing_bmp_ips))

        # SpiNNaker IPs should be given for all live boards
        missing_ips = live_bords - set(spinnaker_ips)
        if missing_ips:
            raise ValueError(
                "SpiNNaker IPs not given for boards {}".format(missing_ips))

        return super(Machine, cls).__new__(
            cls, name, tags, width, height, frozenset(dead_boards),
            frozenset(dead_links), board_locations, bmp_ips, spinnaker_ips)

    @classmethod
    def single_board(cls, name, tags=frozenset(["default"]),
                     bmp_ip=None, spinnaker_ip=None):
        if bmp_ip is None:
            raise TypeError("bmp_ip must be given.")
        if spinnaker_ip is None:
            raise TypeError("spinnaker_ip must be given.")

        return cls(
            name, tags, 1, 1, dead_boards=set([(0, 0, 1), (0, 0, 2)]),
            dead_links=set(), board_locations={(0, 0, 0): (0, 0, 0)},
            bmp_ips={(0, 0): bmp_ip}, spinnaker_ips={(0, 0, 0): spinnaker_ip})

    @classmethod
    def with_standard_ips(cls, name, tags=frozenset(["default"]),
                          width=None, height=None,
                          dead_boards=frozenset(), dead_links=frozenset(),
                          board_locations=None,
                          base_ip="192.168.0.0",
                          cabinet_stride="0.0.5.0",
                          frame_stride="0.0.1.0",
                          board_stride="0.0.0.8",
                          bmp_offset="0.0.0.0",
                          spinnaker_offset="0.0.0.1"):
        # pylint: disable=too-many-arguments

        def ip_to_int(ip):
            """ Convert from string-based IP to a 32-bit integer.
            """
            match = re.match(r"^(\d+).(\d+).(\d+).(\d+)$", ip)
            if not match:
                raise ValueError("Malformed IPv4 address '{}'".format(ip))

            ip_int = 0
            for group in map(int, match.groups()):
                if group & ~0xFF:
                    raise ValueError("Malformed IPv4 address '{}'".format(ip))
                ip_int <<= 8
                ip_int |= group

            return ip_int

        def int_to_ip(ip_int):
            """ Convert from 32-bit integer to string-based IP address.
            """
            return ".".join(str((ip_int >> b) & 0xFF)
                            for b in range(24, -8, -8))

        base_ip = ip_to_int(base_ip)
        cabinet_stride = ip_to_int(cabinet_stride)
        frame_stride = ip_to_int(frame_stride)
        board_stride = ip_to_int(board_stride)
        bmp_offset = ip_to_int(bmp_offset)
        spinnaker_offset = ip_to_int(spinnaker_offset)
        board_locations = _empty_default_dict(board_locations)

        # Generate IP addresses for BMPs
        cabinets_and_frames = set(
            (c, f) for c, f, _ in board_locations.values())
        bmp_ips = {
            (c, f): int_to_ip(base_ip + (cabinet_stride * c) +
                              (frame_stride * f) + bmp_offset)
            for (c, f) in cabinets_and_frames}

        # Generate IP addresses for SpiNNaker boards
        spinnaker_ips = {
            (x, y, z): int_to_ip(base_ip + (cabinet_stride * c) +
                                 (frame_stride * f) + (board_stride * b) +
                                 spinnaker_offset)
            for (x, y, z), (c, f, b) in board_locations.items()}

        return cls(name, set(tags), width, height,
                   dead_boards=set(dead_boards), dead_links=set(dead_links),
                   board_locations=dict(board_locations),
                   bmp_ips=bmp_ips, spinnaker_ips=spinnaker_ips)


def board_locations_from_spinner(filename):
    # Extract lookup from Ethernet connected chips to locations
    chip_locations = {}
    with open(filename, "r") as f:
        for entry in csv.DictReader(f):
            cfb = tuple(map(int, (entry["cabinet"],
                                  entry["frame"],
                                  entry["board"])))

            chip_xy = (int(entry["x"]), int(entry["y"]))

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
