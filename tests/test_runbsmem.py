import unittest
from subprocess import run, CalledProcessError
try:
    run(['bsmem', '-V'])
    HAVE_BSMEM = True
except (OSError, CalledProcessError):
    HAVE_BSMEM = False

from oirunner.runbsmem import run_grey_basic


class RunBsmemTestCase(unittest.TestCase):

    def setUp(self):
        self.datafile = 'tests/2004contest1.oifits'

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_basic(self):
        """Test basic grey reconstruction"""
        run_grey_basic(self.datafile)
        run_grey_basic(self.datafile, pixelsize=0.2)
