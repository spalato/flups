# flups.calibration
# tools for maintaining calibrations 

import numpy as np

# I need a small object for the calibrations..

def load_calibration(which="latest"):
    raise NotImplementedError

def list_calibrations():
    raise NotImplementedError

# def calibrate(pix, b0 : float, b1:float, index:int):
#     """
#     Compute calibration as `wl = b1*(pix + 1 - index) + b0` # !!!check

#     Parameters
#     ----------
#     pix : array-like
#         Pixel values
#     b0 : float
#         Initial value
#     b1 : float
#         Calibration slope
#     index : 1 or 0 
#     """
#     raise NotImplementedError

