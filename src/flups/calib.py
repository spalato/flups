# flups.calibration
# tools for maintaining calibrations 

import os.path as pth
from datetime import date as datetype, datetime
from dataclasses import dataclass
import numpy as np
import yaml
import logging

logger = logging.getLogger(__name__)

# I need a small object for the calibrations..
@dataclass(frozen=True)
class calibration:
    """
    Calibration information for converting pixel number to wavelength (nm).
    
    Thecalibration uses 0-based indexing, ie: the first pixel is number 0.

    Parameters
    ----------
    date : str
        Calibration name (typically a date)
    b0 : float
        Intercept
    b1 : float
        Slope
    """
    name: datetype
    b0: float
    b1: float
    
    @classmethod
    def from_record(cls, name:str, b0: float, b1: float,
        zero_indexed: bool=True):
        """
        Load a calibration from a parameter record.

        Parameters
        ----------
        name : str
            Calibration name, please start with a date in ISO format (YYYY-MM-DD).
        b0 : float
            Intercept
        b1 : float
            Slope
        zero_indexed : bool
            Indicate if the supplied parameters use 0-based indexing. If 
            `zero_indexed` is False, the 
        """
        if isinstance(name, datetype):
            name = name.strftime("%Y-%m-%d")
        else:
            try:
                date = datetype.fromisoformat(name[:10])
            except ValueError:
                logger.warn(f"Calibration name does not start by valid date: {name}")
        if not zero_indexed: # convert from 1-indexing to 0-indexing
            b0 = b0 + b1
        return cls(name, b0, b1)

    def calibrate(self, i):
        """Converts pixel index `i` to wavelength, in nm.
        """
        return self.b0 + self.b1*i

    @property
    def coeffs(self):
        return np.array([self.b0, self.b1])


DEFAULT_CALIB_FILE = pth.join(
    pth.dirname(pth.realpath(__file__)),
    "calibrations.yaml"
)

def load_latest():
    calibs = list_calibrations()
    return max(calibs, key=lambda v: v.name)


def list_calibrations(file=DEFAULT_CALIB_FILE): # this can handle specific directories
    with open(file, "r") as f:
        records = yaml.safe_load(f)
    calibrations = [calibration.from_record(name, **values) 
        for name, values in records.items()]
    return calibrations
