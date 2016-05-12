from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class SDRAM(object):
    """ Represents the properties of the SDRAM of a chip in the machine
    """
    DEFAULT_SDRAM_BYTES = 128 * 1024 * 1024

    DEFAULT_BASE_ADDRESS = 0x70000000

    DEFAULT_SYSTEM_ADDRESS = 0x77800000

    def __init__(self, user_base_address=DEFAULT_BASE_ADDRESS,
                 total_size=DEFAULT_SDRAM_BYTES,
                 free_size=DEFAULT_SDRAM_BYTES):
        """
        :param user_base_address: The start of the space which is available\
                    for use
        :type user_base_address: int
        :type user_base_address: int
        :param total_size: the total size of bytes that this sdram object holds
        :type total_size: int
        :param free_size: the space available in SDRAM
        :raise spinn_machine.exceptions.SpinnMachineInvalidParameterException:\
                    If the size is less than 0
        """
        if total_size < 0:
            raise SpinnMachineInvalidParameterException(
                "size", str(total_size), "Must not be less than 0")
        self._user_base_address = user_base_address
        self._total_size = total_size
        self._free_size = free_size

    @property
    def size(self):
        """ The SDRAM available for user applications

        :return: The space available in bytes
        :rtype: int
        """
        return self._free_size

    @property
    def user_base_address(self):
        """ The start of the SDRAM available for user applications

        :return: The start of the user space in SDRAM
        :rtype: int
        """
        return self._user_base_address

    @property
    def total_size(self):
        """ The size of SDRAM in bytes

        :return: The size of SDRAM in bytes
        :rtype: int
        :raise None: does not raise any known exceptions
        """
        return self._total_size

    def __str__(self):
        return "{} MB".format(self._free_size / (1024 * 1024))

    def __repr__(self):
        return self.__str__()
