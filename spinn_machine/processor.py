DEFAULT_CLOCK_SPEED = 200 * 1000 * 1000

class Processor(object):
    """ A processor object included in a chip 
    """

    def __init__(self, processor_id, clock_speed, is_monitor=False):
        """

        :param processor_id: id of the processor in the chip
        :type processor_id: int
        :param clock_speed: The number of cpu cycles per second of the processor
        :type clock_speed: int
        :param is_monitor: Determines if the processor is considered the\
                    monitor processor, and so should not be otherwise allocated
        :type is_monitor: bool
        :raise None: does not raise any known exceptions
        """
        self._processor_id = processor_id
        self._clock_speed = clock_speed
        self._is_monitor = is_monitor

    @property
    def processor_id(self):
        """ The id of the processor

        :return: id of the processor
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._processor_id
    
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
