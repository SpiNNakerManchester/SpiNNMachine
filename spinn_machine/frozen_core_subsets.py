# Copyright (c) 2023 The University of Manchester
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

from typing import Dict, Iterable
from spinn_utilities.typing.coords import XY
from spinn_utilities.overrides import overrides
from .core_subset import CoreSubset
from .core_subsets import CoreSubsets


class FrozenCoreSubsets(CoreSubsets):
    """
    Represents a frozen group of CoreSubsets, with a maximum of one per
    SpiNNaker chip.
    """

    # pylint: disable=super-init-not-called
    def __init__(self, core_subsets: Iterable[CoreSubset] = ()):
        """
        :param core_subsets:
            The cores for each desired chip
        """
        self._core_subsets: Dict[XY, CoreSubset] = dict()
        # Do the load here so that the blocked add_processor is not called
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            for processor_id in core_subset.processor_ids:
                super().add_processor(x, y, processor_id)

    @overrides(CoreSubsets.add_core_subset)
    def add_core_subset(self, core_subset: CoreSubset) -> None:
        raise RuntimeError("This object is immutable")

    @overrides(CoreSubsets.add_core_subsets)
    def add_core_subsets(self, core_subsets: Iterable[CoreSubset]) -> None:
        raise RuntimeError("This object is immutable")

    @overrides(CoreSubsets.add_processor)
    def add_processor(self, x: int, y: int, processor_id: int) -> None:
        raise RuntimeError("This object is immutable")
