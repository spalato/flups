# flups
Analysis tools for FLUPS @ EDyx. 

The repository is also used to work on experimental code.

## Installation

First you need to clone the current repository. You can use a graphical tool (ex: Github Desktop), or the following command:
```
git clone https://github.com/spalato/flups
```

Then you should install the module in development mode using `pip`. In the `flups/` directory (where you find `setup.py`), run:
```
pip install -e .
```

To test the installation, try:
```
python -c "import flups"
```
If no error message is printed, the installation is successful.

## Overview

Currently, the module contains the following components:
- `io.py`: tools to read and write data files.
- `calib.py`: tools to handle wavelength calibrations.
- `analysis.py`: data processing tools.
- `plot_utils.py`: for quick plotting.


The reposiory also contains the following folders, which are not part of the
python module.
- `npe_debug`: Niko's code for acquisition in Andor Solis.

## Scripts
- `collect_asc.py`: Collect a series of `.asc` files into a single text archive.

  To execute on a complete directory, using PS: 
  > `ls -Directory | %{$_.Name} | %{python -m flups.collect_asc -o "<root>_$_.txt" "$_/*sig*.asc"}`
