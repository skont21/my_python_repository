import os
import re
import sys

def hex2bin(ini_string):
    n = int(ini_string, 16)
    bStr = ''
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    res = bStr
    return str(res)

def get_iob_ovr(iobName):
    cmd = "iobaccess read " + iobName + " ctl_wrd | awk '{print $3}'"
    x = os.popen(cmd).read().strip()
    if not x:
	ovr = "This IOB does not exist"
    else:
    	x=x[7]
    	ctl = hex2bin(x)
    	ovr = ctl[len(ctl)-1]
    return ovr

iob=sys.argv[1]
OVR = get_iob_ovr(iob)
print "Ovewrite: " + OVR
