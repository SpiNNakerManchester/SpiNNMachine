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

from .exceptions import SpinnMachineInvalidParameterException

non_monitor = dict()
monitor = dict()


class Processor(object):
    """ A processor object included in a SpiNNaker chip
    """

    CLOCK_SPEED = 200 * 1000 * 1000
    DTCM_AVAILABLE = 2 ** 16

    __slots__ = (
        "_processor_id", "_clock_speed", "_is_monitor", "_dtcm_available"
    )

    def __init__(self, processor_id, clock_speed=CLOCK_SPEED, is_monitor=False,
                 dtcm_available=DTCM_AVAILABLE):
        """
        :param processor_id: ID of the processor in the chip
        :type processor_id: int
        :param clock_speed: \
            The number of CPU cycles per second of the processor
        :type clock_speed: int
        :param is_monitor: Determines if the processor is considered the\
            monitor processor, and so should not be otherwise allocated
        :type is_monitor: bool
        :param dtcm_available: Data Tightly Coupled Memory available
        :type dtcm_available: int
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:\
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
    def processor_id(self):
        """ The ID of the processor

        :return: ID of the processor
        :rtype: int
        """
        return self._processor_id

    @property
    def dtcm_available(self):
        """ The amount of DTCM available on this processor

        :return: the amount of DTCM available on this processor
        :rtype: int

        """
        return self._dtcm_available

    @property
    def cpu_cycles_available(self):
        """ The number of CPU cycles available from this processor per ms

        :return: the number of CPU cycles available on this processor
        :rtype: int
        """
        return self._clock_speed // 1000

    @property
    def clock_speed(self):
        """ The clock speed of the processor in cycles per second

        :return: The clock speed in cycles per second
        :rtype: int
        """
        return self._clock_speed

    @property
    def is_monitor(self):
        """ Determines if the processor is the monitor, and therefore not\
            to be allocated

        .. warning::
            Currently rejection processors are also marked as monitors.

        :return: True if the processor is the monitor, False otherwise
        :rtype: bool
        """
        return self._is_monitor

    # is_monitor setter no longer available
    # use Machine.set_reinjection_processors instead

    def clone_as_system_processor(self):
        """ Creates a clone of this processor but changing it to a system\
            processor.

        :return: A new Processor with the same properties INCLUDING the ID\
            except now set as a System processor
        :rtype: :py:class:`~spinn_machine.Processor`
        """
        return Processor(self._processor_id, self._clock_speed,
                         is_monitor=True, dtcm_available=self._dtcm_available)

    def __str__(self):
        return "[CPU: id={}, clock_speed={} MHz, monitor={}]".format(
            self._processor_id, (self._clock_speed // 1000000),
            self._is_monitor)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def factory(processor_id, is_monitor=False):
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
