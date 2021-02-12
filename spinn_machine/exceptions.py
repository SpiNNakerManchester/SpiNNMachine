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


class SpinnMachineException(Exception):
    """ A generic exception which all other exceptions extend
    """


class SpinnMachineAlreadyExistsException(SpinnMachineException):
    """ Indicates that something already exists of which there can only be one
    """
    __slots__ = [
        "_item",
        "_value"]

    def __init__(self, item, value):
        """
        :param str item: The item of which there is already one of
        :param str value: The value of the item
        """
        super().__init__("There can only be one {} with a value of {}".format(
            item, value))
        self._item = item
        self._value = value

    @property
    def item(self):
        """ The item of which there is already one
        """
        return self._item

    @property
    def value(self):
        """ The value of the item
        """
        return self._value


class SpinnMachineInvalidParameterException(SpinnMachineException):
    """ Indicates that there is a problem with a parameter value
    """
    __slots__ = [
        "_parameter",
        "_problem",
        "_value"]

    def __init__(self, parameter, value, problem):
        """
        :param str parameter:
            The name of the parameter that has an invalid value
        :param str value: The value of the parameter that is invalid
        :param str problem: The reason for the exception
        """
        super().__init__("It is invalid to set {} to {}: {}".format(
            parameter, value, problem))
        self._parameter = parameter
        self._value = value
        self._problem = problem

    @property
    def parameter(self):
        """ The name of the parameter
        """
        return self._parameter

    @property
    def value(self):
        """ The value of the parameter
        """
        return self._value

    @property
    def problem(self):
        """ The problem with the setting of the parameter
        """
        return self._problem
