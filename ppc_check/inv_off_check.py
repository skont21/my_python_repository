import os
import re
import sys

flags = ["FORCE","DRF","LOVE","BUSY","MALF","COMER","STOPPED"]

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CBOLD = '\33[1m'
CURL = '\33[4m'
CEND = '\33[0m'

def get_iob_existance(iobName):
    cmd = "iobaccess read " + iobName
    x = os.popen(cmd).read().strip()
    if not x:
        ex = False
    else:
        ex = True
    return ex

# get_number_of_inverters : returns the number of inverters

def get_number_of_inverters():
	cmd = "iobtap -n pvarray"
	x = os.popen(cmd).read()
	y = re.findall("pvarray([0-9]*)", x)
	lst = []
	for num in y:
    		num = int(num)
    		if num not in lst:
        		lst.append(num)
	return len(lst)

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
		status=[]
    return status

# get_iob_value : reads the value of an iob and returns the value in float type if it is analogue or in string type if it is not.

def get_iob_value(iobName):
	cmd = "iobaccess read " + iobName + " val | awk '{print $3}'"
	x = os.popen(cmd).read().strip()
	if re.search("S", x) or re.search("ON", x) or re.search("OFF", x) or re.search("ZR", x): #to capture LRs and STATES
		return x
	else:
		try:
			result = float(x)
			return result
		except:
			return None

iob = "ppc:OnOff"
ppc_onoff=[]
ppc_onoff_states = {"S4":"OFF","S3":"ON","ZR":"DEFAULT"}

val = str(get_iob_value(iob))
status = " ".join(get_iob_status(iob))


ppc_onoff.append([val,status])


print '\n' + CBOLD + CURL + "PPC ON/OFF COMMAND:" + CEND +'\n'

if val == "S4":
	print CRED + CBOLD +"PPC Central Inverter ON/OFF command (ppc:OnOff): " + "OFF (4) "  + CEND + " with status: " + CBOLD + status + CEND + "\n"
elif val == "S3":
	print CGREEN + CBOLD + "PPC Central Inverter ON/OFF command (ppc:OnOff): " + "ON (3) " + CEND + " with status: " + CBOLD + status + CEND + "\n"
elif val == "ZR":
	print CBLUE + CBOLD + "PPC Central Inverter ON/OFF command (ppc:OnOff): " + "DEFAULT (8) " + CEND + " with status: " + CBOLD + status + CEND + "\n"
elif val == "None":
	print CRED + CBOLD + "There is not ON/OFF Service in this plant" + CEND
	sys.exit()
else:
	print CYELLOW  + CBOLD + "WARNING : PPC Central Inverter ON/OFF command (ppc:OnOff): " + "UNDEFINED" + " " + CEND + " with status: " + CBOLD + status + CEND + "\n"


cmd = "iobtap -n pvarray[0-9]*:INV_OFF$"
x = os.popen(cmd).read()
inv_off_iobs = re.findall("@?[^:]pvarray[0-9]*:INV_OFF",x)

inv_off = []
errors = []
warnings = []
inv_onoff_states = {"S1":"OFF","S2":"ON","ZR":"DEFAULT"}

for iob in inv_off_iobs:
    val = str(get_iob_value(iob))
    status = " ".join(get_iob_status(iob))
  
    if (val == "S2" and ppc_onoff[0] == "S4") or (val == "S1" and ppc_onoff[0] == "S3"):
	errors.append(CRED + CEBOLD + "ERROR : Inverter" + iob.split("y")[1].split(":")[0] + " ON/OFF command is" + inv_onoff_states[val] + "while PPC Central Inverter ON/OFF command (ppc:OnOff) is " + ppc_onoff_states[ppc_onoff[0]])
      
    if status:
	warnings.append(CYELLOW + CBOLD + "WARNING : Inverter" + iob.split("y")[1].split(":")[0] + " ON/OFF command STATUS is " +  status + CEND) 

print CBOLD + CURL + "INVERTERS ON/OFF COMMANDS:" + CEND +'\n'

if (not errors) and (not warnings):
	print CGREEN + CBOLD + "EVERYTHING IS OK" + CEND
elif errors:
	for error in errors:
		print error +'\n'
else:
	if len(warnings)>100:
		for warning in warnings[0:100]:
			print warning + '\n'
		print CYELLOW + CBOLD + CURL + "There are still" + str(len(warnings)-100) + "that are note being displayed" + CEND
	else:
		for warning in warnings:
			print warning + '\n'
