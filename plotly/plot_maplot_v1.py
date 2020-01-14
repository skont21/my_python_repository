import pandas as pd
import numpy as np
import re
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter

Active =['ppc:P[^F]','.*pccm.*:ACTP_TOT',".*epm.*:ACTP_TOT",".*pccs.*:ACTP_TOT"]
Reactive =['ppc:Q.*','.*pccm.*:REACTP_TOT',".*epm.*:REACTP_TOT",".*pccs.*:REACTP_TOT"]
Voltage =['ppc:V','.*pccm.*:VABC_AVG',".*epm.*:VABC_AVG",".*pccs.*:VABC_AVG"]
Frequency=['ppc:F','.*pccm.*:F',".*epm.*:F",".*pccs.*:F"]
PowerFactor=['ppc:PF','.*pccm.*:PF',"epm.*:PF",".*pccs.*:PF"]
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

measurement1= (0,0,104/256)
measurement2= (62/256,150/256,81/256)
setpoint1= (234/256,0,0)
setpoint2 = (250/256,150/256,0)

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

    measurements=dict()
    if P:
        measurements["P"]=data[P[0]]
    if Q:
        measurements["Q"]=data[Q[0]]
    if V:
        measurements["V"]=data[V[0]]
    if F:
        measurements["F"]=data[F[0]]
    if PF:
        measurements["PF"]=data[PF[0]]


    PSP = [l for k in Active_Setpoint for l in data.columns if re.match(k,l)]
    QSP = [l for k in Reactive_Setpoint for l in data.columns if re.match(k,l)]
    QV_VSP = [l for k in QV_Setpoint for l in data.columns if re.match(k,l)]
    AVR_VSP = [l for k in AVR_Setpoint for l in data.columns if re.match(k,l)]
    FSP = [l for k in Frequency_Setpoint for l in data.columns if re.match(k,l)]
    PFSP = [l for k in PowerFactor_Setpoint for l in data.columns if re.match(k,l)]

    setpoints=dict()
    if PSP:
        setpoints["P"]=data[PSP[0]]
    if QSP:
        setpoints["Q"]=data[QSP[0]]
    if QV_VSP:
        setpoints["QV"]=data[QV_VSP[0]]
    if AVR_VSP:
        setpoints["AVR"]=data[AVR_VSP[0]]
    if FSP:
        setpoints["F"]=data[FSP[0]]
    if PFSP:
        setpoints["PF"]=data[PFSP[0]]


    PEn = [l for k in Active_En for l in data.columns if re.match(k,l)]
    QEn = [l for k in Reactive_En for l in data.columns if re.match(k,l)]
    QVEn = [l for k in QV_En for l in data.columns if re.match(k,l)]
    AVREn = [l for k in AVR_En for l in data.columns if re.match(k,l)]
    FEn = [l for k in Frequency_En for l in data.columns if re.match(k,l)]
    PFEn = [l for k in PowerFactor_En for l in data.columns if re.match(k,l)]

    enables=dict()
    if PEn:
        enables["P"]=data[PEn[0]]
    if QEn:
        enables["Q"]=data[QEn[0]]
    if QVEn:
        enables["QV"]=data[QVEn[0]]
    if AVREn:
        enables["AVR"]=data[AVREn[0]]
    if FEn:
        enables["F"]=data[FEn[0]]
    if PFEn:
        enables["PF"]=data[PFEn[0]]

    return (time,measurements,setpoints,enables)

def plot_P(TIME,P,PSP,PEN,PDB):

    #Setpoint only when control is enabled
    PSP_copy = PSP.copy()
    PSP_copy[PEN==0]=np.NaN

    #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1=ax.plot(TIME,P,label='P(kVAr)',color=measurement1,linewidth=1)
    #Plot Setpoints
    l2=ax.plot(TIME,PSP_copy,label='P Setpoint',color=setpoint1,linewidth=1)
    lb=ax.fill_between(TIME.values,PSP_copy-PDB,PSP_copy+PDB,alpha=0.7,facecolor=l2[0].get_color())

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

    # we will set up a dict mapping legend line to orig line, and enable
    # picking on the legend line
    lines = [l1[0],l2[0]]
    lined = dict()
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        if origline == l2[0]:
            vis_b = not lb.get_visible()
            lb.set_visible(vis_b)
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    return

def plot_Q(TIME,Q,QSP,QEN,QDB):

    #Setpoint only when control is enabled
    QSP_copy = QSP.copy()
    QSP_copy[QEN==0]=np.NaN

    #Creat Figure
    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1=ax.plot(TIME,Q,label='Q(kVAr)',linewidth=1)
    #Plot Setpoints
    l2=ax.plot(TIME,QSP_copy,label='Q Setpoint',linewidth=1)
    lb=ax.fill_between(TIME.values,QSP_copy-QDB,QSP_copy+QDB,alpha=0.3,facecolor=l2[0].get_color())

    #Formatting axis

    ax.set_ylim(min(Q.min(),QSP.min())*2,max(Q.max(),QSP.max())*2)
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

    # we will set up a dict mapping legend line to orig line, and enable
    # picking on the legend line
    lines = [l1[0],l2[0]]
    lined = dict()
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        if origline == l2[0]:
            vis_b = not lb.get_visible()
            lb.set_visible(vis_b)
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    return

def plot_PF(TIME,PF,PFSP,PFEN,PFDB):

    #Setpoint only when control is enabled
    PFSP_copy = PFSP.copy()
    PFSP_copy[PFEN==0]=np.NaN

    #Creat Figure
    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1=ax.plot(TIME,PF,label='Power Factor',linewidth=1)
    #Plot Setpoints
    l2=ax.plot(TIME,PFSP_copy,label='PF Setpoint',linewidth=1)
    lb=ax.fill_between(TIME.values,PFSP_copy-PFDB,PFSP_copy+PFDB,alpha=0.7,facecolor=l2[0].get_color())

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
    lines = [l1[0],l2[0]]
    lined = dict()
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        if origline == l2[0]:
            vis_b = not lb.get_visible()
            lb.set_visible(vis_b)
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    return

def plot_F_P(TIME,P,PSP,F,FSP,FEN,PDB):


#     #Setpoint only when control is enabled
    PSP_copy = PSP.copy()
#     PSP_copy[PEN==0]=np.NaN

#     #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))
    ax2=ax.twinx()
    #Plot Measurement
    l1=ax.plot(TIME,P,label='P(kVAr)',color=measurement1,linewidth=1)
    l2=ax2.plot(TIME,F,label='F(Hz)',color=measurement2,linewidth=1)
    #Plot Setpoints
    l3=ax.plot(TIME,PSP_copy,label='P Setpoint',color=setpoint1,linewidth=0.5)
    lb=ax.fill_between(TIME.values,PSP_copy-PDB,PSP_copy+PDB,alpha=0.7,facecolor=l3[0].get_color())
    l4=ax2.plot(TIME,FSP,label='F Setpoint',color=setpoint2,linewidth=2)
    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax.set_facecolor('whitesmoke')
    ax.grid(which='both',ls='--',lw=1,alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    ax.set_ylim(-0.1*(max(P.max(),PSP.max())),max(P.max(),PSP.max())*1.1)
    ax2.set_ylim(48,52)

    lns = l1+l2+l3+l4
    labs = [l.get_label() for l in lns]
    leg = ax.legend(lns,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lns),prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    ax.set_xlabel('TIME',fontdict=font)
    ax.set_ylabel('P (kW)',fontdict=font)
    ax2.set_ylabel('F (Hz)',fontdict=font)
    ax.tick_params(labelsize=10)
    ax.set_title('Active Power Control',fontdict=font,x=0.5,y=1.1)

    # we will set up a dict mapping legend line to orig line, and enable
    # picking on the legend line
    lines = [l1[0],l2[0],l3[0],l4[0]]
    lined = dict()
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        if origline == l3[0]:
            vis_b = not lb.get_visible()
            lb.set_visible(vis_b)
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    return

def plot_AVR(TIME,V,AVRSP,Q,AVREN,AVRDB):

#     #Setpoint only when control is enabled
    AVRSP_copy = AVRSP.copy()
    AVRSP_copy[AVREN==0]=np.NaN

#     #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))
    ax2=ax.twinx()
    #Plot Measurement
    l1=ax.plot(TIME,V,label='V(V)',color=measurement1,linewidth=0.5)
    l2=ax2.plot(TIME,Q,label='Q(kVAr)',color=measurement2,linewidth=2)
    #Plot Setpoints
    l3=ax.plot(TIME,AVRSP_copy,label='AVR Setpoint',color=setpoint1,linewidth=0.5)
    lb=ax.fill_between(TIME.values,AVRSP_copy-AVRDB,AVRSP_copy+AVRDB,alpha=0.7,facecolor=l3[0].get_color())
#     l4=ax2.plot(TIME,FSP,label='F Setpoint',color=setpoint2,linewidth=2)
    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax.set_facecolor('whitesmoke')
    ax.grid(which='both',ls='--',lw=1,alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    ax.set_ylim((min(V.max(),AVRSP.min()))-1000,max(V.max(),AVRSP.max())+1000)
    ax2.set_ylim(Q.min()*2,Q.max()*2)

    lns = l1+l2+l3
    labs = [l.get_label() for l in lns]
    leg = ax.legend(lns,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lns),prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    ax.set_xlabel('TIME',fontdict=font)
    ax.set_ylabel('Voltage (V)',fontdict=font)
    ax2.set_ylabel('Q (kVAr)',fontdict=font)
    ax.tick_params(labelsize=10)
    ax.set_title('AVR Control',fontdict=font,x=0.5,y=1.1)

    # we will set up a dict mapping legend line to orig line, and enable
    # picking on the legend line
    lines = [l1[0],l2[0],l3[0]]
    lined = dict()
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = lined[legline]
        vis = not origline.get_visible()
        if origline == l3[0]:
            vis_b = not lb.get_visible()
            lb.set_visible(vis_b)
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()

    return
