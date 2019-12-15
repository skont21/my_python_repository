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


# iob_exists : checks whether an iob exists and returns True or False

def iob_exists(iobName):
	cmd = "iobaccess read " + iobName
	x = os.popen(cmd).read().strip()
	if not x:
		return False
	else:
		return True


# hex2bin : converters hexadecimal to binary
 
def hex2bin(ini_string):
	n = int(ini_string, 16)
	bStr = ''
	while n > 0:
		bStr = str(n % 2) + bStr
		n = n >> 1
	res = bStr
	return str(res)


# get_iob_status : Reads the status of an iob and returns a list containing the active flags, an empty list if there are no flags, or ["DOES NOT EXIST"].

def get_iob_status(iobName):

	flags = ["FORCE","DRF","LOVE","BUSY","MALF","COMER","STOPPED"]
	cmd = "iobaccess read " + iobName + " stat_wrd | awk '{print $3}'"
	x = os.popen(cmd).read().strip()
	status = []
	if not x:
		status = ["DOES NOT EXIST"]
	else :
		x=x[len(x)-2:len(x)]  # keeps the last 2 digits from the hexadecimal return value
		st = hex2bin(x)
		if len(st) == 8 :
			st=st[1:len(st)] # cuts the 8th bit, it does not correspond to any flag
		stat_wrd = "0"*(len(flags)-len(st))+st # fills the bit word with 0s on the left to get exactly 7 elements
		for i in range(0,len(flags)) :
			if stat_wrd[i] == "1":
				status.append(flags[i])
	return status


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


# display_PPC_enabled_functions() : prints the enabled PPC functions and their main attributes

def display_PPC_enabled_functions():
	
	print "====================== P RELATED FUNCTIONS ======================\n"	

	if get_iob_value("apc:En") == "ON":
		print "P CONTROL (apc:En): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
		print "P CONTROL SETPOINT (apc:PSP0) : " + CGREENBG + CBOLD + " " + str(get_iob_value("apc:PSP0")) + " kW " + CEND + "  Measurement: " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:P0")) + " kW " + CEND + "\n"
		display_apc_Mode()
		if get_iob_value("apc:RateEn") == "ON":
			print "P-RAMP CONTROL (apc:RateEn): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
			print "P RAMP-UP SETTING (apc:RateUp0): " + CGREENBG + CBOLD + " " + str(get_iob_value("apc:RateUp0")) + " kW/min " + CEND + "\n"
			print "P RAMP-DOWN SETTING (apc:RateDown0): " + CGREENBG + CBOLD + " " + str(get_iob_value("apc:RateDown0")) + " kW/min " + CEND + "\n"
		elif get_iob_value("apc:RateEn") == "ZR":
			print "P-RAMP CONTROL (apc:RateEn): " + CYELLOWBG + CBOLD + " " + "DISABLED" + " " + CEND + "\n"
		if get_iob_value("apc:FCEn") == "ON":
			print "FREQ CONTROL (apc:FCEn): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
			if get_iob_value("apc:FUEn") == "ON":
				print "UNDER-FREQ CONTROL (apc:FUEn): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
	else:
		print "P CONTROL (apc:En): " + CYELLOWBG + CBOLD + " " + "DISABLED" + " " + CEND + "\n"
	
	print "\n====================== Q RELATED FUNCTIONS ======================\n"

	if get_iob_value("rpc:Func") == "S1":
		print "Q CONTROL (rpc:Func): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
		print "Q CONTROL SETPOINT (rpc:QSP0) : " + CGREENBG + CBOLD + " " + str(get_iob_value("rpc:QSP0")) + " kVAr " + CEND + "  Measurement: " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:Q0")) + " kVAr " + CEND + "\n"
		display_rpc_Mode()
	elif get_iob_value("rpc:Func") == "S2":
		print "Q(V) CONTROL (rpc:Func): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
		print "Q(V) CONTROL SETPOINT (rpc:VSP0) : " + CGREENBG + CBOLD + " " + str(get_iob_value("rpc:VSP0")) + " V " + CEND + "\n"
		display_rpc_Mode()
	elif get_iob_value("rpc:Func") == "S3":
		print "Q(P) CONTROL (rpc:Func): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
		display_rpc_Mode()
	elif get_iob_value("rpc:Func") == "S4":
		print "PF CONTROL (rpc:Func): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
		print "PF CONTROL SETPOINT (pfc:PFSP) : " + CGREENBG + CBOLD + " " + str(get_iob_value("pfc:PFSP")) + " " + CEND + "  Measurement: " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:PF")) + " " + CEND + "\n"
		display_pfc_UseRPC()
		if get_iob_value("pfc:UseRPC") == "ZR":
			display_pfc_Mode()
		elif get_iob_value("pfc:UseRPC") == "ON":		
			display_rpc_Mode()
	elif get_iob_value("rpc:Func") == "S5":
		print "PF(V) CONTROL (rpc:Func): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
	elif get_iob_value("rpc:Func") == "S6":
		print "PF(P) CONTROL (rpc:Func): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
	elif get_iob_value("rpc:Func") == "S7":
		print "AVR CONTROL (rpc:Func): " + CGREENBG + CBOLD + " " + "ENABLED" + " " + CEND + "\n"
		print "AVR CONTROL SETPOINT (avr:VSP0) : " + CGREENBG + CBOLD + " " + str(get_iob_value("avr:VSP0")) + " V " + CEND + "  Measurement: " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:V0")) + " V " + CEND + "\n"
		display_rpc_Mode()
	elif get_iob_value("rpc:Func") == "S0":
		print "ALL Q-RELATED CONTROLS (rpc:Func): " + CYELLOWBG + CBOLD + " " + "DISABLED" + " " + CEND + "\n"
	

def display_apc_PlantSt():
	if get_iob_value("apc:PlantSt") == "ZR":
		print "PPC Plant Status (apc:PlantSt): " + CREDBG + CBOLD + " " + "Powered-off" + " " + CEND + "\n"
	elif get_iob_value("apc:PlantSt") == "ON":
		print "PPC Plant Status (apc:PlantSt): " + CGREENBG + CBOLD + " " + "Powered-on" + " " + CEND + "\n"
	else:
		print "PPC Plant Status (apc:PlantSt): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


def display_ppc_OnOff():
	if get_iob_value("ppc:OnOff") == "S4":
		print "PPC Inverter ON/OFF central command (ppc:OnOff): " + CREDBG + CBOLD + " " + "OFF" + " " + CEND + "\n"
	elif get_iob_value("ppc:OnOff") == "S3":
		print "PPC Inverter ON/OFF central command (ppc:OnOff): " + CGREENBG + CBOLD + " " + "ON" + " " + CEND + "\n"
	else:
		print "PPC Inverter ON/OFF central command (ppc:OnOff): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


def display_ppc_CSel():
	if get_iob_value("ppc:CSel") == "ZR":
		print "PPC Mode - Local/Remote (ppc:CSel): " + CBLUEBG + CBOLD + " " + "Local" + " " + CEND + "\n"
		if get_iob_value("apc:CSelOvr_S") == "S1":
			print "P Mode is overwritten (apc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Remote" + " " + CEND + "\n"
		if get_iob_value("rpc:CSelOvr_S") == "S1":
			print "Q Mode is overwritten (rpc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Remote" + " " + CEND + "\n"
	elif get_iob_value("ppc:CSel") == "ON":
		print "PPC Mode - Local/Remote (ppc:CSel): " + CBLUEBG + CBOLD + " " + "Remote" + " " + CEND + "\n"
		if get_iob_value("apc:CSelOvr_S") == "S0":
			print "P Mode is overwritten (apc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Local" + " " + CEND + "\n"
		if get_iob_value("rpc:CSelOvr_S") == "S0":
			print "Q Mode is overwritten (rpc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Local" + " " + CEND + "\n"
	else:
		print "PPC Mode - Local/Remote (ppc:CSel): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"
		
		if get_iob_value("apc:CSelOvr_S") == "S1":
			print "P Mode is overwritten (apc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Remote" + " " + CEND + "\n"
		elif get_iob_value("apc:CSelOvr_S") == "S0":
			print "P Mode is overwritten (apc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Local" + " " + CEND + "\n"

		if get_iob_value("rpc:CSelOvr_S") == "S1":
			print "Q Mode is overwritten (rpc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Remote" + " " + CEND + "\n"
		elif get_iob_value("rpc:CSelOvr_S") == "S0":
			print "Q Mode is overwritten (rpc:CSelOvr_S): " + CYELLOWBG  +  CBOLD + " " + "Local" + " " + CEND + "\n"
		

def display_apc_Mode():
	if get_iob_value("apc:Mode") == "S0":
		print "P CONTROL LOOP (apc:Mode): " + CREDBG + CBOLD + " " + "Open Loop" + " " + CEND + "\n"
	elif get_iob_value("apc:Mode") == "S1":
		print "P CONTROL LOOP (apc:Mode): " + CGREENBG + CBOLD + " " + "Closed Loop" + " " + CEND + "\n"
	elif get_iob_value("apc:Mode") == "S2":
		print "P CONTROL LOOP (apc:Mode): " + CYELLOWBG + CBOLD + " " + "Closed Loop with Feed Forward" + " " + CEND + "\n"
	else:
		print "P CONTROL LOOP (apc:Mode): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


def display_rpc_Mode():
	if get_iob_value("rpc:Mode") == "S0":
		print "Q CONTROL LOOP (rpc:Mode): " + CREDBG + CBOLD + " " + "Open Loop" + " " + CEND + "\n"
	elif get_iob_value("rpc:Mode") == "S1":
		print "Q CONTROL LOOP (rpc:Mode): " + CGREENBG + CBOLD + " " + "Closed Loop" + " " + CEND + "\n"
	elif get_iob_value("rpc:Mode") == "S2":
		print "Q CONTROL LOOP (rpc:Mode): " + CYELLOWBG + CBOLD + " " + "Closed Loop with Feed Forward" + " " + CEND + "\n"

	else:
		print "Q CONTROL LOOP (rpc:Mode): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


def display_pfc_Mode():
	if get_iob_value("pfc:Mode") == "S0":
		print "PF CONTROL LOOP (pfc:Mode): " + CREDBG + CBOLD + " " + "Open Loop" + " " + CEND + "\n"
	elif get_iob_value("rpc:Mode") == "S1":
		print "PF CONTROL LOOP (pfc:Mode): " + CGREENBG + CBOLD + " " + "Closed Loop" + " " + CEND + "\n"
	elif get_iob_value("rpc:Mode") == "S2":
		print "PF CONTROL LOOP (pfc:Mode): " + CYELLOWBG + CBOLD + " " + "Closed Loop with Feed Forward" + " " + CEND + "\n"

	else:
		print "PF CONTROL LOOP (pfc:Mode): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


def display_pfc_UseRPC():
	if get_iob_value("pfc:UseRPC") == "ZR":
		print "Power Factor Control performed via (pfc:UseRPC): " + CREDBG + CBOLD + " " + "PF setpoints to inverters" + " " + CEND + "\n"
	elif get_iob_value("pfc:UseRPC") == "ON":
		print "Power Factor Control performed via (pfc:UseRPC): " + CGREENBG + CBOLD + " " + "Q setpoints to inverters" + " " + CEND + "\n"
	else:
		print "Power Factor Control performed via (pfc:UseRPC): " + CYELLOWBG  +  CBOLD + " " + "Undefined" + " " + CEND + "\n"


# check_ACTP_LRs(): checks all the ACTP_LR iobs and prints messages regarding their value and status 

def check_ACTP_LRs():
	cmd = "iobtap -n :ACTP_LR"
	x = os.popen(cmd).read()
	y = re.findall("[^ ]*[0-9]*:ACTP_LR ", x)
	for name in y:
		if not iob_exists(name):
			y.remove(name)
	value_count = 0
	status_count = 0
	
	if get_iob_value("apc:En") == "ON":		
		for iobName in y:
			if get_iob_value(iobName) != "ON":
				value_count += 1
				print CYELLOW  +  CBOLD + iobName + " is not ON " + CEND + "\n"
		if value_count == 0:
			print CGREENBG  +  CBOLD + "All ACTP_LR iob values are ON " + CEND + "\n" 		
	
	elif get_iob_value("apc:En") == "ZR":		
		for iobName in y:
			if get_iob_value(iobName) != "ZR":
				value_count += 1
				print CYELLOW  +  CBOLD + iobName + " is not OFF " + CEND + "\n"
		if value_count == 0:
			print CGREENBG  +  CBOLD + "All ACTP_LR iob values are OFF " + CEND + "\n" 

	for iobName in y:
		if len(get_iob_status(iobName)) != 0:
			status_count += 1
			print CYELLOW  +  CBOLD + iobName + " status is " + (' '.join(get_iob_status(iobName))) + CEND + "\n"
	if status_count == 0:
		print CGREENBG  +  CBOLD + "All ACTP_LR iob statuses are OK " + CEND + "\n" 	


# check_REACTP_LRs(): checks all the ACTP_LR iobs and prints messages regarding their value and status 

def check_REACTP_LRs():
	cmd = "iobtap -n :REACTP_LR"
	x = os.popen(cmd).read()
	y = re.findall("[^ ]*[0-9]*:REACTP_LR ", x)
	for name in y:
		if not iob_exists(name):
			y.remove(name)
	value_count = 0
	status_count = 0
	
	if get_iob_value("rpc:Func") in ["S1", "S2", "S3", "S7"] or (get_iob_value("rpc:Func") in ["S4", "S5", "S6"] and get_iob_value("pfc:UseRPC") == "ON"):	
		for iobName in y:
			if get_iob_value(iobName) != "ON":
				value_count += 1
				print CYELLOW  +  CBOLD + iobName + " is not ON " + CEND + "\n"
		if value_count == 0:
			print CGREENBG  +  CBOLD + "All REACTP_LR iob values are ON " + CEND + "\n" 		
	
	elif get_iob_value("rpc:Func") in ["S4", "S5", "S6"] and get_iob_value("pfc:UseRPC") == "ZR":	
		print "PF CONTROL VIA PF SETPOINT - CHECK COSPHI RLs!"
	elif get_iob_value("rpc:Func") == "S0":	
		for iobName in y:
			if get_iob_value(iobName) != "ZR":
				value_count += 1
				print CYELLOW  +  CBOLD + iobName + " is not OFF " + CEND + "\n"
		if value_count == 0:
			print CGREENBG  +  CBOLD + "All REACTP_LR iob values are OFF " + CEND + "\n" 

	for iobName in y:
		if len(get_iob_status(iobName)) != 0:
			status_count += 1
			print CYELLOW  +  CBOLD + iobName + " status is " + (' '.join(get_iob_status(iobName))) + CEND + "\n"
	if status_count == 0:
		print CGREENBG  +  CBOLD + "All REACTP_LR iob statuses are OK " + CEND + "\n" 	
		

	
	



########################################################################################################################################
#################################################           MAIN CODE        ###########################################################
########################################################################################################################################





CRED = '\33[91m'
CGREEN = '\33[4m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CBOLD = '\33[1m'
CEND = '\33[0m'
CGREENBG  = '\33[42m'
CREDBG    = '\33[41m'
CBLUEBG    = '\33[44m'
CYELLOWBG    = '\33[43m'
CURL = '\33[4m'


print "\n\n" + CRED + CBOLD + "Plant General Information: " + " " + CEND + "\n"
print "Rated power (ppc:Pmax): " + CBOLD + " " + str(get_iob_value("ppc:Pmax")) + " kW " + CEND + ""
print "Installed power (ppc:Pnom): " + CBOLD + " " + str(get_iob_value("ppc:Pnom")) + " kW " + CEND + ""
print "Rated voltage (ppc:Vnom): " + CBOLD + " " + str(get_iob_value("ppc:Vnom")) + " V " + CEND + ""
print "Rated frequency (ppc:Fnom): " + CBOLD + " " + str(get_iob_value("ppc:Fnom")) + " Hz " + CEND + ""
print "Number of inverters: " + CBOLD + " " + str(get_number_of_inverters()) + " " + CEND + ""
print "Number of loggers: " + CBOLD + " " + str(get_number_of_smartloggers()) + " " + CEND + "\n"

print "\n" + CRED + CBOLD + "Total plant measurements at the control point: " + " " + CEND + "\n"
print "Active power (ppc:P0): " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:P0")) + " kW " + CEND + "\n"
print "Reactive power (ppc:Q0): " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:Q0")) + " kVAr " + CEND + "\n"
print "Power factor (ppc:PF): " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:PF")) + " " + CEND + "\n"
print "Voltage (ppc:V0): " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:V0")) + " V " + CEND + "\n"
print "Frequency (ppc:F): " + CBLUEBG + CBOLD + " " + str(get_iob_value("ppc:F")) + " Hz " + CEND + "\n"

print "\n" + CRED + CBOLD + "PPC General Information: " + " " + CEND + "\n"
display_apc_PlantSt()
display_ppc_CSel()
display_ppc_OnOff()

print "\n" + CRED + CBOLD + "PPC Functions: " + CEND + "\n"

display_PPC_enabled_functions()

check_ACTP_LRs()
check_REACTP_LRs()

















































