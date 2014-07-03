class SpinnMachineException(Exception):
    """ A generic exception which all other exceptions extend
    """
    pass

class SpinnMachineAlreadyExistsException(SpinnMachineException):
    """ Indicates that something already exists of which there can only be one
    """
    
    def __init__(self, item, value):
        """
        
        :param item: The item of which there is already one of
        :type item: str
        :param value: The value of the item
        :type value: str
        """
        pass

class SpinnMachineInvalidParameterException(SpinnMachineException):
    """ Indicates that there is a problem with a parameter value
    """
    
    def __init__(self, parameter, value, problem):
        """
        
        :param parameter: The name of the parameter that has an invalid value
        :type item: str
        :param value: The value of the parameter that is invalid
        :type value: str
        :param problem: The reason for the exception
        :type problem: str
        """
        pass
