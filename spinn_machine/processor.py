from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class Processor(object):
    """ A processor object included in a chip
    """

    CPU_AVAILABLE = 200000
    DTCM_AVAILABLE = 2 ** 15

    def __init__(self, processor_id, clock_speed, is_monitor=False,
                 dtcm_available=DTCM_AVAILABLE):
        """

        :param processor_id: id of the processor in the chip
        :type processor_id: int
        :param clock_speed: The number of cpu cycles per second of the\
                    processor
        :type clock_speed: int
        :param is_monitor: Determines if the processor is considered the\
                    monitor processor, and so should not be otherwise allocated
        :type is_monitor: bool
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
        """ The id of the processor

        :return: id of the processor
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._processor_id

    @property
    def dtcm_available(self):
        """the amount of dtcm avilable on this processor

        :return: the amount of dtcm avilable on this processor
        :rtype: int
        :raise None: does not raise any known exceptions

        """
        return self._dtcm_available

    @property
    def cpu_cycles_available(self):
        """the amount of cpu cycles available from this processor

        :return: the amount of cpu cycles avilable on this processor
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return Processor.CPU_AVAILABLE
    
    @property
    def clock_speed(self):
        """ The clock speed of the processor in cycles per second
        
        :return: The clock speed in cycles per second
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._clock_speed
    
    @property
    def is_monitor(self):
        """ Determines if the processor is the monitor, and therefore not\
            to be allocated
        
        :return: True if the processor is the monitor, False otherwise
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        return self._is_monitor
    
    def __str__(self):
        return "[CPU: id={}, clock_speed={} MHz, monitor={}]".format(
            self._processor_id, (self._clock_speed / 1000000),
            self._is_monitor)
    
    def __repr__(self):
        return self.__str__()
