import unittest
import os
import tempfile

import numpy as np
from astropy.io import fits
from astropy import wcs

from oirunner.priorimage import MAS_TO_DEG
from oirunner.makesf.__main__ import create_parser, makeimage, COPY_KEYWORDS


class MakesfTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = create_parser()
        data = np.zeros([64, 64], float)
        data[32, 32] = 1.0
        w = wcs.WCS(naxis=2)
        w.wcs.cdelt = [0.5 * MAS_TO_DEG, -0.5 * MAS_TO_DEG]
        self.hdu = fits.PrimaryHDU(data, header=w.to_header())
        self.hdu.header['HDUNAME'] = 'OUTPUT99'
        self.hdu.header['ORIGIN'] = 'ESO'
        self.hdu.header['OBJECT'] = 'alf Ori'
        self.hdu.header['AUTHOR'] = 'A. Chiavassa'
        self.hdu.header['REFERENC'] = 'A&A 515, 12 (2010)'
        with tempfile.NamedTemporaryFile(suffix='.fits', mode='wb',
                                         delete=False) as tempimage:
            self.hdu.writeto(tempimage)
            tempimage.close()
            self.imageName = tempimage.name
        self.tempResult = tempfile.NamedTemporaryFile(suffix='.fits',
                                                      mode='wb', delete=False)

    def tearDown(self):
        os.remove(self.imageName)
        self.tempResult.close()
        os.remove(self.tempResult.name)

    def test_version(self):
        """Test '--version' argument"""
        with self.assertRaises(SystemExit) as cm:
            self.parser.parse_args(['--version'])
            self.assertEqual(cm.exception.code, 0)

    def test_makeimage(self):
        """Test image blur and threshold"""
        args = self.parser.parse_args(["--overwrite",
                                       self.imageName, self.tempResult.name,
                                       "2.0", "0.1"])
        makeimage(args)
        with fits.open(self.tempResult.name) as hdulist:
            for kw in COPY_KEYWORDS:
                self.assertEqual(hdulist[0].header[kw], self.hdu.header[kw])
        args = self.parser.parse_args(["--overwrite", "--blank=0.0001",
                                       self.imageName, self.tempResult.name,
                                       "2.0", "0.1"])
        makeimage(args)
        with fits.open(self.tempResult.name) as hdulist:
            for kw in COPY_KEYWORDS:
                self.assertEqual(hdulist[0].header[kw], self.hdu.header[kw])


if __name__ == '__main__':
    unittest.main()
