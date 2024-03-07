# -------------------------------------------------------------------------
#
# Copyright (c) 2024 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2024 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

# -*- coding: UTF-8 -*-

from hamcrest import assert_that, equal_to, none, not_none, contains_string


class Assert(object):
    """Wrapper functions on top of hamcrest assertions
    Usage:
        Assert.assert_equals(actual, expected, message)
        Assert.assert_not_equals(actual,expected, message)
        Assert.fail(message)
    """

    @staticmethod
    def assert_true(condition, message=None):
        """Assert a condition is True
        :param condition: condition to check
        :param message: message to display in case of assertion failure
        :return: None
        """
        assert_that(condition, equal_to(True), message)

    @staticmethod
    def assert_false(condition, message=None):
        """Assert a condition is False
        :param condition: condition to check
        :param message: message to display in case of assertion failure
        :return:
        """
        assert_that(condition, equal_to(False), message)

    @staticmethod
    def assert_equals(actual, expected, message=None):
        """Assert expected and actual values match
        :param actual: actual result
        :param expected: expected result
        :param message: message to display in case of assertion failure
        :return: None
        """
        assert_that(actual, equal_to(expected), message)

    @staticmethod
    def assert_contains(actual, expected, message=None):
        """Assert expected contains actual value
        :param actual: actual result
        :param expected: expected result
        :param message: message to display in case of assertion failure
        :return: None
        """
        assert_that(actual, contains_string(expected), message)

    @staticmethod
    def assert_not_equals(actual, expected, message=None):
        """Assert expected and actual values do not match
        :param actual: actual result
        :param expected: expected result
        :param message: message to display in case of assertion failure
        :return: None
        """
        assert_that(actual, not (equal_to(expected)), message)

    @staticmethod
    def assert_none(condition, message=None):
        """Assert result is None
        :param condition: condition to check
        :param message: message to display in case of assertion failure
        :return: None
        """
        assert_that(condition, none, message)

    @staticmethod
    def assert_not_none(condition, message=None):
        """Assert result is NOT None
        :param condition: condition to check
        :param message: message to display in case of assertion failure
        :return: None
        """
        assert_that(condition, not_none, message)

    @staticmethod
    def assert_fail(message=None):
        """Force fail scenario
        :param message: message to display in case of assertion failure
        :return: None
        """
        assert_that(False, equal_to(True), message)
