import os.path
import tempfile
import unittest
from shutil import copyfile
from subprocess import CalledProcessError, run

try:
    run(["bsmem", "-V"])
    HAVE_BSMEM = True
except (OSError, CalledProcessError):
    HAVE_BSMEM = False

import oirunner.runbsmem as runbs

DATAFILE = "tests/2004contest1.oifits"
IMAGEFILE = "tests/gauss10.fits"


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
            out = runbs.reconst_grey_basic(tempdatafile, wav=(500.0, 600.0))
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, uvmax=1.1e8)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, use_t3="phi")
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, alpha=4000.0)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(tempdatafile, flux=0.99)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic(
                tempdatafile,
                pixelsize=0.25,
                wav=(500.0, 600.0),
                uvmax=1.1e8,
                use_t3="phi",
                alpha=4000.0,
                flux=0.95,
            )
            self.assertTrue(os.path.exists(out))

    @unittest.skipUnless(HAVE_BSMEM, "requires bsmem")
    def test_grey_basic_using_image(self):
        """Test grey reconstruction using a prior image"""
        with tempfile.TemporaryDirectory() as dirname:
            tempdatafile = os.path.join(dirname, os.path.basename(DATAFILE))
            copyfile(DATAFILE, tempdatafile)
            out = runbs.reconst_grey_basic_using_image(tempdatafile, IMAGEFILE)
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic_using_image(
                tempdatafile, IMAGEFILE, wav=(500.0, 600.0)
            )
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic_using_image(
                tempdatafile, IMAGEFILE, uvmax=1.1e8
            )
            out = runbs.reconst_grey_basic_using_image(
                tempdatafile, IMAGEFILE, use_t3="phi"
            )
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic_using_image(
                tempdatafile, IMAGEFILE, alpha=4000.0
            )
            out = runbs.reconst_grey_basic_using_image(
                tempdatafile, IMAGEFILE, flux=0.95
            )
            self.assertTrue(os.path.exists(out))
            out = runbs.reconst_grey_basic_using_image(
                tempdatafile,
                IMAGEFILE,
                wav=(500.0, 600.0),
                uvmax=1.1e8,
                use_t3="phi",
                alpha=4000.0,
                flux=0.95,
            )
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
