# analysis and data processing functions.
import os
import numpy as np
from scipy.ndimage import median_filter
from scipy.constants import eV, h, c, nano, femto, pi, centi
import toml
import logging

logger = logging.getLogger(__name__)
__dirpath = os.path.dirname(os.path.abspath(__file__))

def nm2ev(x):
    return h*c/x/nano/eV


def ev2nm(x):
    return h*c/x/eV/nano


def nm2cmi(x):
    return centi/x/nano


def cmi2nm(x):
    return centi/x/nano


def despike_median(data, size, threshold=5):
    cutoff = np.std(data) * threshold
    filtered = median_filter(data, size=size)
    reject = np.abs(filtered-data) > cutoff
    despiked = np.copy(data)
    despiked[reject] = filtered[reject]
    return despiked


def lognorm(x, amp, x0, delta, gamma):
    """
    Lognormal peak model. Designed for use with wavenumbers.

    The function is:
    y = amp * exp(-ln(2) [ln(1+2 gamma * [x-x0] / delta)/gamma]^2)

    Parameters
    ----------
    x : (N,) array-like
        Independant variable. Typically wavenumbers
    amp : float
        Amplitude parameters (h)
    x0 : float
        Peak position.
    delta : float > 0
        Width parameter
    gamma: float
        Asymmetry parameter

    Returns
    -------
    y : (N,) array-like
        Peak values
    """
    arg = np.maximum(2 * gamma * (x - x0) / delta, -1+1E-6)
    return amp * np.exp(-np.log(2) * ((np.log1p(arg)) / gamma) ** 2)


# load lognormal parameters
default_ref_spectra = {}
#try:
with open(os.path.join(__dirpath, "refspec_Gerecke_RSI_2016.toml")) as f:
    default_ref_spectra.update(toml.load(f))
#except Exception:
#    logger.warning("Loading reference fluorescence spectra failed.")


def ref_spec_wn(wnm, reference, database=default_ref_spectra):
    """
    Reference spectrum as a photon counts over wavenumbers.

    Parameters
    ----------
    wnm : (N,) array-like
        Wavenumbers in inverse cm.
    reference : string or parameters
        Reference name or parameters. See note.
    database : mapping
        Dictionnary mapping reference name to parameters. Defaults to the contents of `refspec_Gerecke_RSI_2016.toml`.

    Returns
    -------
    y : (N,) array-like
        Fluorescence spectrum in units of photon counts/wavenumber

    Notes
    -----
    When passing parameters directly or un the database, the parameters must be a list of M contributions each with
    4 parameters (see `lognorm`).
    """
    if isinstance(reference, str):
        try:
            params = database[reference]
        except KeyError:
            raise KeyError(f"Reference spectrum name not found: {reference}. Must be one of: {list(database.keys())}.")
    else:  # try using parameters directly
        params = reference
    y = np.zeros_like(wnm, dtype=float)
    for p in params:
        y += lognorm(wnm, *p)
    return y


def ref_spec_wl(wl, reference, database=default_ref_spectra):
    """
    Reference spectrum as a photon counts over wavelength.

    Parameters
    ----------
    wnm : (N,) array-like
        Wavelength in nm.
    reference : string or parameters
        Reference name or parameters. See `ref_spec_wn`.
    database : mapping
        Dictionnary mapping reference name to parameters. See: `ref_spec_wn`.

    Returns
    -------
    y : (N,) array-like
        Fluorescence spectrum in units of photon counts/wavelength.

    See also
    --------
    `ref_spec_wn`: Most arguments are passed to this function.
    """
    wnm = nm2cmi(wl)
    return ref_spec_wn(wnm, reference, database)*wl**2
