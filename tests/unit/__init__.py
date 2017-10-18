#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from unittest import mock


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.mock_log = mock.patch('gitlab_changelog._log')
        self.mock_log.start()

    def tearDown(self):
        self.mock_log.stop()

    def mock_utcnow(self, mock_datetime):
        mock_datetime.now = mock.Mock(return_value=datetime(2017, 2, 15, 13, 5, 12))
        mock_datetime.strftime = datetime.strftime

    def mock_process(self, wait_return_value, stdout_return_value=[b'']):
        mock_process = mock.Mock()
        mock_process.wait.return_value = wait_return_value
        mock_process.stdout.readlines.return_value = stdout_return_value
        return mock_process

    def mock_read(self, return_value):
        mock_read = mock.MagicMock()
        mock_read.read.return_value = return_value
        return mock_read
