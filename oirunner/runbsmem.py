from subprocess import check_output
# from astropy.io import fits
import os.path
# import numpy as np

BSMEM = 'bsmem'

DEFAULT_DIM = 128


def reconst_grey(datafile, outputfile, dim, pixelsize):
    args = [BSMEM, '--noui',
            '--data=%s' % datafile,
            '--clobber', '--output=%s' % outputfile,
            '--dim=%d' % dim]
    if pixelsize is not None:
        args += ['--pixelsize=%f' % pixelsize]
    print("Running '%s'" % ' '.join(args))
    output = check_output(args)
    result = 'Iteration' + str(output).split('Iteration')[-1]
    print('\n%s %s' % (outputfile, result))


def run_grey_basic(datafile, dim=DEFAULT_DIM, pixelsize=None):
    stem = os.path.splitext(os.path.basename(datafile))[0]
    outputfile = 'bsmem_%s.fits' % stem  # in CWD
    reconst_grey(datafile, outputfile, dim, pixelsize)


def run_grey_2step(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   basmax=25.0):
    pass


def run_grey_nstep(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   basmax=[25.0, 30.0, 40.0, 50.0]):
    pass
