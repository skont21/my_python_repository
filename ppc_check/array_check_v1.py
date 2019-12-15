import os
from subprocess import Popen, PIPE
import re

def padding(text_list):
    col_width = max(len(word) for row in text_list for word in row)
    for row in text_list:
        print "".join(word.center(col_width) for word in row)

def iobtap(com):
    return Popen(com.split(),stdout=PIPE).communicate()[0].decode('utf-8').splitlines()


CRED = '\33[91m'
CGREEN = '\33[4m'
CBOLD = '\33[1m'
CEND = '\33[0m'
CGREENBG  = '\33[42m'
CREDBG    = '\33[41m'

ACTIVE = ["ACTP_SPPS","_ACTP_SPS_G","_ACTP_SPPS","_ACTP_SPP","_ACTP_SP","ACTP_SP","_PAC","PAC_P","PAC"]

print("----------------------------------------------------------------------------------------------------------------------\n")

#PVARRAY - SPPC

cmd = "iobtap -n ^pvarray.*:pac_p$"
arr = iobtap(cmd)
cmd = "iobtap -n ^sppc.*:pac_p$"
sppc = iobtap(cmd)

npv = len(arr)-1
if len(arr)>1:
    print CRED + CBOLD +"Number of pvarrays: " + str(npv) + CEND + " " + "\n"

nsppc = len(sppc)-1
if len(sppc)>1:
    print CRED + CBOLD +"Number of loggers: "+ str(nsppc) + CEND + " " + "\n"

#-------------------------------------------------------------------------------------------------------------------------------------
#ACTP_LR

if len(sppc)>1:
    cmd = "iobtap -n ^sppc.*:actp_lr"
elif len(arr)>1:
    cmd = "iobtap -n ^pvarray.*:actp_lr"
else:
    print CRED + CBOLD +"NO LOGGERS OR PVARRAYS IN THIS CONTROLLER" + CEND + " " + "\n"
    raise SystemExit

actp_lr = iobtap(cmd)

print CRED + CBOLD +"Active Power Release:"+ CEND + " " + "\n"

text=[]
if actp_lr[1].split()[2][0] == "@":

    text.append(["COMMAND","   STATUS"])

    for i in range(1,len(actp_lr)):

        words_c = actp_lr[i].split()
        c1 = words_c[2]
        c2 = words_c[6]
        if words_c[5] == '------' :
            c3 = 'OK'
        elif "M" in words_c[5] :
            c3 = 'MALF'
        elif "C" in words_c[5] :
            c3 = 'COMER'
        elif "B" in words_c[5] :
            c3 = 'BUSY'
        elif "B" in words_c[5] :
            c3 = 'STOPPED'
        else :  c3 = ' '

        text.append([c1,c2,c3])
else:

    text.append(["COMMAND","VALUE","STATUS","FEEDBACK","VALUE","STATUS"])

    for i in range(1,((len(actp_lr)-1)/2)+1):

        words_c = actp_lr[2*i-1].split()
        c1 = words_c[2]
        if words_c[4] == '------' :
            c3 = 'OK'
        elif "M" in words_c[4] :
            c3 = 'MALF'
        elif "C" in words_c[4] :
            c3 = 'COMER'
        elif "B" in words_c[4] :
            c3 = 'BUSY'
        elif "B" in words_c[4] :
            c3 = 'STOPPED'
        else :  c3 = ' '

        words_f = actp_lr[2*i].split()
        f1= words_f[2]
        if words_f[4] == '------' :
            f3 = 'OK'
        elif "M" in words_f[4] :
            f3 = 'MALF'
        elif "C" in words_f[4] :
            f3 = 'COMER'
        elif "B" in words_f[4] :
            f3 = 'BUSY'
        elif "B" in words_f[4] :
            f3 = 'STOPPED'
        else :  f3 = ' '

        c2=  words_c[6]
        f2=  words_f[6]

        text.append([c1,c2,c3,f1,f2,f3])

padding(text)
print("\n")

#-------------------------------------------------------------------------------------------------------------------------------------

#REACTP_LR

if len(sppc)>1:
    cmd = "iobtap -n ^sppc.*:reactp_lr"
else : cmd = "iobtap -n ^pvarray.*:reactp_lr"

reactp_lr = iobtap(cmd)

print CRED + CBOLD +"Reactive Power Release:"+ CEND + " " + "\n"

text=[]
if reactp_lr[1].split()[2][0] == "@":

    text.append(["COMMAND","   STATUS"])

    for i in range(1,len(actp_lr)):

        words_c = reactp_lr[i].split()
        c1 = words_c[2]
        c2 = words_c[6]
        if words_c[5] == '------' :
            c3 = 'OK'
        elif "M" in words_c[5] :
            c3 = 'MALF'
        elif "C" in words_c[5] :
            c3 = 'COMER'
        elif "B" in words_c[5] :
            c3 = 'BUSY'
        elif "B" in words_c[5] :
            c3 = 'STOPPED'
        else :  c3 = ' '


        text.append([c1,c2,c3])
else:

    text.append(["COMMAND","VALUE","STATUS","FEEDBACK","VALUE","STATUS"])
    for i in range(1,((len(reactp_lr)-1)/2)+1):

            words_c = reactp_lr[2*i-1].split()
            c1 = words_c[2]
            if words_c[4] == '------' :
                c3 = 'OK'
            elif "M" in words_c[4] :
                c3 = 'MALF'
            elif "C" in words_c[4] :
                c3 = 'COMER'
            elif "B" in words_c[4] :
                c3 = 'BUSY'
            elif "B" in words_c[4] :
                c3 = 'STOPPED'
            else :  c3 = ' '

            words_f = reactp_lr[2*i].split()
            f1= words_f[2]
            if words_f[4] == '------' :
                f3 = 'OK'
            elif "M" in words_f[4] :
                f3 = 'MALF'
            elif "C" in words_f[4] :
                f3 = 'COMER'
            elif "B" in words_f[4] :
                f3 = 'BUSY'
            elif "B" in words_f[4] :
                f3 = 'STOPPED'
            else :  f3 = ' '


            c2=  words_c[6]
            f2=  words_f[6]
            text.append([c1,c2,c3,f1,f2,f3])

padding(text)
print("\n")

#-------------------------------------------------------------------------------------------------------------------------------------

#Setpoints

if len(sppc)>1:
    cmd = "iobtap -n ^sppc.*:_*actp_sp|^sppc.*:.*pac"
    ngen = nsppc
    gen = "sppc"
else :
    cmd = "iobtap -n ^pvarray.*:_*actp_sp|^pvarray.*:.*pac"
    ngen = npv
    gen = "pvarray"

actpsp = iobtap(cmd)


print CRED + CBOLD +"Active Power:"+ CEND + "\n"
for i in range(1,ngen+1):
    text=[]
    print CRED + CBOLD +gen+"0"*(3-len(str(i)))+str(i)+ ":"+ CEND + "\n"
    r = re.compile(".*"+gen+"0"*(3-len(str(i)))+str(i)+".*")
    for l in filter(r.match,actpsp):
        if len(l.split()) == 9 :
            text.append([l.split()[2],l.split()[7]+" "+l.split()[8]])
        elif len(l.split()) == 8:
            text.append([l.split()[2],l.split()[6]+" "+l.split()[7]])
        else:
            text.append([l.split()[2],l.split()[6]])
    padding(text)
    print("\n")

print("----------------------------------------------------------------------------------------------------------------------\n")
