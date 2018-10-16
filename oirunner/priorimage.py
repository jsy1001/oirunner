"""Python module to create initial/prior model images for BSMEM.

Attributes:
  MAS_TO_DEG (float): Conversion factor from milliarcseconds to degrees.

"""

import logging
from typing import Union

import numpy as np
import scipy.signal
from astropy.io import fits
from astropy import wcs

MAS_TO_DEG = 1/3600/1000


def get_pixelsize(imagehdu: Union[fits.PrimaryHDU, fits.ImageHDU]) -> float:
    """Return image pixel size in milliarcseconds."""
    try:
        cdelt1 = imagehdu.header['CDELT1']
        cdelt2 = imagehdu.header['CDELT2']
    except KeyError:
        raise KeyError("CDELT1/2 keywords missing, pixelsize unknown")
    if abs(cdelt1) != abs(cdelt2):
        raise ValueError("Image pixels are not square " +
                         "(CDELT1=%f, CDELT2=%f)" % (cdelt1, cdelt2))
    return cdelt1 / MAS_TO_DEG


def makesf(imagehdu: Union[fits.PrimaryHDU, fits.ImageHDU],
           fwhm: float, threshold: float,
           blank: float = 1e-8) -> fits.PrimaryHDU:
    """Blur and threshold image for use as BSMEM prior model.

    Args:
      imagehdu:  Input FITS image HDU.
      fwhm:      FWHM of Gaussian to convolve with in mas.
      threshold: Threshold relative to peak intensity.
      blank:     Replacement value for pixels below threshold.

    Returns:
      Output FITS image HDU.

    Raises:
      KeyError, ValueError

    """
    # Get image attributes
    dims = imagehdu.data.shape
    pixelsize = get_pixelsize(imagehdu)
    minvalue = imagehdu.data.min()
    maxvalue = imagehdu.data.max()
    logging.info('Image pixelsize = %f mas' % pixelsize)
    logging.info('Image min = %g' % minvalue)
    logging.info('Image max = %g' % maxvalue)

    # Initialize parameters
    sigma = fwhm / pixelsize / 2.3548
    lowest = threshold * maxvalue

    # Generate Gaussian
    bw = int(6*sigma)
    blur = np.zeros((bw, bw), np.float)
    for i in range(bw):
        for j in range(bw):
            blur[i, j] = np.exp(-((i - bw/2)**2 + (j - bw/2)**2) /
                                (2 * sigma * sigma))

    # Convolve
    logging.info('Blurring image with sigma=%f pix...' % sigma)
    result = scipy.signal.convolve(imagehdu.data, blur, 'same')
    logging.info('...blur done')
    # Renormalise
    result = result * maxvalue / result.max()

    # Threshold
    logging.info('Thresholding image at %f (blank=%f)...' % (threshold, blank))
    for i in range(dims[0]):
        for j in range(dims[1]):
            if result[i, j] < lowest:
                result[i, j] = blank
    logging.info('...threshold done')

    # Create output HDU with WCS keywords
    w = wcs.WCS(naxis=2)
    w.wcs.cdelt = [pixelsize * MAS_TO_DEG, pixelsize * MAS_TO_DEG]
    outhdu = fits.PrimaryHDU(data=result, header=w.to_header())
    outhdu.header['HISTORY'] = 'makesf fwhm=%f threshold=%f' % (fwhm,
                                                                threshold)
    return outhdu
