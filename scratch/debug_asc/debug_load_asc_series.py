# Something got confused, and the FLUPS data was saved with metadata at the END
# instead of the start. Let's try to handle both cases.

import sys

def locate_datetime(contents):
    return contents.find("Date and Time")

fnames = sys.argv[1:]

for fn in fnames:
    with open(fn) as f:
        contents = f.read()
    print(fn, locate_datetime(contents))
