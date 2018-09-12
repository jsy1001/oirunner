"""Python module to run BSMEM, perhaps iteratively.

Attributes:
  BSMEM (str):        Pathname of bsmem executable.
  DEFAULT_DIM (int):  Default reconstructed image width.
  DEFAULT_MT (int):   Default model type.
  DEFAULT_MW (float): Default model width.

"""

import os.path
import tempfile
import logging
from typing import Sequence
from subprocess import run, PIPE, CalledProcessError

from astropy.io import fits

from .priorimage import makesf


BSMEM = 'bsmem'
DEFAULT_DIM = 128
DEFAULT_MT = 3
DEFAULT_MW = 10.0


def _get_outputfile(datafile: str, iteration: int) -> str:
    dirname, basename = os.path.split(datafile)
    stem = os.path.splitext(basename)[0]
    return os.path.join(dirname, 'bsmem_%d_%s.fits' % (iteration, stem))


def run_bsmem(args: Sequence[str], fullstdout: str = None) -> None:
    """Run bsmem as subprocess and log result.

    Args:
      args: Arguments for subprocess.
      fullstdout: Destination filename for full stdout.

    """
    logging.info("Running '%s'" % ' '.join(args))
    try:
        process = run(args, check=True, stdout=PIPE, stderr=PIPE)
        out = process.stdout.decode('utf-8')
        if fullstdout is not None:
            with open(fullstdout, 'w') as f:
                f.write(out)
        result = 'Iteration' + out.split('Iteration')[-1]
        logging.info('Last iteration:\n%s' % result)
    except CalledProcessError as e:
        # log output from bsmem process
        logging.exception("bsmem failed:\n%s\n%s" % (e.stderr.decode('utf-8'),
                                                     e.stdout.decode('utf-8')))
        raise


def reconst_using_model(datafile: str, outputfile: str, dim:
                        int, modeltype: int, modelwidth: float,
                        pixelsize: float = None,
                        uvmax: float = None) -> None:
    """Run bsmem using initial/prior model.

    Args:
      datafile:   Input OIFITS data filename.
      outputfile: Output FITS filename.
      dim:        Reconstructed image width (pixels).
      modeltype:  Initial/prior image model type (0-4).
      modelwidth: Initial/prior image model width (mas).
      pixelsize:  Reconstructed image pixel size (mas).
      uvmax:      Maximum uv radius to select (waves).

    """
    args = [BSMEM, '--noui',
            '--data=%s' % datafile,
            '--clobber', '--output=%s' % outputfile,
            '--dim=%d' % dim,
            '--mt=%d' % modeltype,
            '--mw=%f' % modelwidth]
    if pixelsize is not None:
        args += ['--pixelsize=%f' % pixelsize]
    if uvmax is not None:
        args += ['--uvmax=%f' % uvmax]
    fullstdout = os.path.splitext(outputfile)[0] + '-out.txt'
    run_bsmem(args, fullstdout)


def reconst_using_image(datafile: str, outputfile: str, dim: int,
                        pixelsize: float, imagehdu: fits.PrimaryHDU,
                        uvmax: float = None) -> None:
    """Run bsmem using initial/prior image.

    Args:
      datafile:   Input OIFITS data filename.
      outputfile: Output FITS filename.
      dim:        Reconstructed image width (pixels).
      pixelsize:  Reconstructed image pixel size (mas).
      imagehdu:   FITS HDU containing initial/prior image.
      uvmax:      Maximum uv radius to select (waves).

    """
    tempImage = tempfile.NamedTemporaryFile(suffix='.fits', mode='wb',
                                            delete=False)
    imagehdu.writeto(tempImage.name, overwrite=True)
    tempImage.close()
    args = [BSMEM, '--noui',
            '--data=%s' % datafile,
            '--clobber', '--output=%s' % outputfile,
            '--dim=%d' % dim,
            '--pixelsize=%f' % pixelsize,
            '--sf=%s' % tempImage.name]
    if uvmax is not None:
        args += ['--uvmax=%f' % uvmax]
    fullstdout = os.path.splitext(outputfile)[0] + '-out.txt'
    run_bsmem(args, fullstdout)
    os.remove(tempImage.name)


def run_grey_basic(datafile: str,
                   pixelsize: float = None,
                   dim: int = DEFAULT_DIM,
                   modeltype: int = DEFAULT_MT,
                   modelwidth: float = DEFAULT_MW,
                   uvmax: float = None) -> None:
    """Reconstruct a grey image by running bsmem once.

    Args:
      datafile:   Input OIFITS data filename.
      pixelsize:  Reconstructed image pixel size (mas).
      dim:        Reconstructed image width (pixels).
      modeltype:  Initial/prior image model type (0-4).
      modelwidth: Initial/prior image model width (mas).
      uvmax:      Maximum uv radius to select (waves).

    """
    reconst_using_model(datafile, _get_outputfile(datafile, 1), dim,
                        modeltype, modelwidth,
                        pixelsize=pixelsize, uvmax=uvmax)


def run_grey_2step(datafile: str,
                   pixelsize: float,
                   dim: int = DEFAULT_DIM,
                   modeltype: int = DEFAULT_MT,
                   modelwidth: float = DEFAULT_MW,
                   uvmax1: float = 1.1e8,
                   fwhm: float = 1.25,
                   threshold: float = 0.05) -> None:
    """Reconstruct a grey image by running bsmem twice.

    Args:
      datafile:   Input OIFITS data filename.
      pixelsize:  Reconstructed image pixel size (mas).
      dim:        Reconstructed image width (pixels).
      modeltype:  Initial/prior image model type for 1st run (0-4).
      modelwidth: Initial/prior image model width for 1st run (mas).
      uvmax1:     Maximum uv radius to select for 1st run (waves).
      fwhm:       FWHM of Gaussian to convolve 1st run output with (mas).
      threshold:  Threshold (relative to peak) to apply to 1st run output.

    """
    # :TODO: intelligent defaults for uvmax1, fwhm?
    out1file = _get_outputfile(datafile, 1)
    reconst_using_model(datafile, out1file, dim, modeltype, modelwidth,
                        pixelsize=pixelsize, uvmax=uvmax1)
    with fits.open(out1file) as hdulist:
        imagehdu = makesf(hdulist[0], fwhm, threshold)
    reconst_using_image(datafile, _get_outputfile(datafile, 2), dim, pixelsize,
                        imagehdu)
