# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinn_machine import CoreSubset


def test_coresubset():
    core_subset = CoreSubset(0, 0, [1, 2, 3])
    assert len(core_subset) == 3
    assert core_subset.x == 0
    assert core_subset.y == 0
    assert 2 in core_subset

    core_subset.add_processor(3)
    assert len(core_subset) == 3

    core_subset.add_processor(4)
    assert len(core_subset) == 4

    assert list(core_subset.processor_ids) == [1, 2, 3, 4]
    assert core_subset.__repr__() == ("0:0:OrderedSet([1, 2, 3, 4])")


def test_equals():
    core_subset = CoreSubset(0, 0, [1, 2, 3])
    assert core_subset == CoreSubset(0, 0, [1, 2, 3])
    assert core_subset != CoreSubset(0, 1, [1, 2, 3])
    assert core_subset != CoreSubset(0, 0, [1])
    assert core_subset != "oops"


def test_in_dict():
    cs1 = CoreSubset(0, 0, [1, 2, 3])
    cs2 = CoreSubset(0, 0, [4, 5, 6])
    cs3 = CoreSubset(0, 1, [1, 2, 3])
    cs4 = CoreSubset(0, 0, [1, 2, 3])
    cs5 = CoreSubset(0, 0, [1, 2, 3, 4])
    d = {}
    d[cs1] = 1
    d[cs2] = 2
    d[cs3] = 3
    d[cs4] = 4
    d[cs5] = 4
    assert len(d) == 4
