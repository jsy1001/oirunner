import unittest
from subprocess import run, CalledProcessError
try:
    run(['bsmem', '-V'])
    HAVE_BSMEM = True
except (OSError, CalledProcessError):
    HAVE_BSMEM = False

from oirunner.runbsmem import run_grey_basic, run_grey_2step


class RunBsmemTestCase(unittest.TestCase):

    def setUp(self):
        self.datafile = 'tests/2004contest1.oifits'

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_basic(self):
        """Test basic grey reconstruction"""
        run_grey_basic(self.datafile)
        run_grey_basic(self.datafile, pixelsize=0.2)

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_2step(self):
        """Test two-step grey reconstruction"""
        run_grey_2step(self.datafile, pixelsize=0.15)
