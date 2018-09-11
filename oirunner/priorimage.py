"""Python module to create initial/prior model images for BSMEM.

Attributes:
  MAS_TO_DEG (float): Conversion factor from milliarcseconds to degrees.

"""

import numpy as np
import scipy.signal
from astropy.io import fits
from astropy import wcs

MAS_TO_DEG = 1/3600/1000


def makesf(imghdu, fwhm, threshold):
    """Blur and threshold image for use as BSMEM prior model.

    Args:
      imghdu (fits.PrimaryHDU or fits.ImageHDU): Input FITS image HDU.
      fwhm (float): FWHM of Gaussian to convolve with in mas.
      threshold: (float): Threshold relative to peak intensity.

    Returns:
      fits.PrimaryHDU: Output FITS image HDU.

    Raises:
       KeyError, ValueError

    """

    # Read image
    dims = imghdu.data.shape
    try:
        cdelt1 = imghdu.header['CDELT1']
        cdelt2 = imghdu.header['CDELT2']
    except KeyError:
        raise KeyError("CDELT1/2 keywords missing, pixelsize unknown")
    if abs(cdelt1) != abs(cdelt2):
        raise ValueError("Image pixels are not square " +
                         "(CDELT1=%f, CDELT2=%f)" % (cdelt1, cdelt2))
    pixelsize = cdelt1 / MAS_TO_DEG
    print('CDELT1 = %f mas' % pixelsize)
    minvalue = imghdu.data.min()
    maxvalue = imghdu.data.max()
    print('min = %g' % minvalue)
    print('max = %g' % maxvalue)

    # Parameters:
    sigma = fwhm / pixelsize / 2.3548
    lowest = threshold * maxvalue
    blank = 1e-8

    # Generate Gaussian
    bw = int(6*sigma)
    blur = np.zeros((bw, bw), np.float)
    for i in range(bw):
        for j in range(bw):
            blur[i, j] = np.exp(-((i - bw/2)**2 + (j - bw/2)**2) /
                                (2 * sigma * sigma))

    # Convolve
    print('Blurring with sigma=%f pix...' % sigma)
    result = scipy.signal.convolve(imghdu.data, blur, 'same')
    print('done')
    # Renormalise
    result = result * maxvalue / result.max()

    # Threshold
    print('Thresholding at %f...' % threshold)
    for i in range(dims[0]):
        for j in range(dims[1]):
            if result[i, j] < lowest:
                result[i, j] = blank
    print('done')

    # Create output HDU with WCS keywords
    w = wcs.WCS(naxis=2)
    w.wcs.cdelt = [pixelsize * MAS_TO_DEG, pixelsize * MAS_TO_DEG]
    outhdu = fits.PrimaryHDU(data=result, header=w.to_header())
    outhdu.header['HISTORY'] = 'makesf fwhm=%f threshold=%f' % (fwhm, threshold)
    return outhdu
