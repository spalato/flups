import logging
from glob import glob
from argparse import ArgumentParser
import re
import numpy as np
from .io import load_asc_series, save_txt

if __name__!= "__main__":
    import warnings
    warnings.warn("This file should be run as a script. Exiting...")
    import sys
    sys.exit(1)

logging.basicConfig(
    format="%(levelname)5s | %(name)s: %(message)s",
    level=logging.INFO
)


parser = ArgumentParser(description="Collects a series of `asc` into a single `.txt` file.")
# add possibility to specify timestep
parser.add_argument("-s", "--step", help="Time step")
# add possibility to specify wavelength calibrations
# add switch to save to npz archive
parser.add_argument("-o", "--output", help="Output root name")
parser.add_argument("input", help="Input pattern (`glob`).")

args = parser.parse_args()

fnames = glob(args.input)

args.output = args.output or fnames[0][:-8]+".txt"

logging.info("Loading files...")
data = load_asc_series(fnames, args.step)

logging.info(f"Saving to: {args.output}")
save_txt(args.output, *data)
