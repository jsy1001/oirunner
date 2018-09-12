import unittest
import tempfile
import os.path
from shutil import copyfile
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
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname,
                                        os.path.basename(self.datafile))
            copyfile(self.datafile, tempdatafile)
            run_grey_basic(tempdatafile)
            run_grey_basic(tempdatafile, pixelsize=0.25)
            run_grey_basic(tempdatafile, uvmax=1.1e8)
            run_grey_basic(tempdatafile, pixelsize=0.25, uvmax=1.1e8)

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_2step(self):
        """Test two-step grey reconstruction"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname,
                                        os.path.basename(self.datafile))
            copyfile(self.datafile, tempdatafile)
            run_grey_2step(tempdatafile, 0.25)
