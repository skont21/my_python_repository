import os
import re
import sys

flags = ["FORCE","DRF","LOVE","BUSY","MALF","COMER","STOPPED"]

CRED = '\33[91m'
CGREEN = '\33[4m'
CBOLD = '\33[1m'
CEND = '\33[0m'
CGREENBG  = '\33[42m'
CREDBG    = '\33[41m'

def hex2bin(ini_string):
    n = int(ini_string, 16)
    bStr = ''
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    res = bStr
    return str(res)

def get_iob_status(iobName):
    cmd = "iobaccess read " + iobName + " stat_wrd | awk '{print $3}'"
    x = os.popen(cmd).read().strip()
    if not x:
        status = ["This IOB does not exist"]
    else :
        x=x[len(x)-2:len(x)]
        st = hex2bin(x)
	if len(st) == 8 :
		st=st[1:len(st)]
        stat_wrd = "0"*(len(flags)-len(st))+st 
        status=[]
        for i in range(0,len(flags)) :
            if stat_wrd[i] == "1":
                status.append(flags[i])
	if not status:
		status=["OK"]
    return status



iob =sys.argv[1]
state = get_iob_status(iob)
print CRED + CBOLD +"IOB Status of {" + iob +  "}:" + " ".join(state) + CEND + " " + "\n"

