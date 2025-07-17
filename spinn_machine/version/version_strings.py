# Copyright (c) 2024 The University of Manchester
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

from enum import Enum
from typing import List, Tuple
from typing_extensions import Self
from spinn_machine.exceptions import SpinnMachineException


class VersionStrings(Enum):
    """
    A description of strings in cfg settings to say test versions

    As additional Versions are added this should allow easy testing of these
    as far as possible.
    """

    ANY = (1, "Any", [3, 5, 201, 248])
    FOUR_PLUS = (2, "Four plus", [3, 5, 248])
    # To test stuff with more than four chips.
    BIG = (3, "Big", [5, 248])
    # Tests that specifically require 8 by 8 board(s)
    # Could be changed but not worth the effort until needed
    EIGHT_BY_EIGHT = (5, "eight by eigth", [5, 248])
    # Tests for 8 by 8 boards with FPGAs defined
    WITH_FPGAS = (6, "with fpgas", [5])

    def __new__(cls, *args: Tuple[int, str, List[int]],  **kwds: None) -> Self:
        vs = object.__new__(cls)
        vs._value_ = args[0]
        return vs

    def __init__(self, value: int, text: str, versions: List[int]):
        """
        :param value: enum ID for this version
        :param text: label for this enum
        :param versions: machine versions that this group includes
        """
        # ignore the first param since it's already set by __new__
        _ = value
        self.text = text
        self._versions = versions

    def __str__(self) -> str:
        return self.text

    @property
    def short_str(self) -> str:
        """
        The text but in a shortened version

        This makes the text lower case and removes some special characters
        """
        return self.shorten(self.text)

    # this makes sure that the description is read-only
    @property
    def options(self) -> List[int]:
        """
        The list of the versions covered by this string

        This list can grow as new versions are added
        """
        return self._versions

    @classmethod
    def shorten(cls, value: str) -> str:
        """
        Makes the String lower case and removes some special characters

        :param value: original string
        :returns: original in lower case and without special characters
        """
        return value.lower().replace("_", "").replace("-", "").replace(" ", "")

    @classmethod
    def from_string(cls, value: str) -> "VersionStrings":
        """
        Gets a VersionString object from a String

        :param value: label
        :returns: VersionStrings Enum with this label
        """
        value_short = cls.shorten(value)
        for vs in cls:
            if value_short == vs.short_str:
                return vs
        raise SpinnMachineException(f"No version for {value=}")
