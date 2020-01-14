import pandas as pd
import numpy as np
import re
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter

Active =['ppc:P[^F]','pccm.*:ACTP_TOT',"epm.*:ACTP_TOT","pccs.*:ACTP_TOT"]
Reactive =['ppc:Q.*','pccm.*:REACTP_TOT',"epm.*:REACTP_TOT","pccs.*:REACTP_TOT"]
Voltage =['ppc:V','pccm.*:VABC_AVG',"epm.*:VABC_AVG","pccs.*:VABC_AVG"]
Frequency=['ppc:F','pccm.*:F',"epm.*:F","pccs.*:F"]
PowerFactor=['ppc:PF','pccm.*:PF',"epm.*:PF","pccs.*:PF"]
Active_Setpoint = ['apc:PSP']
Reactive_Setpoint = ['rpc:QSP']
QV_Setpoint = ['rpc:VSP']
AVR_Setpoint = ['avr:VSP']
Frequency_Setpoint = ['apc:FSP']
PowerFactor_Setpoint = ['pfc:PFSP']
Active_En = ['apc:En']
Reactive_En = ['rpc:En']
QV_En = ['rpc:VCEn']
AVR_En = ['avr:En']
Frequency_En = ['apc:FCEn']
PowerFactor_En = ['pfc:En']

font = {'family': 'serif',
    'color':  'black',
    'weight': 'bold',
    'size': 14,
    }

legend_font = {'weight': 'bold',
              'size':10}

ticks_font = {'fontsize':8,
             'fontweight':'bold'}

def get_data_from_csv(data_csv):
    try:
        data=pd.read_csv(data_csv,delimiter=" ")
        if data.columns[0]!='TIME':
            data=pd.read_csv(data_csv,delimiter=",")
        if data.columns[0]!='TIME':
            data=pd.read_csv(data_csv,delimiter=";")
        if "." in data['TIME'][0]:
            data['TIME']= data['TIME'].str.split(".",n=1,expand=True)[0]
        data.replace("---",np.NaN,inplace=True)
        for col in data.select_dtypes('object').columns:
            try:
                data[col]=data[col].astype(float)
            except ValueError:
                continue
        data = data.round(3)
        data['TIME']=data['TIME'].apply(lambda x : datetime.datetime.strptime(x, '%H:%M:%S'))
        return data
    except FileNotFoundError as e:
        print(e)
        return e

def get_traces(data):

    time =data['TIME']

    P = [l for k in Active for l in data.columns if re.match(k,l)]
    Q = [l for k in Reactive for l in data.columns if re.match(k,l)]
    V = [l for k in Voltage for l in data.columns if re.match(k,l)]
    F = [l for k in Frequency for l in data.columns if re.match(k,l)]
    PF = [l for k in PowerFactor for l in data.columns if re.match(k,l)]

    measurements={"P":data[P[0]],"Q":data[Q[0]],"V":data[V[0]],"F":data[F[0]],"PF":data[PF[0]]}

    PSP = [l for k in Active_Setpoint for l in data.columns if re.match(k,l)]
    QSP = [l for k in Reactive_Setpoint for l in data.columns if re.match(k,l)]
    QV_VSP = [l for k in QV_Setpoint for l in data.columns if re.match(k,l)]
    AVR_VSP = [l for k in AVR_Setpoint for l in data.columns if re.match(k,l)]
    FSP = [l for k in Frequency_Setpoint for l in data.columns if re.match(k,l)]
    PFSP = [l for k in PowerFactor_Setpoint for l in data.columns if re.match(k,l)]

    setpoints={"P":data[PSP[0]],"Q":data[QSP[0]],"QV":data[QV_VSP[0]],"AVR":data[AVR_VSP[0]],"F":data[FSP[0]],"PF":data[PFSP[0]]}

    PEn = [l for k in Active_En for l in data.columns if re.match(k,l)]
    QEn = [l for k in Reactive_En for l in data.columns if re.match(k,l)]
    QVEn = [l for k in QV_En for l in data.columns if re.match(k,l)]
    AVREn = [l for k in AVR_En for l in data.columns if re.match(k,l)]
    FEn = [l for k in Frequency_En for l in data.columns if re.match(k,l)]
    PFEn = [l for k in PowerFactor_En for l in data.columns if re.match(k,l)]

    enables= {"P":data[PEn[0]],"Q":data[QEn[0]],"QV":data[QVEn[0]],"AVR":data[AVREn[0]],"F":data[FEn[0]],"PF":data[PFEn[0]]}
    return (time,measurements,setpoints,enables)

def plot_P(TIME,P,PSP,PEN,PDB):

    #Setpoint only when control is enabled
    PSP_copy = PSP.copy()
    PSP_copy[PEN==0]=np.NaN

    #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1,=ax.plot(TIME,P,label='P(kVAr)',linewidth=1)
    #Plot Setpoints
    l2,=ax.plot(TIME,PSP_copy,label='P Setpoint',linewidth=1)
    ax.fill_between(TIME.values,PSP_copy-PDB,PSP_copy+PDB,alpha=0.7,facecolor=l2.get_color())

    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('whitesmoke')
    ax.grid(which='both',ls='--',lw=1,alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    ax.set_ylim(-0.1*(max(P.max(),PSP.max())),max(P.max(),PSP.max())*1.1)
    leg = ax.legend(bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=2,prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()
    ax.set_ylabel('P (kW)',fontdict=font)
    ax.set_xlabel('TIME',fontdict=font)
    ax.tick_params(labelsize=10)
    ax.set_title('Active Power Control',fontdict=font,x=0.5,y=1.1)

    plt.show()
    return

def plot_Q(TIME,Q,QSP,QEN,QDB):

    #Setpoint only when control is enabled
    QSP_copy = QSP.copy()
    QSP_copy[QEN==0]=np.NaN

    #Creat Figure
    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1,=ax.plot(TIME,Q,label='Q(kVAr)',linewidth=1)
    #Plot Setpoints
    l2,=ax.plot(TIME,QSP_copy,label='Q Setpoint',linewidth=1)
    ax.fill_between(TIME.values,QSP_copy-QDB,QSP_copy+QDB,alpha=0.7,facecolor=l2.get_color())

    #Formatting axis

    ax.set_ylim(min(Q.min(),QSP.min())*1.1,max(Q.max(),QSP.max())*1.1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('whitesmoke')
    ax.grid(which='both',ls='--',lw=1,alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(labelsize=10)
    ax.set_ylabel('Q (kVAr)',fontdict=font)
    ax.set_xlabel('TIME',fontdict=font)
    ax.set_title('Reactive Power Control',fontdict=font,x=0.5,y=1.1)
    leg = ax.legend(bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=2,prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    plt.show()
    return

def plot_PF(TIME,PF,PFSP,PFEN,PFDB):

    #Setpoint only when control is enabled
    PFSP_copy = PFSP.copy()
    PFSP_copy[PFEN==0]=np.NaN

    #Creat Figure
    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1,=ax.plot(TIME,PF,label='Power Factor',linewidth=1)
    #Plot Setpoints
    l2,=ax.plot(TIME,PFSP_copy,label='PF Setpoint',linewidth=1)
    ax.fill_between(TIME.values,PFSP_copy-PFDB,PFSP_copy+PFDB,alpha=0.7,facecolor=l2.get_color())

    #Formatting axis

    ax.set_ylim(min(PF.min(),PFSP.min())*1.1,max(PF.max(),PFSP.max())*1.1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('whitesmoke')
    ax.grid(which='both',ls='--',lw=1,alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(labelsize=10)
    ax.set_ylabel('PF',fontdict=font)
    ax.set_xlabel('TIME',fontdict=font)
    ax.set_title('Power Factor Control',fontdict=font,x=0.5,y=1.1)
    leg = ax.legend(bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=2,prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    plt.show()
    return
