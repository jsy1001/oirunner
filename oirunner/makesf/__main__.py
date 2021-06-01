"""Make initial/prior model image for BSMEM.

Attributes:
  COPY_KEYWORDS (List[str]): FITS header keywords copied from input file.

"""

import argparse
import os.path
import sys

from astropy.io import fits

from oirunner import __version__
from oirunner.priorimage import makesf

COPY_KEYWORDS = ["HDUNAME", "ORIGIN", "OBJECT", "AUTHOR", "REFERENC"]


def copyheader(fromhdu, tohdu):
    """Copy subset of header cards."""
    for kw in COPY_KEYWORDS:
        try:
            tohdu.header[kw] = fromhdu.header[kw]
        except KeyError:
            pass


def makeimage(args):
    """Make initial/prior image for BSMEM from existing image."""
    if not args.overwrite and os.path.exists(args.outputimage):
        sys.exit("Not creating '%s' as it already exists." % args.outputimage)
    with fits.open(args.inputimage) as hdulist:
        if args.blank is None:
            outhdu = makesf(hdulist[0], args.fwhm, args.threshold)
        else:
            outhdu = makesf(hdulist[0], args.fwhm, args.threshold, blank=args.blank)
        copyheader(hdulist[0], outhdu)
        outhdu.writeto(args.outputimage, overwrite=args.overwrite)


def create_parser():
    """Return new ArgumentParser instance for this script."""
    parser = argparse.ArgumentParser(description="Make initial/prior image for BSMEM")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    parser.add_argument(
        "-o", "--overwrite", action="store_true", help="Overwrite existing file"
    )
    parser.add_argument(
        "-b", "--blank", type=float, help="Replacement value for pixels below threshold"
    )
    parser.add_argument("inputimage", help="Input FITS image")
    parser.add_argument("outputimage", help="Output FITS image")
    parser.add_argument(
        "fwhm", type=float, help="FWHM of Gaussian to convolve with in mas"
    )
    parser.add_argument(
        "threshold", type=float, help="Threshold relative to peak intensity"
    )
    return parser


def main():
    """Run application."""
    parser = create_parser()
    args = parser.parse_args()
    try:
        makeimage(args)
    except AttributeError:
        parser.print_usage()


if __name__ == "__main__":
    main()
