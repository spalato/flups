# flups.io: tools for reading and writing files

import re
import logging
import numpy as np
from .calib import load_latest, calibration
logger = logging.getLogger(__name__)


def read_asc(fname):
    """
    Read a single `asc` file, the ASCII format from Andor Solis.

    Parameters
    ----------
    fname : str, path-like
        File to open.

    """
    logger.debug("Loading `.asc` file: %s", fname)
    with open(fname) as f:
        contents = f.read()
    meta_start = contents.find("Date and Time")
    logger.debug("  Metadata at %i", meta_start)
    if meta_start == 0:
        start = contents.find("\n"*3)
        end = None
    else:
        start = None
        end = contents.find("\n"*3)
    return np.loadtxt((ln for ln in contents[start:end].splitlines() if ln), delimiter=",")


def load_asc_series(fnames, calib=None, step=None):
    """
    Load a series of Andor Solis `asc` files. Computes the delays and wl.

    Parameters
    ----------
    fnames: iterable of filenames.
        The list of files to load.
    calib: flups.calib.calibration; array-like of shape (2,) or None
        Wavelength calibration used to convert the pixels to wavelength.
        The parameters can also be passed as an array: `[b0, b1]`, where `b0` is
        the initial value assuming 0-based indexing. If `None` (default), uses
        the lastest calibration from `flups.calib`
    step: float or None
        The timestep, in fs. If `None` (default), the timestep will be found
        from the filename as `_sNNN_`.

    Returns
    -------
    delays : (M,) np.ndarray
        Delays, fs. Starts from 0.
    wl : (N,) np.ndarray
        Wavelengths, nm.
    trace : (M,N) np.ndarray
        Signal intensity
    """
    # read the data
    trace = [read_asc(fn)[:,1] for fn in fnames]
    # TODO: change to proper error.
    assert np.allclose([t.size for t in trace], trace[0].size) # check they all have the same length
    trace = np.array(trace)
    # compute time axis
    step = step or float(re.search("_s(\d+)_", fnames[0]).group(1))
    n_pix = trace.shape[1]
    delays = np.arange(0, trace.shape[0])*step
    # compute wavelength axis
    pixels = np.arange(n_pix)
    if calib is None:
        calib = load_latest()
    if isinstance(calib, calibration):
        wl = calib.calibrate(pixels)
    else:
        b0, b1 = calib
        wl = b0 + b1*pixels
    assert trace.shape == (delays.size, wl.size)
    return delays, wl, trace


def load_npz(fname):
    """
    Load data from an npz archive.

    Parameters
    ----------
    fname : str
        Path to the archive.

    Returns
    -------
    delays : (M,) np.ndarray
        Delays, fs. Starts from 0.
    wl : (N,) np.ndarray
        Wavelengths, nm.
    trace : (M,N) np.ndarray
        Signal intensity
    """
    df = np.load(fname)
    delays = df["delays"]
    trace = df["trace"]
    wl = df["wl"]
    return delays, wl, trace


def load_txt(fname):
    """
    Load data from a ".txt" file.

    The first element is discarded (ie: top left corner), the first column 
    contains the delays, the first row contains the wavelength, and the rest 
    contains the signal intensity.

    Parameters
    ----------
    fname : str
        Path to the archive.

    Returns
    -------
    delays : (M,) np.ndarray
        Delays, fs. Starts from 0.
    wl : (N,) np.ndarray
        Wavelengths, nm.
    trace : (M,N) np.ndarray
        Signal intensity
    """
    cnt = np.loadtxt(fname)
    delays = cnt[1:,0]
    wl = cnt[0,1:]
    trace = cnt[1:,1:]
    return delays, wl, trace


def save_txt(fname, delays, wl, trace):
    """
    Saves the data in a `.txt` file.

    The first element is undefined, the first column contains the delays, the 
    first row contains the wavelengths and the rest contains the signal
    intensity.

    Parameters
    ----------
    fname : str
        Path to the archive.
    delays : (M,) np.ndarray
        Delays, fs. Starts from 0.
    wl : (N,) np.ndarray
        Wavelengths, nm.
    trace : (M,N) np.ndarray
        Signal intensity

    See also
    --------
    flups.io.load_txt
    """
    cnt = np.full([s+1 for s in trace.shape], np.nan)
    cnt[1:,0] = delays
    cnt[0,1:] = wl
    cnt[1:,1:] = trace
    np.savetxt(fname, cnt, fmt="%.06g")
