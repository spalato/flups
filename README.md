# flups
Analysis tools for FLUPS @ EDyx

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

## Scripts
- `collect_asc.py`: Collect a series of `.asc` files into a single text archive.

  To execute on a complete directory, using PS: 
  > `ls -Directory | %{$_.Name} | %{python -m flups.collect_asc -o "<root>_$_.txt" "$_/*sig*.asc"}`
