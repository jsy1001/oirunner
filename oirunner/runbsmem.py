import os.path
from subprocess import run, PIPE, CalledProcessError

from astropy.io import fits

from .priorimage import makesf


BSMEM = 'bsmem'

DEFAULT_DIM = 128
DEFAULT_MT = 3
DEFAULT_MW = 10.0


def get_outputfile(datafile, iteration):
    dirname, basename = os.path.split(datafile)
    stem = os.path.splitext(basename)[0]
    return os.path.join(dirname, 'bsmem_%d_%s.fits' % (iteration, stem))


def run_bsmem(args, outputfile):
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


def reconst_using_model(datafile, outputfile, dim, modeltype, modelwidth,
                        pixelsize=None, uvmax=None):
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
    run_bsmem(args, outputfile)


def reconst_using_image(datafile, outputfile, dim, pixelsize, imagehdu,
                        uvmax=None):
    imagefile = 'tempsf.fits'
    imagehdu.writeto(imagefile, overwrite=True)
    args = [BSMEM, '--noui',
            '--data=%s' % datafile,
            '--clobber', '--output=%s' % outputfile,
            '--dim=%d' % dim,
            '--pixelsize=%f' % pixelsize,
            '--sf=%s' % imagefile]
    if uvmax is not None:
        args += ['--uvmax=%f' % uvmax]
    run_bsmem(args, outputfile)


def run_grey_basic(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   modeltype=DEFAULT_MT, modelwidth=DEFAULT_MW):
    reconst_using_model(datafile, get_outputfile(datafile, 1), dim,
                        modeltype, modelwidth, pixelsize=pixelsize)


def run_grey_2step(datafile, dim=DEFAULT_DIM, pixelsize=None,
                   modeltype=DEFAULT_MT, modelwidth=DEFAULT_MW,
                   uvmax1=2.0e6, fwhm=2.0, threshold=0.05):
    # :TODO: choose automatic pixelsize outside of BSMEM?
    #        or run 1 iteration on full dataset?
    # :TODO: intelligent defaults for uvmax1, fwhm?
    out1file = get_outputfile(datafile, 1)
    reconst_using_model(datafile, out1file, dim, modeltype, modelwidth,
                        pixelsize=pixelsize, uvmax=uvmax1)
    with fits.open(out1file) as hdulist:
        imagehdu = makesf(hdulist[0], fwhm, threshold)
    reconst_using_image(datafile, get_outputfile(datafile, 2), dim, pixelsize,
                        imagehdu)
