import os
from subprocess import Popen, PIPE
import re


def padding(text_list):
    col_width = max(len(word) for row in text_list for word in row)
    for row in text_list:
        print "".join(word.center(col_width) for word in row)

def iobtap(com):
    return Popen(com.split(),stdout=PIPE).communicate()[0].decode('utf-8').splitlines()

def iobaccess_read(com):
    p1 = Popen(com.split(),stdout=PIPE).communicate()[0].decode('utf-8').splitlines()
    return p1[0].split()[2]

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


CRED = '\33[91m'
CGREEN = '\33[4m'
CBOLD = '\33[1m'
CEND = '\33[0m'
CGREENBG  = '\33[42m'
CREDBG    = '\33[41m'
fr=1
freq_val = ["apc:FODroop",	"apc:FOMode",	"apc:FOSlope",	"apc:FReset_S",	"apc:FSrc",	"apc:FUBase_S",	"apc:FUDroop",	"apc:FUMax_S",	"apc:FUMode",	"apc:FUReset_S",	"apc:FUSlope",	"apc:FZero_S","apc:FBase_S"]
En_C = ["apc:En","apc:FCEn","apc:FOEn","apc:FUEn","apc:RateEn","rpc:En","rpc:VCEn","pfc:En","avr:En","apc:REn"]
flags = ["FORCE","DRF","LOVE","BUSY","MALF","COMER","STOPPED"]

print("\n")

#PVARRAY

cmd = "iobtap -n pvarray"
arr = os.popen(cmd).read()
y = re.findall("pvarray([0-9]*)", arr)
lst = []
for num in y:
        num = int(num)
        if num not in lst:
            lst.append(num)
npv = len(lst)
print CRED + CBOLD +"Number of pvarrays: "+ str(npv) + CEND + " " + "\n"


#SPPC

cmd = "iobtap -n sppc"
x = os.popen(cmd).read()
y = re.findall("sppc([0-9]*)", x)
lst = []
for num in y:
        num = int(num)
        if num not in lst:
            lst.append(num)
nsppc =len(lst)

print CRED + CBOLD +"Number of loggers: "+ str(nsppc) + CEND + " " + "\n"


# MEASUREMENTS

cmd = "iobtap -n ppc:[^o].*0$|ppc:.*F$"
meas = iobtap(cmd)

print CRED + CBOLD +"Measurements:"+ CEND + " "
text=[]
for i in range(1,len(meas)):
    words = meas[i].split()
    if len(words)==8:
        text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
    else:
        text.append([words[2]," =",words[len(words)-1]])
padding(text)
print("\n")

# NOMINAL

cmd = "iobtap -n ppc:.*nom|ppc:.*max"
nom = iobtap(cmd)

print CRED + CBOLD +"Nominal and Maximum Values:"+ CEND + " "
text=[]
for i in range(1,len(nom)):
    words = nom[i].split()
    if len(words)==8:
        text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
    else:
        text.append([words[2]," =",words[len(words)-1]])
padding(text)
print("\n")

#APC MODE

cmd = "iobaccess read apc:Mode val"
apc_mode = iobaccess_read(cmd)

if apc_mode=="S0":
    print CREDBG +  CBOLD + "APC IN OPEN-LOOP" + CEND  + " "
elif apc_mode=="S1":
    print CGREENBG +   CBOLD + "APC IN CLOSED-LOOP" +CEND   + " "
else:
    print CREDBG  +  CBOLD + "APC IN UKNOWN MODE" +CEND   + " "

#RPC MODE

cmd = "iobaccess read rpc:Mode val"
rpc_mode = iobaccess_read(cmd)

if rpc_mode=="S0":
    print CREDBG  +  CBOLD + "RPC IN OPEN-LOOP" + CEND    + " "
elif rpc_mode=="S1":
    print CGREENBG  +  CBOLD + "RPC IN CLOSED-LOOP"  + CEND + " "
else:
    print CREDBG  +  CBOLD + "RPC IN UKNOWN MODE"  +CEND + " "


#PFC MODE

cmd = "iobaccess read pfc:Mode val"
pfc_mode = iobaccess_read(cmd)

if pfc_mode=="S0":
    print CREDBG  +  CBOLD + "PFC IN OPEN-LOOP" + CEND    + " "
elif pfc_mode=="S1":
    print CGREENBG  +  CBOLD + "PFC IN CLOSED-LOOP"  + CEND + " "
else:
    print CREDBG + CBLACK  + CBOLD + "PFC IN UKNOWN MODE"  +CEND + " "

#RAMP MODE

cmd = "iobtap -n apc:Ramp_Mode"
ramp_mode = iobtap(cmd)
if len(ramp_mode) > 1 :
    words=ramp_mode[1].split()
    print CGREENBG  +  CBOLD + "Ramp Mode is:" + words[6] + words[7]  + CEND + " "
else :
    print CGREENBG  +  CBOLD  + "No ramp mode " + CEND +  " "

print("\n")

#LOCAL SETPOINTS

cmd = "iobtap -n sp0_s|:rate.*wn0_s|:rate.*p0_s|rpc:vd.*0_"
sets = iobtap(cmd)

print CRED + CBOLD +"Local Setpoints:"+ CEND + " "
text=[]
for i in range(1,len(sets)):
    words = sets[i].split()
    if len(words)==8:
        text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
    else:
        text.append([words[2]," =",words[len(words)-1]])
padding(text)
print("\n")


#REMOTE SETPOINTS

cmd = "iobtap -n sp1_s|:rate.*wn1_s|:rate.*p1_s|rpc:vd.*1_"
sets = iobtap(cmd)

print CRED + CBOLD +"Remote Setpoints:"+ CEND + " "
text=[]
for i in range(1,len(sets)):
    words = sets[i].split()
    if len(words)==8:
        text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
    else:
        text.append([words[2]," =",words[len(words)-1]])
padding(text)
print("\n")

#CONTROL ENABLED/DISABLED

cmd = "iobtap -n :.*en$"
en = iobtap(cmd)

print CRED + CBOLD +"Enabed/Disabled:"+ CEND + " "
text=[]
for i in range(1,len(en)):
    words = en[i].split()
    if words[2] in En_C:
        text.append([words[2]," is",words[len(words)-1]])
padding(text)
print("\n")

#PID PERIODS

cmd = "iobtap -n period$"
per = iobtap(cmd)

print CRED + CBOLD +"Periods:"+ CEND + " "
text=[]
for i in range(1,len(per)):
    words = per[i].split()
    text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
padding(text)
print("\n")

cmd = "iobtap -n db"
dbs = iobtap(cmd)

#CONTROL DEADBANDS

print CRED + CBOLD +"Control Deadbands:"+ CEND + " "
text=[]
for i in range(1,len(dbs)):
    words = dbs[i].split()
    if len(words)==8:
        text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
    else:
        text.append([words[2]," =",words[len(words)-1]])
padding(text)
print("\n")

#LOCAL/REMOTE

cmd = "iobtap -n ppc:csel$|apc:cs|rpc:cs"
cs = iobtap(cmd)

print CRED + CBOLD +"Local/Remote:"+ CEND + " "
text=[]
for i in range(1,len(cs)):
    words = cs[i].split()
    if words[2] ==  "apc:CSelOvr_S":
        text.append(["APC in :",words[len(words)-1]+" Mode"])
        # print "Active power Control in :" + "\t" +  words[len(words)-2] +  words[len(words)-1] + " Mode" + " "
    elif  words[2] ==  "rpc:CSelOvr_S":
        text.append(["RPC in :",words[len(words)-1]+" Mode"])
        # print "Reactive power Control in :" + "\t" +  words[len(words)-2] +  words[len(words)-1] + " Mode" + " "
    elif words[2] ==  "ppc:CSel":
        text.append(["PPC in :",words[len(words)-1]+" Mode"])
        # print "PPC in :" + "\t" + words[len(words)-2] +  words[len(words)-1] + " Mode" + " "
padding(text)
print("\n")

#PLANT STATE

cmd = "iobtap -n PlantSt$"
pl = iobtap(cmd)

if len(pl)>1:
    print CRED + CBOLD +"Plant State:"+ CEND + " "
    print "The plant is:    " + pl[1].split()[7] + " "

    print("\n")

#GCLIM

cmd = "iobtap -n gclim"
gc = iobtap(cmd)

print CRED + CBOLD +"GCLim Pramaters:"+ CEND + " "
text  =[]
for i in range(1,len(gc)):
    words = gc[i].split()
    if len(words)==8:
        text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
    else:
        text.append([words[2]," =",words[len(words)-1]])
padding(text)
print("\n")

#FREQUENCY CONTROL PARAMETERS

cmd = "iobtap -n apc:f"
fr_iobs = iobtap(cmd)

text=[]
if len(fr_iobs) > 1 :
    for i in range(1,len(fr_iobs)):
        words = fr_iobs[i].split()
        if words[2] in freq_val:
            text.append([words[2]," =",words[len(words)-2]+" "+words[len(words)-1]])
    if len(text) > 0 :
        print CRED + CBOLD +"Frequency Control Configuration:"+ CEND + " "
        padding(text)
        print("\n")

#ACTP_LR

cmd = "iobtap -n :actp_lr"
actp_lr = iobtap(cmd)

if len(actp_lr)>1:
    print CRED + CBOLD +"Active Power Release:"+ CEND + " " + "\n"

    text=[]
    if actp_lr[1].split()[2][0] == "@":

        text.append(["COMMAND","VALUE","STATUS"])

        for i in range(1,len(actp_lr)):

            words_c = actp_lr[i].split()
            c1 = words_c[2]
            c2 = words_c[6]
            c3 = " ".join(get_iob_status(c1))
            
            text.append([c1,c2,c3])
    else:

        text.append(["COMMAND","VALUE","STATUS","FEEDBACK","VALUE","STATUS"])

        for i in range(1,((len(actp_lr)-1)/2)+1):

            words_c = actp_lr[2*i-1].split()
            c1 = words_c[2]
            c3 = get_iob_status(c1)
            if not c3 or (len(c3)==1 and c3[0]=="rsv"):
                c3 ="OK"
            else:
                c3= " ".join(c3)

            words_f = actp_lr[2*i].split()
            f1= words_f[2]
            f3 = " ".join(get_iob_status(f1))

            c2=  words_c[6]
            f2=  words_f[6]

            text.append([c1,c2,c3,f1,f2,f3])

    padding(text)
    print("\n")

#REACTP_LR

cmd = "iobtap -n :reactp_lr"
reactp_lr = iobtap(cmd)

if len(reactp_lr)>1:

    print CRED + CBOLD +"Reactive Power Release:"+ CEND + " " + "\n"

    text=[]
    if reactp_lr[1].split()[2][0] == "@":

        text.append(["COMMAND","VALUE","STATUS"])

        for i in range(1,len(actp_lr)):

            words_c = reactp_lr[i].split()
            c1 = words_c[2]
            c3 = " ".join(get_iob_status(c1))
            
            text.append([c1,c2,c3])
    else:

        text.append(["COMMAND","VALUE","STATUS","FEEDBACK","VALUE","STATUS"])
        for i in range(1,((len(reactp_lr)-1)/2)+1):

                words_c = reactp_lr[2*i-1].split()
                c1 = words_c[2]
                c3 = " ".join(get_iob_status(c1))
               

                words_f = reactp_lr[2*i].split()
                f1= words_f[2]

                f3 = " ".join(get_iob_status(f1))
            
                c2=  words_c[6]
                f2=  words_f[6]

                text.append([c1,c2,c3,f1,f2,f3])

    padding(text)
