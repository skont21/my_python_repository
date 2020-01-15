# %matplotlib notebook
from plot_maplot_v1 import *
import matplotlib as mpl
mpl.use('TkAgg')

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

csv=input("Please enter the path of you csv file:")
data = get_data_from_csv(csv)
(time,m,s,en)=get_traces(data)
print(CBOLD+"Traces Found:"+CEND+"\n")
print(CBOLD+"Measurements"+CEND)
print("------------")
for k in m.keys():
    print(k,"------>",m[k].name)
print(CBOLD+"Setpoints"+CEND)
print("------------")
plots=dict()
i=1
for k in s.keys():
    plots[str(i)]=k
    print(k,"------>",s[k].name)
    i=i+1
if ('P' in s.keys())&('Q' in s.keys()):
    plots[str(i)]='Q Capability'
    i=i+1
plots[str(i)]="All Measurements"
print(CBOLD+"Enable/Disable"+CEND)
print("-------------")
for k in en.keys():
    print(k,"------>",en[k].name)

print("\n"+"What plot would you like to generate?"+"\n\n"+CBOLD+"Available Choises"+CEND+"\n")
for k,v, in plots.items():
    print(k,")",v)
while True:
    choise = input(CBOLD+"Choose by Number:"+CEND)
    print("\n")
    try:
        choise=int(choise)
        if choise in range(1,len(plots)+1):
            break
        else:
            print("\n"+"Enter a valid nuber"+"\n")
    except:
        print("\n"+"Enter a valid nuber:"+"\n")

if plots[str(choise)]=="P":
    pdb=float(input("Enter the desired setpoint deadband(kW):"))
    plot_P(time,m['P'],s['P'],en['P'],pdb)
elif  plots[str(choise)]=="Q":
    qdb=float(input("Enter the desired setpoint deadband(kVAr):"))
    plot_Q(time,m['Q'],s['Q'],en['Q'],qdb)
elif  plots[str(choise)]=="AVR":
    avrdb=float(input("Enter the desired setpoint deadband(V):"))
    plot_AVR(time,m['V'],s['AVR'],m['Q'],en['AVR'],avrdb)
elif  plots[str(choise)]=="QV":
    qdb=float(input("Enter the desired setpoint deadband(kVAr):"))
    plot_QV(time,m['V'],s['QV'],m['Q'],s['Q'],en['QV'],qdb)
elif  plots[str(choise)]=="F":
    pdb=float(input("Enter the desired setpoint deadband(kW):"))
    plot_F_P(time,m['P'],s['P'],m['F'],s['F'],en['F'],pdb)
elif  plots[str(choise)]=="PF":
    pfdb=float(input("Enter the desired setpoint deadband:"))
    plot_PF(time,m['PF'],s['PF'],en['PF'],pfdb)
elif  plots[str(choise)]=="All Measurements":
    plot_meas(time,m['P'],m['Q'],m['V'],m['PF'],m['F'])
elif  plots[str(choise)]=="Q Capability":
    qdb=float(input("Enter the desired setpoint deadband(kVAr):"))
    plot_PQ(time,m['P'],m['Q'],s['Q'],en['Q'],qdb)
