from psycopg2.tests import unittest

import src.utils as utils


class TestConfig(unittest.TestCase):

    def test_full_path(self):
        real_path = utils.full_path("test/this")
        self.assertIn("TnyBot/test/this", real_path)

