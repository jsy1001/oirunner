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

import oirunner.runbsmem as runbs

DATAFILE = 'tests/2004contest1.oifits'
IMAGEFILE = 'tests/gauss10.fits'


class RunBsmemTestCase(unittest.TestCase):

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_basic(self):
        """Test grey reconstruction"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname, os.path.basename(DATAFILE))
            copyfile(DATAFILE, tempdatafile)
            out = runbs.reconst_grey_basic(tempdatafile)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, pixelsize=0.25)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, uvmax=1.1e8)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, alpha=4000.)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, pixelsize=0.25,
                                           uvmax=1.1e8, alpha=4000.)
            self.assertTrue(os.path.exists(out))

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_basic_using_image(self):
        """Test grey reconstruction using a prior image"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname, os.path.basename(DATAFILE))
            copyfile(DATAFILE, tempdatafile)
            out = runbs.reconst_grey_basic_using_image(tempdatafile, IMAGEFILE)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, uvmax=1.1e8)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, alpha=4000.)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile,
                                           uvmax=1.1e8, alpha=4000.)
            self.assertTrue(os.path.exists(out))

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_2step(self):
        """Test two-step grey reconstruction"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname, os.path.basename(DATAFILE))
            copyfile(DATAFILE, tempdatafile)
            out = runbs.reconst_grey_2step(tempdatafile, 0.25)
            self.assertTrue(os.path.exists(out))

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_2step_using_image(self):
        """Test two-step grey reconstruction using a prior image"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname, os.path.basename(DATAFILE))
            copyfile(DATAFILE, tempdatafile)
            out = runbs.reconst_grey_2step_using_image(tempdatafile, IMAGEFILE)
            self.assertTrue(os.path.exists(out))
