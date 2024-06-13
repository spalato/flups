import logging
from glob import glob
from argparse import ArgumentParser
import re
import numpy as np
from .io import load_asc_series, save_txt
# usage, win:`ls -Directory | %{$_.Name} | %{python -m flups.collect_asc -o "$((Get-Item .).Name)_$_.txt" "$_/*sig*.asc"}`
__HAS_PBAR = False
try:
    from tqdm import tqdm
    __HAS_PBAR = True
    from tqdm.contrib.logging import logging_redirect_tqdm
except:
    pass

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
parser.add_argument("-s", "--step",
                    default="first",
                    help="Time step. Accepts a number, 'first' or 'filename'."
                         "If 'first', the delay is read from the first pixel of each spectrum."
                         "If 'filename', find timestep from filename. Default: 'first'")
# add possibility to specify wavelength calibrations
# add way to save to npz archive
#  add debug level
parser.add_argument("--debug", action="store_true", help="Set logging level to debug.")
parser.add_argument("--no-pbar", action="store_true", help="Don't use a progress bar.")
parser.add_argument("-o", "--output", help="Output root name")
parser.add_argument("input", help="Input pattern (`glob`).")

args = parser.parse_args()
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)

fnames = sorted(glob(args.input), key=frame_idx)



args.output = args.output or fnames[0][:-8]+".txt"

logging.info("Loading files...")
if __HAS_PBAR and not args.no_pbar:
    fnames = tqdm(fnames, total=len(fnames))
data = load_asc_series(fnames, step=args.step)

logging.info(f"Saving to: {args.output}")
save_txt(args.output, *data)
