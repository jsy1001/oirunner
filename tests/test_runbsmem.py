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

from oirunner.runbsmem import reconst_grey_basic, reconst_grey_2step

DATAFILE = 'tests/2004contest1.oifits'


class RunBsmemTestCase(unittest.TestCase):

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_basic(self):
        """Test basic grey reconstruction"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname, os.path.basename(DATAFILE))
            copyfile(DATAFILE, tempdatafile)
            reconst_grey_basic(tempdatafile)
            reconst_grey_basic(tempdatafile, pixelsize=0.25)
            reconst_grey_basic(tempdatafile, uvmax=1.1e8)
            reconst_grey_basic(tempdatafile, pixelsize=0.25, uvmax=1.1e8)

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_2step(self):
        """Test two-step grey reconstruction"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname, os.path.basename(DATAFILE))
            copyfile(DATAFILE, tempdatafile)
            reconst_grey_2step(tempdatafile, 0.25)
