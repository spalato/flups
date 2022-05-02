import logging
from glob import glob
from argparse import ArgumentParser
import re
import numpy as np
from .io import load_asc_series, save_txt
# usage, win:`ls -Directory | %{$_.Name} | %{python -m flups.collect_asc -o "$((Get-Item .).Name)_$_.txt" "$_/*sig*.asc"}`


def frame_idx(fname):
    """Get frame index from filename: `name0001.asc` returns 1"""
    return int(fname[-8:-4])

if __name__!= "__main__":
    import warnings
    warnings.warn("This file should be run as a script. Exiting...")
    import sys
    sys.exit(1)

logging.basicConfig(
    format="%(levelname)5s | %(name)s: %(message)s",
    level=logging.INFO
)


parser = ArgumentParser(description="Collects a series of `asc` into a single `.txt` file.",
epilog="""usage, MSW:`ls -Directory | %{$_.Name} | %{python -m flups.collect_asc -o "$((Get-Item .).Name)_$_.txt" "$_/*sig*.asc"}`""",
)
# add possibility to specify timestep
parser.add_argument("-s", "--step", help="Time step")
# add possibility to specify wavelength calibrations
# add way to save to npz archive
#  add debug level
parser.add_argument("-o", "--output", help="Output root name")
parser.add_argument("input", help="Input pattern (`glob`).")

args = parser.parse_args()

fnames = sorted(glob(args.input), key=frame_idx)

args.output = args.output or fnames[0][:-8]+".txt"

logging.info("Loading files...")
data = load_asc_series(fnames, args.step)

logging.info(f"Saving to: {args.output}")
save_txt(args.output, *data)
