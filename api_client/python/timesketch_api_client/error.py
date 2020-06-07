# Copyright 2019 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Timesketch API client library."""
from __future__ import unicode_literals

import json

import bs4

from . import definitions


def _get_message(response):
    """Return a formatted message string from the response text."""
    soup = bs4.BeautifulSoup(response.text, features='html.parser')
    text = ''
    if soup.p:
        return soup.p.string

    try:
        response_dict = json.loads(response.text.decode('utf-8'))
    except (json.JSONDecodeError, AttributeError):
        return str(response.text)

    if not isinstance(response_dict, dict):
        return str(response_dict)

    return response_dict.get('message', str(response_dict))


def get_response_json(response, logger):
    """Return the JSON object from a response, logging any errors."""
    status = response.status_code in definitions.HTTP_STATUS_CODE_20X
    if not status:
        logger.warning('Failed response: [{0:d}] {2:s} {1:s}'.format(
            response.status_code, response.reason.encode('utf-8'),
            _get_message(response)))

    try:
        return response.json()
    except json.JSONDecodeError as e:
        logger.error('Unable to decode response: {0!s}'.format(e))
        return {}


def error_message(response, message=None, error=RuntimeError):
    """Raise an error using error message extracted from response."""
    if not message:
        message = 'Unknown error, with error: '
    text = _get_message(response)

    raise error('{0:s}, with error [{1:d}] {2!s} {3:s}'.format(
        message, response.status_code, response.reason, text))


def check_return_status(response, logger):
    """Check return status and return a boolean."""
    status = response.status_code in definitions.HTTP_STATUS_CODE_20X
    if status:
        return status

    logger.warning('Failed response: [{0:d}] {1:s}'.format(
        response.status_code, _get_message(response)))
    return status


class Error(Exception):
    """Base error class."""


class UnableToRunAnalyzer(Error):
    """Raised when unable to run an analyzer."""
