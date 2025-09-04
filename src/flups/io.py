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

    # def __fixup(line): # Uncomment in case of emergency...
    #     """huh.. The wavelength is saved using , as decimal separator, while the value uses `.`"""
    #     if line.count(",") > 1:
    #         line = line.replace(",", ".", 1)
    #     return line
    # return np.loadtxt((__fixup(ln) for ln in contents[start:end].splitlines() if ln), delimiter=",")
    return np.loadtxt((ln for ln in contents[start:end].splitlines() if ln), delimiter=",")


def load_asc_series(fnames, calib=None, step="first"):
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
        the first column of the first file.
    step: float, or str in {"first", "filename"}. Default: "first".
        The timestep, in ps.
        If "first" (default), the position is read from the first pixel of each spectrum.
        If "filename", the timestep will be found from the filename as `_sNNN_`.

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
    # TODO: actually read the pixel/wl axis from the first file.
    # skip that calibration step, Marco was not using it anyways. It's easy to replace at the end.
    nfiles = len(fnames)
    logger.debug(f"nfiles: {nfiles}")
    fnames = iter(fnames)
    first = read_asc(next(fnames))
    wl = first[:, 0]  # we are reading the first file twice, but whatever
    logger.debug(f"wl.size: {wl.size}")
    trace = [first[:,1]]
    for fn in fnames:
        trace.append(read_asc(fn)[:, 1])
    # TODO: change to proper error.
    assert np.allclose([t.size for t in trace], trace[0].size)  # check they all have the same length
    trace = np.array(trace)
    logger.debug(f"Trace shape: {trace.shape}")
    assert trace.shape == (nfiles, wl.size)
    # compute time axis
    if step == "first":
        delays = trace[:,0]
    elif step == "filename":
        step = float(re.search(r"_s(\d+)_", fnames[0]).group(1))
        delays = np.arange(0, trace.shape[0])*step
    else:
        try:
            step = float(step)
        except ValueError:
            raise ValueError("step argument not understood. Must be a float, convertible to a float, or in "
                             "{'first', 'filename'}.")
        delays = np.arange(0, trace.shape[0]) * step
    if delays[1]<delays[0]:
        delays = delays[::-1]
        trace = trace[::-1,:]
    # compute wavelength axis
    n_pix = trace.shape[1]
    pixels = np.arange(n_pix)
    if calib is None:
        pass  # keep the data from the first file.
    elif isinstance(calib, calibration):
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
