import unittest

from oirunner.runbsmem import run_grey_basic


class RunBsmemTestCase(unittest.TestCase):

    def setUp(self):
        self.datafile = 'tests/2004contest1.oifits'

    def test_grey_basic(self):
        """Test basic grey reconstruction"""
        run_grey_basic(self.datafile)
        run_grey_basic(self.datafile, pixelsize=0.2)
