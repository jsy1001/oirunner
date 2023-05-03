"""Python module to run BSMEM, perhaps iteratively.

Attributes:
  BSMEM (str):        Pathname of bsmem executable.
  DEFAULT_DIM (int):  Default reconstructed image width.
  DEFAULT_MT (int):   Default model type.
  DEFAULT_MW (float): Default model width.

"""

import logging
import os
import tempfile
from subprocess import CalledProcessError, PIPE, run
from typing import Optional, Sequence, Tuple

from astropy.io import fits

from .priorimage import get_pixelsize, makesf


BSMEM = "bsmem"
DEFAULT_DIM = 128
DEFAULT_MT = 3
DEFAULT_MW = 10.0


def _get_outputfile(
    datafile: str, iteration: int, wav: Optional[Tuple[float, float]]
) -> str:
    dirname, basename = os.path.split(datafile)
    stem, _ = os.path.splitext(basename)
    if wav is None:
        return os.path.join(dirname, f"bsmem_{iteration}_{stem}.fits")
    else:
        meanwav = int((wav[0] + wav[1]) / 2)
        return os.path.join(dirname, f"bsmem_{iteration}_{stem}_{meanwav}nm.fits")


def run_bsmem(args: Sequence[str], fullstdout: Optional[str] = None) -> None:
    """Run bsmem as subprocess and log result.

    Args:
      args: Arguments for subprocess.
      fullstdout: Destination filename for full stdout.

    """
    logging.info("Running '%s'" % " ".join(args))
    try:
        process = run(args, check=True, stdout=PIPE, stderr=PIPE)
        out = process.stdout.decode("utf-8")
        if fullstdout is not None:
            with open(fullstdout, "w") as f:
                f.write(out)
        result = "Iteration" + out.split("Iteration")[-1]
        logging.info(f"Last iteration:\n{result}")
    except CalledProcessError as e:
        # log output from bsmem process
        logging.exception(
            f"bsmem failed:\n{e.stderr.decode('utf-8')}\n{e.stdout.decode('utf-8')}"
        )
        raise


def run_bsmem_using_model(
    datafile: str,
    outputfile: str,
    dim: int,
    modeltype: int,
    modelwidth: float,
    pixelsize: Optional[float] = None,
    wav: Optional[Tuple[float, float]] = None,
    uvmax: Optional[float] = None,
    use_t3: str = "all",
    alpha: Optional[float] = None,
    flux: Optional[float] = None,
) -> None:
    """Run bsmem using initial/prior model.

    Args:
      datafile:   Input OIFITS data filename.
      outputfile: Output FITS filename.
      dim:        Reconstructed image width (pixels).
      modeltype:  Initial/prior image model type (0-4).
      modelwidth: Initial/prior image model width (mas).
      pixelsize:  Reconstructed image pixel size (mas).
      wav:        Min and max wavelengths to select (nm).
      uvmax:      Maximum uv radius to select (waves).
      use_t3:     Bispectrum data to use if any (possible values="all", "none",
                  "amp", "phi")
      alpha:      Regularization hyperparameter.
      flux:       Assumed total flux.

    """
    args = [
        BSMEM,
        "--noui",
        "--clobber",
        f"--data={datafile}",
        f"--output={outputfile}",
        f"--dim={dim}",
        f"--mt={modeltype}",
        f"--mw={modelwidth}",
    ]
    if pixelsize is not None:
        args += [f"--pixelsize={pixelsize}"]
    if wav is not None:
        args += [f"--wavmin={wav[0]}", f"--wavmax={wav[1]}"]
    if uvmax is not None:
        args += [f"--uvmax={uvmax}"]
    args += [f"--use_t3={use_t3}"]
    if alpha is not None:
        args += ["--autoalpha=3", f"--alpha={alpha}"]
    else:
        args += ["--autoalpha=4"]
    if flux is not None:
        args += [f"--flux={flux}"]
    fullstdout = os.path.splitext(outputfile)[0] + "-out.txt"
    run_bsmem(args, fullstdout)


def run_bsmem_using_image(
    datafile: str,
    outputfile: str,
    dim: int,
    pixelsize: float,
    imagehdu: fits.PrimaryHDU,
    wav: Optional[Tuple[float, float]] = None,
    uvmax: Optional[float] = None,
    use_t3: str = "all",
    alpha: Optional[float] = None,
    flux: Optional[float] = None,
) -> None:
    """Run bsmem using initial/prior image.

    Args:
      datafile:   Input OIFITS data filename.
      outputfile: Output FITS filename.
      dim:        Reconstructed image width (pixels).
      pixelsize:  Reconstructed image pixel size (mas).
      imagehdu:   FITS HDU containing initial/prior image.
      wav:        Min and max wavelengths to select (nm).
      uvmax:      Maximum uv radius to select (waves).
      use_t3:     Bispectrum data to use if any (possible values="all", "none",
                  "amp", "phi")
      alpha:      Regularization hyperparameter.
      flux:       Assumed total flux.

    """
    tempimage = tempfile.NamedTemporaryFile(suffix=".fits", mode="wb", delete=False)
    imagehdu.writeto(tempimage.name, overwrite=True)
    tempimage.close()
    args = [
        BSMEM,
        "--noui",
        "--clobber",
        f"--data={datafile}",
        f"--output={outputfile}",
        f"--dim={dim}",
        f"--pixelsize={pixelsize}",
        f"--sf={tempimage.name}",
    ]
    if wav is not None:
        args += [f"--wavmin={wav[0]}", f"--wavmax={wav[1]}"]
    if uvmax is not None:
        args += [f"--uvmax={uvmax}"]
    args += [f"--use_t3={use_t3}"]
    if alpha is not None:
        args += ["--autoalpha=3", f"--alpha={alpha}"]
    else:
        args += ["--autoalpha=4"]
    if flux is not None:
        args += [f"--flux={flux}"]
    fullstdout = os.path.splitext(outputfile)[0] + "-out.txt"
    run_bsmem(args, fullstdout)
    os.remove(tempimage.name)


def reconst_grey_basic(
    datafile: str,
    pixelsize: Optional[float] = None,
    dim: int = DEFAULT_DIM,
    modeltype: int = DEFAULT_MT,
    modelwidth: float = DEFAULT_MW,
    wav: Optional[Tuple[float, float]] = None,
    uvmax: Optional[float] = None,
    use_t3: str = "all",
    alpha: Optional[float] = None,
    flux: Optional[float] = None,
) -> str:
    """Reconstruct a grey image by running bsmem once.

    Args:
      datafile:   Input OIFITS data filename.
      pixelsize:  Reconstructed image pixel size (mas).
      dim:        Reconstructed image width (pixels).
      modeltype:  Initial/prior image model type (0-4).
      modelwidth: Initial/prior image model width (mas).
      wav:        Min and max wavelengths to select (nm).
      uvmax:      Maximum uv radius to select (waves).
      use_t3:     Bispectrum data to use if any (possible values="all", "none",
                  "amp", "phi")
      alpha:      Regularization hyperparameter.
      flux:       Assumed total flux.

    Returns:
       Output FITS filename.

    """
    outputfile = _get_outputfile(datafile, 1, wav)
    run_bsmem_using_model(
        datafile,
        outputfile,
        dim,
        modeltype,
        modelwidth,
        pixelsize=pixelsize,
        wav=wav,
        uvmax=uvmax,
        use_t3=use_t3,
        alpha=alpha,
        flux=flux,
    )
    return outputfile


def reconst_grey_basic_using_image(
    datafile: str,
    imagefile: str,
    wav: Optional[Tuple[float, float]] = None,
    uvmax: Optional[float] = None,
    use_t3: str = "all",
    alpha: Optional[float] = None,
    flux: Optional[float] = None,
) -> str:
    """Reconstruct a grey image by running bsmem once using a prior image.

    Args:
      datafile:   Input OIFITS data filename.
      imagefile:  Input initial/prior FITS image.
      wav:        Min and max wavelengths to select (nm).
      uvmax:      Maximum uv radius to select (waves).
      use_t3:     Bispectrum data to use if any (possible values="all", "none",
                  "amp", "phi")
      alpha:      Regularization hyperparameter.
      flux:       Assumed total flux.

    Returns:
       Output FITS filename.

    """
    outputfile = _get_outputfile(datafile, 1, wav)
    with fits.open(imagefile) as hdulist:
        imagehdu = hdulist[0]
        dim = imagehdu.data.shape[0]
        pixelsize = get_pixelsize(imagehdu)
        run_bsmem_using_image(
            datafile,
            outputfile,
            dim,
            pixelsize,
            imagehdu,
            wav=wav,
            uvmax=uvmax,
            use_t3=use_t3,
            alpha=alpha,
            flux=flux,
        )
    return outputfile


def reconst_grey_2step(
    datafile: str,
    pixelsize: float,
    dim: int = DEFAULT_DIM,
    modeltype: int = DEFAULT_MT,
    modelwidth: float = DEFAULT_MW,
    wav: Optional[Tuple[float, float]] = None,
    uvmax1: float = 1.1e8,
    use_t3: str = "all",
    alpha: Optional[float] = None,
    flux: Optional[float] = None,
    fwhm: float = 1.25,
    threshold: float = 0.05,
) -> str:
    """Reconstruct a grey image by running bsmem twice.

    Args:
      datafile:   Input OIFITS data filename.
      pixelsize:  Reconstructed image pixel size (mas).
      dim:        Reconstructed image width (pixels).
      modeltype:  Initial/prior image model type for 1st run (0-4).
      modelwidth: Initial/prior image model width for 1st run (mas).
      wav:        Min and max wavelengths to select (nm).
      uvmax1:     Maximum uv radius to select for 1st run (waves).
      use_t3:     Bispectrum data to use if any (possible values="all", "none",
                  "amp", "phi")
      alpha:      Regularization hyperparameter for both runs.
      flux:       Assumed total flux.
      fwhm:       FWHM of Gaussian to convolve 1st run output with (mas).
      threshold:  Threshold (relative to peak) to apply to 1st run output.

    Returns:
       Output FITS filename.

    """
    # TODO: intelligent defaults for uvmax1, fwhm?
    out1file = _get_outputfile(datafile, 1, wav)
    run_bsmem_using_model(
        datafile,
        out1file,
        dim,
        modeltype,
        modelwidth,
        pixelsize=pixelsize,
        wav=wav,
        uvmax=uvmax1,
        use_t3=use_t3,
        alpha=alpha,
        flux=flux,
    )
    with fits.open(out1file) as hdulist:
        imagehdu = makesf(hdulist[0], fwhm, threshold)
    out2file = _get_outputfile(datafile, 2, wav)
    run_bsmem_using_image(
        datafile,
        out2file,
        dim,
        pixelsize,
        imagehdu,
        wav=wav,
        use_t3=use_t3,
        alpha=alpha,
        flux=flux,
    )
    return out2file


def reconst_grey_2step_using_image(
    datafile: str,
    imagefile: str,
    wav: Optional[Tuple[float, float]] = None,
    uvmax1: float = 1.1e8,
    use_t3: str = "all",
    alpha: Optional[float] = None,
    flux: Optional[float] = None,
    fwhm: float = 1.25,
    threshold: float = 0.05,
) -> str:
    """Reconstruct a grey image by running bsmem twice using a prior image.

    Args:
      datafile:   Input OIFITS data filename.
      imagefile:  Input initial/prior FITS image.
      wav:        Min and max wavelengths to select (nm).
      uvmax1:     Maximum uv radius to select for 1st run (waves).
      use_t3:     Bispectrum data to use if any (possible values="all", "none",
                  "amp", "phi")
      alpha:      Regularization hyperparameter for both runs.
      flux:       Assumed total flux.
      fwhm:       FWHM of Gaussian to convolve 1st run output with (mas).
      threshold:  Threshold (relative to peak) to apply to 1st run output.

    Returns:
       Output FITS filename.

    """
    out1file = _get_outputfile(datafile, 1, wav)
    with fits.open(imagefile) as hdulist:
        image1hdu = hdulist[0]
        dim = image1hdu.data.shape[0]
        pixelsize = get_pixelsize(image1hdu)
        run_bsmem_using_image(
            datafile,
            out1file,
            dim,
            pixelsize,
            image1hdu,
            wav=wav,
            uvmax=uvmax1,
            use_t3=use_t3,
            alpha=alpha,
            flux=flux,
        )
    out2file = _get_outputfile(datafile, 2, wav)
    with fits.open(out1file) as hdulist:
        image2hdu = makesf(hdulist[0], fwhm, threshold)
        run_bsmem_using_image(
            datafile,
            out2file,
            dim,
            pixelsize,
            image2hdu,
            wav=wav,
            use_t3=use_t3,
            alpha=alpha,
            flux=flux,
        )
    return out2file
