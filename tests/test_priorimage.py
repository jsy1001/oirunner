import unittest

from astropy.io import fits
from astropy import wcs
import numpy as np

from oirunner.priorimage import makesf, MAS_TO_DEG


class PriorImageTestCase(unittest.TestCase):

    def setUp(self):
        self.data = np.zeros([64, 64], float)
        self.data[31, 32] = 0.04
        self.data[32, 32] = 1.0
        self.data[33, 32] = 0.06

    def test_makesf(self):
        """Test blur and threshold"""
        w = wcs.WCS(naxis=2)
        w.wcs.cdelt = [0.5 * MAS_TO_DEG, 0.5 * MAS_TO_DEG]
        hdu = fits.PrimaryHDU(self.data, header=w.to_header())
        outhdu = makesf(hdu, 2.0, 0.05, 0.0025)
        self.assertEqual(outhdu.data.shape, self.data.shape)
        self.assertAlmostEqual(outhdu.data.max(), self.data.max())
        self.assertTrue(np.all(outhdu.data >= 0.0025))
        self.assertAlmostEqual(outhdu.header['CDELT1'], w.wcs.cdelt[0])
        self.assertAlmostEqual(outhdu.header['CDELT2'], w.wcs.cdelt[1])

    def test_makesf_nopixsize(self):
        """CDELT1/2 keywords missing, should fail with KeyError"""
        hdu = fits.PrimaryHDU(self.data)
        with self.assertRaises(KeyError):
            makesf(hdu, 2.0, 0.1)

    def test_makesf_nonsquarepix(self):
        """abs(CDELT1) != abs(CDELT2), should fail with ValueError"""
        w = wcs.WCS(naxis=2)
        w.wcs.cdelt = [0.5 * MAS_TO_DEG, 1.0 * MAS_TO_DEG]
        hdu = fits.PrimaryHDU(self.data, header=w.to_header())
        with self.assertRaises(ValueError):
            makesf(hdu, 2.0, 0.1)
