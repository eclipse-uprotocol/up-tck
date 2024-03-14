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

import os
import logging
import time

from logging.config import dictConfig
from time import strftime

# Log folder directory
LOG_DIR = "logs"

# Logger configuration settings
LOG_SETTINGS = {

    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        # 'formatted_console': {
        #     'class': 'logging.StreamHandler',
        #     'level': 'INFO',
        #     'formatter': 'detailed',
        #     'stream': 'ext://sys.stdout',
        # },
        # 'formatted_file': {
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'level': 'INFO',
        #     'formatter': 'detailed',
        #     'filename': "logs" + os.path.sep + "uitests_" + strftime("%Y-%m-%d_%H_%M_%S") + ".log",
        #     'mode': 'a',
        #     'maxBytes': 10485760,
        #     'backupCount': 5,
        # },
        # 'unformatted_console': {
        #     'class': 'logging.StreamHandler',
        #     'level': 'INFO',
        #     'formatter': 'blank',
        #     'stream': 'ext://sys.stdout',
        # },
        # 'unformatted_file': {
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'level': 'INFO',
        #     'formatter': 'blank',
        #     'filename': "logs" + os.path.sep + "uitests_" + strftime("%Y-%m-%d_%H_%M_%S") + ".log",
        #     'mode': 'a',
        #     'maxBytes': 10485760,
        #     'backupCount': 5,
        # },
    },
    'formatters': {
        'detailed': {
            'format': '[%(levelname)s] : %(asctime)s : %(filename)s : %(funcName)s:%(lineno)d : %(message)s',
        },
        'blank': {
            'format': '',
        },
    },
    'loggers': {
        # 'formatted_log': {
        #         'level': 'DEBUG',
        #         'handlers': ['formatted_file', 'formatted_console']
        #     },
        # 'unformatted_log': {
        #     'level': 'DEBUG',
        #     'handlers': ['unformatted_file', 'unformatted_console']
        # },
    }
}


class TimeFilter(logging.Filter):
    def __init__(self, context, name=''):
        context.log_timestamp = time.time()
        self.context = context
        super(TimeFilter, self).__init__(name=name)

    def filter(self, record):
        self.context.log_timestamp = time.time()
        return super().filter(record)


def setup_logging():
    """Use the LOG_SETTINGS defined above and initialize the logger
    :return: None
    """
    dictConfig(LOG_SETTINGS)


def setup_formatted_logging(context):
    """Formatted log includes file name, time stamp and log levels
    :param context: Holds contextual information
    :return: None
    """
    context.logger = logging.getLogger('formatted_log')
    context.logger.addFilter(TimeFilter(context, name='formatted_log'))


def setup_unformatted_logging(context):
    """Unformatted logging doesn't include file name, timestamp and/or log levels
    Ideal for situations where you want to print some messages to log where the above
    parameters are not required. For example to print a message to screen that
    "Testing is started ...", We do not need to include the file name, time stamp or
    log levels. It helps in separating the different section of log files and makes
    them more readable.
    :param context: Holds contextual information
    :return: None
    """
    context.logger = logging.getLogger('unformatted_log')
    context.logger.addFilter(TimeFilter(context, name='unformatted_log'))
