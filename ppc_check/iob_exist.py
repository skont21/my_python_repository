import os
import re
import sys

def get_iob_existance(iobName):
    cmd = "iobaccess read " + iobName
    x = os.popen(cmd).read().strip()
    if not x:
        ex = False
    else:
        ex = True
    return ex

iob=sys.argv[1]
Existance = get_iob_existance(iob)
print "This IOB exists : " + str(Existance)
