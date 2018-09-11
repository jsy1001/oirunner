from subprocess import run, PIPE, CalledProcessError
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
    try:
        process = run(args, check=True, stdout=PIPE, stderr=PIPE)
        out = process.stdout.decode('utf-8')
        prefix = os.path.splitext(outputfile)[0]
        with open(prefix + '-out.txt', 'w') as f:
            f.write(out)
        result = 'Iteration' + out.split('Iteration')[-1]
        print('\n%s %s' % (outputfile, result))
    except CalledProcessError as e:
        print("FAILED: %s" % e.stderr.decode('utf-8'))


def run_grey_basic(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   modeltype=DEFAULT_MT, modelwidth=DEFAULT_MW):
    dirname, basename = os.path.split(datafile)
    stem = os.path.splitext(basename)[0]
    outputfile = os.path.join(dirname, 'bsmem_%s.fits' % stem)
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
