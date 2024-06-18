import unittest
from datetime import datetime, timedelta

from framework.service import Service
from framework.utils import utc

from .. import DummyStartResponse

environ, start_response = dict(QUERY_STRING=''), DummyStartResponse()


class TestModule(unittest.TestCase):
    def test_init(self):
        tuple(Service(__name__)(environ, start_response))

        self.assertIsInstance(utc.now, datetime)
        self.assertIsInstance(utc.timestamp, float)
        self.assertEqual(utc.timestamp, utc.now.timestamp())

    def test_delta(self):
        tuple(Service(__name__, time_zone='-03:30')(environ, start_response))

        self.assertEqual(
            utc.now + timedelta(seconds=-(3 * 60 * 60 + 30 * 60)),
            utc.delta.datetime(utc.now),
        )

        self.assertEqual(
            utc.now + timedelta(seconds=-(3 * 60 * 60 + 30 * 60)),
            utc.delta.timestamp(utc.timestamp),
        )

        tuple(Service(__name__, time_zone='+03:00')(environ, start_response))

        self.assertEqual(
            utc.now + timedelta(seconds=3 * 60 * 60),
            utc.delta.datetime(utc.now),
        )

        self.assertEqual(
            utc.now + timedelta(seconds=3 * 60 * 60),
            utc.delta.timestamp(utc.timestamp),
        )


def utc_tests():
    suite = unittest.TestSuite()

    for test in (
            'test_init',
            'test_delta',
    ):
        suite.addTest(TestModule(test))

    return suite
