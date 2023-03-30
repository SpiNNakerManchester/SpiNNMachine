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


class SpinnMachineException(Exception):
    """
    A generic exception which all other exceptions in this package extend.
    """


class SpinnMachineAlreadyExistsException(SpinnMachineException):
    """
    Indicates that something already exists of which there can only be one.
    """
    __slots__ = [
        "_item",
        "_value"]

    def __init__(self, item, value):
        """
        :param str item: The item of which there is already one of
        :param str value: The value of the item
        """
        super().__init__(
            f"There can only be one {item} with a value of {value}")
        self._item = item
        self._value = value

    @property
    def item(self):
        """
        The item of which there is already one.
        """
        return self._item

    @property
    def value(self):
        """
        The value of the item.
        """
        return self._value


class SpinnMachineInvalidParameterException(SpinnMachineException):
    """
    Indicates that there is a problem with a parameter value.
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
        super().__init__(
            f"It is invalid to set {parameter} to {value}: {problem}")
        self._parameter = parameter
        self._value = value
        self._problem = problem

    @property
    def parameter(self):
        """
        The name of the parameter.
        """
        return self._parameter

    @property
    def value(self):
        """
        The value of the parameter.
        """
        return self._value

    @property
    def problem(self):
        """
        The problem with the setting of the parameter.
        """
        return self._problem
