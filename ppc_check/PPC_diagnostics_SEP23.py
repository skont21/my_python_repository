import os
import time
import re
import sys


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


# get_number_of_smartloggers : returns the number of smartloggers

def get_number_of_smartloggers():
	cmd = "iobtap -n sppc"
	x = os.popen(cmd).read()
	y = re.findall("sppc([0-9]*)", x)
	lst = []
	for num in y:
    		num = int(num)
    		if num not in lst:
        		lst.append(num)
	return len(lst)


# get_ioblog : returns the outcome of the ioblog process as a list of lists. Each list contains the elements of one line of the ioblog output.

def get_ioblog(seconds, ioblog_period, *iobs):
	cmd = "ioblog -p " + str(ioblog_period) + " " + (' '.join(map(str, iobs)))
    	x = os.popen(cmd)
   	time.sleep(seconds)
    	os.popen("killall ioblog")
    	result_raw = x.read()
    	lines = result_raw.splitlines()
    	result = []
    	for line in lines:
        	result.append(line.split())
    	return result


# get_number_of_test_inverter : gets the inverter number from the user and returns it as a string

def get_number_of_test_inverter():
    	raw_num = raw_input("\nPlease enter test inverter number: ")
  	try:
        	num = int(raw_num)
    	except:
        	sys.exit(raw_num + " is a wrong value!\nExiting program...\n")
    	if num < 10:
        	num_string = "00" + str(num)
    	elif num >= 10 and num < 100:   
        	num_string = "0" + str(num)
    	elif num >= 1000:
        	sys.exit("Only numbers up to 999 are supported!\nExiting program...\n")
    	else:
        	num_string = str(num)
    	return num_string


# get_ppc_related_iobs_of_inverter : selects the PPC related iobs from the inverter app based on specific search keys and returns them in a list

def get_ppc_related_iobs_of_inverter(inverterName):
	cmd = "iobtap -n pvarray"
	x = os.popen(cmd).read()
	search_keys = ["PAC", "QAC", "ACTP", "INV_OFF", "VAR_MOD", "W_MOD"]
	ppc_related_iobs = []
	all_iobs = re.findall((inverterName + "[^ ]*"), x)
	for iob in all_iobs:
		for key in search_keys:
			if re.search(key, iob):
				if iob not in ppc_related_iobs:
					ppc_related_iobs.append(iob)
	sorted(ppc_related_iobs)
	return ppc_related_iobs


# get_inverter_state() : prints the PPC related iobs of the inverter selected by the user

def get_inverter_state():
	inverterName = "pvarray" + get_number_of_test_inverter() + ":"
	print "Reading " + inverterName
	ppc_realted_iobs = get_ppc_related_iobs_of_inverter(inverterName)
	for iobName in ppc_realted_iobs:
		if get_iob_value(iobName) != None:
			print iobName + " "*(35-len(iobName)) + " " + str(get_iob_value(iobName))
		else:
			print "Problem with reading iob " + iobName
	iobs_to_check = ["ACTP_LR", "ACTP_LR_F", "REACTP_LR", "REACTP_LR_F", "ACTP_SPPS", "_ACTP_SPPS", "ACTP_SPP", "REACTP_SPPS", "_REACTP_SPPS", "REACTP_SPP"]
	for iob in iobs_to_check:
		iobName = inverterName + iob
		if iobName not in ppc_realted_iobs:
			print iobName + " "*(35-len(iobName)) + " not found"	

# get_PPC_state() : UNDER CONSTRUCTION

def get_PPC_state():
	print "Reading PPC:"
	ppc_local_enable_iobs = ["apc:En0_S", "apc:RateEn0_S", "apc:FCEn0_S", "apc:REn0_S", "apc:SLEn0_S", "rpc:En0_S", "rpc:RateEn0_S", "pfc:En0_S", "rpc:VCEn0_S", "avr:En0_S"]
	ppc_remote_enable_iobs = ["apc:En1_S", "apc:RateEn1_S", "apc:FCEn1_S", "apc:REn1_S", "apc:SLEn1_S", "rpc:En1_S", "rpc:RateEn1_S", "pfc:En1_S", "rpc:VCEn1_S", "avr:En1_S"]
	ppc_local_setpoint_iobs = ["apc:PSP0_S", "apc:RateUp0_S", "apc:RateDown0_S", "apc:FSP0_S", "apc:RPSP0_S", "apc:SSP0_S", "rpc:QSP0_S", "rpc:Rate0_S", "pfc:PFSP0_S", "rpc:VSP0_S", "avr:VSP0_S"]
	ppc_remote_setpoint_iobs = ["apc:PSP1_S", "apc:RateUp1_S", "apc:RateDown1_S", "apc:FSP1_S", "apc:RPSP1_S", "apc:SSP1_S", "rpc:QSP1_S", "rpc:Rate1_S", "pfc:PFSP1_S", "rpc:VSP1_S", "avr:VSP1_S"]
	for iobName in ppc_iobs:
		if get_iob_value(iobName) != None:
			print iobName + " "*(35-len(iobName)) + str(get_iob_value(iobName))
		else:
			print "Problem with reading iob " + iobName
	iobs_to_check = ["ACTP_LR", "ACTP_LR_F", "REACTP_LR", "REACTP_LR_F", "ACTP_SPPS", "_ACTP_SPPS", "ACTP_SPP", "REACTP_SPPS", "_REACTP_SPPS", "REACTP_SPP"]
	for iob in iobs_to_check:
		iobName = inverterName + iob
		if iobName in ppc_realted_iobs:
			print iobName + " "*(35-len(iobName)) + " found"
		else:
			print iobName + " "*(35-len(iobName)) + " not found"	



########################################################################################################################################
#################################################           MAIN CODE        ###########################################################
########################################################################################################################################


CRED = '\33[91m'
CGREEN = '\33[4m'
CBOLD = '\33[1m'
CEND = '\33[0m'
CGREENBG  = '\33[42m'
CREDBG    = '\33[41m'
CBLUEBG    = '\33[44m'
CYELLOWBG    = '\33[43m'


print "\n"
print "Number of inverters in the plant: " + CBLUEBG + CBOLD + " " + str(get_number_of_inverters()) + " " + CEND + "\n"

print "Number of smart-loggers in the plant: " + CBLUEBG + CBOLD + " " + str(get_number_of_smartloggers()) + " " + CEND + "\n"



if get_iob_value("apc:PlantSt") == "ZR":
	print "PPC Plant Status (apc:PlantSt): " + CREDBG + CBOLD + " " + "Powered-off" + " " + CEND + "\n"
elif get_iob_value("apc:PlantSt") == "ON":
	print "PPC Plant Status (apc:PlantSt): " + CGREENBG + CBOLD + " " + "Powered-on" + " " + CEND + "\n"
else:
	print "PPC Plant Status (apc:PlantSt): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


if get_iob_value("ppc:OnOff") == "S4":
	print "PPC Central Inverter ON/OFF command (ppc:OnOff): " + CREDBG + CBOLD + " " + "OFF" + " " + CEND + "\n"
elif get_iob_value("ppc:OnOff") == "S3":
	print "PPC Central Inverter ON/OFF command (ppc:OnOff): " + CGREENBG + CBOLD + " " + "ON" + " " + CEND + "\n"
else:
	print "PPC Central Inverter ON/OFF command (ppc:OnOff): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


if get_iob_value("ppc:CSel") == "ZR":
	print "PPC Mode - Local/Remote (ppc:CSel): " + CBLUEBG + CBOLD + " " + "Local" + " " + CEND + "\n"
elif get_iob_value("ppc:CSel") == "ON":
	print "PPC Mode - Local/Remote (ppc:CSel): " + CBLUEBG + CBOLD + " " + "Remote" + " " + CEND + "\n"
else:
	print "PPC Mode - Local/Remote (ppc:CSel): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"
















































