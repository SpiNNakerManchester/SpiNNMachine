# Copyright (c) 2014 The University of Manchester
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
from typing import Dict
from .exceptions import SpinnMachineInvalidParameterException

non_monitor: Dict[int, 'Processor'] = dict()
monitor: Dict[int, 'Processor'] = dict()


class Processor(object):
    """
    A processor object included in a SpiNNaker chip.
    """

    CLOCK_SPEED = 200 * 1000 * 1000
    DTCM_AVAILABLE = 2 ** 16

    __slots__ = (
        "_processor_id", "_clock_speed", "_is_monitor", "_dtcm_available"
    )

    def __init__(self, processor_id: int,
                 clock_speed: int = CLOCK_SPEED,
                 is_monitor: bool = False,
                 dtcm_available: int = DTCM_AVAILABLE):
        """
        :param int processor_id:
            ID of the processor in the chip
        :param int clock_speed:
            The number of CPU cycles per second of the processor
        :param bool is_monitor:
            Determines if the processor is considered the
            monitor processor, and so should not be otherwise allocated
        :param int dtcm_available:
            Data Tightly Coupled Memory available
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:
            If the clock speed is negative
        """

        if clock_speed < 0:
            raise SpinnMachineInvalidParameterException(
                "clock_speed", str(clock_speed),
                "Clock speed cannot be less than 0")

        self._processor_id = processor_id
        self._clock_speed = clock_speed
        self._is_monitor = is_monitor
        self._dtcm_available = dtcm_available

    @property
    def processor_id(self) -> int:
        """
        The ID of the processor.

        :rtype: int
        """
        return self._processor_id

    @property
    def dtcm_available(self) -> int:
        """
        The amount of DTCM available on this processor.

        :rtype: int
        """
        return self._dtcm_available

    @property
    def cpu_cycles_available(self) -> int:
        """
        The number of CPU cycles available from this processor per ms.

        :rtype: int
        """
        return self._clock_speed // 1000

    @property
    def clock_speed(self) -> int:
        """
        The clock speed of the processor in cycles per second.

        :rtype: int
        """
        return self._clock_speed

    @property
    def is_monitor(self) -> bool:
        """
        Determines if the processor is the monitor, and therefore not
        to be allocated.

        .. warning::
            Currently rejection processors are also marked as monitors.

        :rtype: bool
        """
        return self._is_monitor

    def __str__(self) -> str:
        return (
            f"[CPU: id={self._processor_id}, "
            f"clock_speed={self._clock_speed // 1000000} MHz, "
            f"monitor={self._is_monitor}]")

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def factory(processor_id: int, is_monitor: bool = False) -> 'Processor':
        """
        Retrieves or creates a Processor with this id and monitor setting

        To keep the memory usage down this class keeps a cache of
        Processor objects and reuses these as much as possible.

        :param int processor_id:
        :param bool is_monitor:
        :rtype: Processor
        """
        if is_monitor:
            if processor_id not in monitor:
                monitor[processor_id] = Processor(
                    processor_id, is_monitor=is_monitor)
            return monitor[processor_id]
        else:
            if processor_id not in non_monitor:
                non_monitor[processor_id] = Processor(
                    processor_id, is_monitor=is_monitor)
            return non_monitor[processor_id]
