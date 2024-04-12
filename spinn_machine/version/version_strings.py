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

from enum import StrEnum
from typing import List
from spinn_machine.exceptions import SpinnMachineException


class VersionStrings(StrEnum):
    """
    A description of strings in cfg settings to say test versions

    As additional Versions are added this should allow easy testing of these
    as far as possible.
    """

    ANY = ("Any", [3, 5, 201])
    FOUR_PLUS = ("Four plus", [3, 5])
    # To test stuff with more than four chips.
    BIG = ("Big", [5])
    # Specifically to test stuff over multiple boards
    MULTIPLE_BOARDS = ("Multiple boards", [5])
    # Specifically to test the various wrapping Machine classes
    WRAPPABLE = ("Wrappable", [5])

    def __new__(cls, *args, **kwds):
        s = str.__new__(cls)
        s._value_ = args[0]
        return s

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, versions: List[int]):
        self._versions = versions

    def __str__(self):
        return self.value

    @property
    def short_str(self):
        return self.shorten(self.value)

    # this makes sure that the description is read-only
    @property
    def options(self) -> List[int]:
        return self._versions

    @classmethod
    def shorten(cls, value):
        return value.lower().replace("_", "").replace("-", "").replace(" ", "")

    @classmethod
    def from_String(cls, value):
        value_short = cls.shorten(value)
        for vs in cls:
            if value_short == vs.short_str:
                return vs
        raise SpinnMachineException(f"No version for {value=}")
