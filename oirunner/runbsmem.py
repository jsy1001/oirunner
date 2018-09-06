from subprocess import check_output
# from astropy.io import fits
import os.path
# import numpy as np

BSMEM = 'bsmem'

DEFAULT_DIM = 128
DEFAULT_MT = 3
DEFAULT_MW = 10.0


def reconst_grey(datafile, outputfile, dim, pixelsize,
                 modeltype, modelwidth):
    args = [BSMEM, '--noui',
            '--data=%s' % datafile,
            '--clobber', '--output=%s' % outputfile,
            '--dim=%d' % dim,
            '--mt=%d' % modeltype,
            '--mw=%f' % modelwidth]
    if pixelsize is not None:
        args += ['--pixelsize=%f' % pixelsize]
    print("Running '%s'" % ' '.join(args))
    output = check_output(args)
    result = 'Iteration' + str(output).split('Iteration')[-1]
    print('\n%s %s' % (outputfile, result))


def run_grey_basic(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   modeltype=DEFAULT_MT, modelwidth=DEFAULT_MW):
    stem = os.path.splitext(os.path.basename(datafile))[0]
    outputfile = 'bsmem_%s.fits' % stem  # in CWD
    reconst_grey(datafile, outputfile, dim, pixelsize,
                 modeltype, modelwidth)


def run_grey_2step(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   modeltype=DEFAULT_MT, modelwidth=DEFAULT_MW,
                   basmax=25.0):
    pass


def run_grey_nstep(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   modeltype=DEFAULT_MT, modelwidth=DEFAULT_MW,
                   basmax=[25.0, 30.0, 40.0, 50.0]):
    pass
