import pandas as pd
import numpy as np
import re
import datetime
from colorutils import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter,LinearLocator,MaxNLocator,MultipleLocator


import matplotlib as mpl
mpl.use('TkAgg')

Active =['ppc:P[^F]','.*pccm.*:ACTP_TOT',".*epm.*:ACTP_TOT",".*pccs.*:ACTP_TOT"]
Reactive =['ppc:Q.*','.*pccm.*:REACTP_TOT',".*epm.*:REACTP_TOT",".*pccs.*:REACTP_TOT"]
Voltage =['ppc:V','.*pccm.*:VABC_AVG',".*epm.*:VABC_AVG",".*pccs.*:VABC_AVG"]
Frequency=['ppc:F','.*pccm.*:FREQ',".*epm.*:FREQ",".*pccs.*:FREQ"]
PowerFactor=['ppc:PF','.*pccm.*:PF',"epm.*:PF",".*pccs.*:PF"]
Expected=['.*Pexp']
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
Expected_En=['apc:REn']

measurement1= (228/256,26/256,28/256)
measurement2= (55/256,126/256,184/256)
measurement3= (77/256,175/256,74/256)
measurement4= (255/256,127/256,0)
measurement5= (152/256,78/256,163/256)
measurements=[measurement1,measurement2,measurement3,measurement4,measurement5]
setpoint1= (1/256,102/256,94/256)
setpoint2 = (254/256,59/256,211/256)

font = {'family': 'serif',
    'color':  'black',
    'weight': 'bold',
    'size': 14,
    }

legend_font = {'weight': 'bold',
              'size':10}

ticks_font = {'fontsize':8,
             'fontweight':'bold'}

ylabels_dict={'P':'P (kW)','Q':'Q (kVAr)','V':'Volatge (V)','PF':'PF','F':'F (Hz)'}

def get_data_from_csv(data_csv):
    try:
        data=pd.read_csv(data_csv,delimiter=" ")
        if data.columns[0]!='TIME':
            data=pd.read_csv(data_csv,delimiter=",")
        # if data.columns[0]!='TIME':
        #     data=pd.read_csv(data_csv,delimiter=";")
        if data.columns[0]=='TIME':
            if "." in data['TIME'][0]:
                data['TIME']= data['TIME'].str.split(".",n=1,expand=True)[0]
            data['TIME']=data['TIME'].apply(lambda x : datetime.datetime.strptime(x, '%H:%M:%S'))
        data.replace("---",np.NaN,inplace=True)
        for col in data.select_dtypes('object').columns:
            try:
                data[col]=data[col].astype(float)
            except ValueError:
                continue
        data = data.round(3)
        return data
    except FileNotFoundError as e:
        print(e)
        return e

def get_traces(data):

    try:
        time =data['TIME']
        if pd.Timestamp(1900,1,1,0,0,0) in time.to_list():
            new_day = time.index[time == pd.Timestamp(1900,1,1,0,0,0)].tolist()
            time_new = time.copy()
            time_new[time_new.index>=new_day[0]]=time[time.index>=new_day[0]]+datetime.timedelta(days=1)
            time=time_new
    except:
        time = pd.Series()

    P = [l for k in Active for l in data.columns if re.match(k,l)]
    Q = [l for k in Reactive for l in data.columns if re.match(k,l)]
    V = [l for k in Voltage for l in data.columns if re.match(k,l)]
    F = [l for k in Frequency for l in data.columns if re.match(k,l)]
    PF = [l for k in PowerFactor for l in data.columns if re.match(k,l)]
    Pexp = [l for k in Expected for l in data.columns if re.match(k,l)]

    measurements=dict()
    if P:
        measurements["P"]=data[P]
    if Q:
        measurements["Q"]=data[Q]
    if V:
        measurements["V"]=data[V]
    if F:
        measurements["F"]=data[F]
    if PF:
        measurements["PF"]=data[PF]
    if Pexp:
        measurements["Pexp"]=data[Pexp]


    PSP = [l for k in Active_Setpoint for l in data.columns if re.match(k,l)]
    QSP = [l for k in Reactive_Setpoint for l in data.columns if re.match(k,l)]
    QV_VSP = [l for k in QV_Setpoint for l in data.columns if re.match(k,l)]
    AVR_VSP = [l for k in AVR_Setpoint for l in data.columns if re.match(k,l)]
    FSP = [l for k in Frequency_Setpoint for l in data.columns if re.match(k,l)]
    PFSP = [l for k in PowerFactor_Setpoint for l in data.columns if re.match(k,l)]

    setpoints=dict()
    if PSP:
        setpoints["P"]=data[PSP]
    if QSP:
        setpoints["Q"]=data[QSP]
    if QV_VSP:
        setpoints["QV"]=data[QV_VSP]
    if AVR_VSP:
        setpoints["AVR"]=data[AVR_VSP]
    if FSP:
        setpoints["F"]=data[FSP]
    if PFSP:
        setpoints["PF"]=data[PFSP]


    PEn = [l for k in Active_En for l in data.columns if re.match(k,l)]
    QEn = [l for k in Reactive_En for l in data.columns if re.match(k,l)]
    QVEn = [l for k in QV_En for l in data.columns if re.match(k,l)]
    AVREn = [l for k in AVR_En for l in data.columns if re.match(k,l)]
    FEn = [l for k in Frequency_En for l in data.columns if re.match(k,l)]
    PFEn = [l for k in PowerFactor_En for l in data.columns if re.match(k,l)]
    REn = [l for k in Expected_En for l in data.columns if re.match(k,l)]

    enables=dict()
    if PEn:
        enables["P"]=data[PEn]
    if QEn:
        enables["Q"]=data[QEn]
    if QVEn:
        enables["QV"]=data[QVEn]
    if AVREn:
        enables["AVR"]=data[AVREn]
    if FEn:
        enables["F"]=data[FEn]
    if PFEn:
        enables["PF"]=data[PFEn]
    if REn:
        enables["Pexp"]=data[REn]

    return (time,measurements,setpoints,enables)

def calc_minmax(*args):
    a = min(c.min() for c in args)
    b = max(d.max() for d in args)
    m = a-(b-a)/10
    M = b+(b-a)/10
    return(m,M)

def plot_existing(figure,texts,verticals,horizontals,arrows):
    import random
    import string

    def randstring(n):
      alphabet = string.ascii_letters[0:6] + string.digits
      hexc = ''.join(random.choice(alphabet) for i in range(n))
      return '#'+hexc

    fig, ax = plt.subplots(figsize=(10,5))
    x = figure.axes[0].lines[0].get_data()[0]
    if isinstance(x[0],np.datetime64):
        x = [str(el).split("T")[1].split(".")[0] for el in x]
        time = pd.Series(x)
        time= time.apply(lambda y : datetime.datetime.strptime(str(y), '%H:%M:%S'))
        x=pd.Series(time)

    num_a=0
    lines=[]
    i=1
    j=1
    if len(figure.axes)>1:
        ax2=ax.twinx()
        ax2.set_facecolor(figure.axes[1].get_facecolor())

    for a in figure.axes:
        for l in a.lines:
            y = l.get_data()[1]
            if num_a==0:
                if len(x)==len(y):
                    line,=ax.plot(x,y)
                    line.set_color(figure.axes[num_a].lines[i-1].get_color())
                    line.set_label(figure.axes[num_a].lines[i-1].get_label())
                    lines.append(line)
                    i+=1
            else:
                line,=ax2.plot(x,y)
                line.set_color(figure.axes[num_a].lines[j-1].get_color())
                line.set_label(figure.axes[num_a].lines[j-1].get_label())
                lines.append(line)
                j+=1
            l.set_picker(5)
            l.set_alpha(1)
        num_a+=1

    tss=[]
    for t in texts:
        rot=t.get_rotation()
        text=t.get_text()
        fs=t.get_fontsize()
        fst=t.get_fontstyle()
        fw=t.get_fontweight()
        lw=t.get_bbox_patch().get_linewidth()
        ec_rgb=t.get_bbox_patch().get_edgecolor()
        bc_rgb=t.get_bbox_patch().get_facecolor()
        ec='#%02x%02x%02x' %  (int(ec_rgb[0]*255),int(ec_rgb[1]*255),int(ec_rgb[2]*255))
        bc='#%02x%02x%02x' %  (int(bc_rgb[0]*255),int(bc_rgb[1]*255),int(bc_rgb[2]*255))
        tx=t.get_position()[0]
        ty=t.get_position()[1]
        props = dict(boxstyle='round', facecolor=bc, alpha=1)
        ts=fig.axes[0].text(tx,ty,text,rotation=rot,c=ec,fontdict={'size':fs,'weight':fw},bbox=props,picker=5)
        tss.append(ts)

    ars=[]
    for a in arrows:
        xstart=a.get_position()[0]
        ystart=a.get_position()[1]
        arx=a.xy[0]
        ary=a.xy[1]
        lw=a.arrow_patch.get_linewidth()
        lst=a.arrow_patch.get_linestyle()
        la = a.arrow_patch.get_alpha()
        ast = a.arrowprops['arrowstyle']
        ac_rgb = a.arrow_patch.get_edgecolor()
        ac='#%02x%02x%02x' %  (int(ac_rgb[0]*255),int(ac_rgb[1]*255),int(ac_rgb[2]*255))
        ar=fig.axes[0].annotate(s="",xy=(arx,ary),xytext=(xstart,ystart), arrowprops=dict(lw=lw,arrowstyle=ast,color=ac,ls=lst,alpha=la),picker=5)
        ars.append(ar)


    hss=[]
    for h in horizontals:
        hs=fig.axes[0].axhline(y=h.get_data()[1][0],xmin=0,xmax=1,linewidth=h.get_linewidth(),ls=h.get_linestyle(),c=h.get_color(),picker=5)
        hss.append(hs)

    vss=[]
    for v in verticals:
        vs=fig.axes[0].axvline(x=v.get_data()[0][0],ymin=0,ymax=1,linewidth=v.get_linewidth(),ls=v.get_linestyle(),c=v.get_color(),picker=5)
        vss.append(vs)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor(figure.axes[0].get_facecolor())
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    if isinstance(x[0],pd._libs.tslibs.timestamps.Timestamp):
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    else:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
        ax.xaxis.set_minor_locator(AutoMinorLocator())

    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.set_xlabel(figure.axes[0].get_xlabel(),fontdict=font)
    ax.set_xlabel(figure.axes[0].get_ylabel(),fontdict=font)
    ax.set_title(figure.axes[0].get_title(),fontdict=font,x=0.5,y=1.1)
    ax.set_ylim(figure.axes[0].get_ylim())
    ax.set_xlim(figure.axes[0].get_xlim())

    labs = [l.get_label() for l in lines]
    leg = ax.legend(lines,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lines),prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    if j > 1:
        ax2.spines["top"].set_visible(False)
        ax2.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
        ax2.yaxis.set_minor_locator(AutoMinorLocator())
        a2.set_xlabel(figure.axes[1].get_xlabel(),fontdict=font)
        a2.set_ylim(figure.axes[2].get_ylim())


    # try:
    #     m = min([min(calc_minmax(l.get_data()[1])) for l in lines])
    #     M = max([max(calc_minmax(l.get_data()[1])) for l in lines])
    #     ax2.set_ylim(m,M)
    # except:pass
    #
    # try:
    #     m = min(min([calc_minmax(l.get_data()[1]) for l in lines]))
    #     M = max(max([calc_minmax(l.get_data()[1]) for l in lines]))
    #     ax.set_ylim(m,M)
    # except:pass

    return (fig,fig.axes,lines,leg,tss,vss,hss,ars)


def plot_P(TIME,P,PSP,PEN):

    #Setpoint only when control is enabled
    PSP_copy = PSP.copy()
    PSP_copy[PEN==0]=np.NaN

    #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1=ax.plot(TIME,P,label='P(kW)',color=measurement1,linewidth=2)
    #Plot Setpoints
    l2=ax.plot(TIME,PSP_copy,label='P Setpoint',color=setpoint1,linewidth=1)

    lns = l1+l2
    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
        #l.set_zorder(0.1)
    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    m,M=calc_minmax(P,PSP)

    ax.set_ylim(m,M)
    leg = ax.legend(bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=2,prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()
    ax.set_ylabel('P (kW)',fontdict=font)
    ax.set_xlabel('TIME',fontdict=font)
    ax.tick_params(labelsize=10)
    title = ax.set_title('Active Power Control',fontdict=font,x=0.5,y=1.1)

    lines = [l1[0],l2[0]]

    return (fig,fig.axes,lines,leg)

def plot_Pexp(TIME,P,PSP,PEN,PEXP):

    #Setpoint only when control is enabled
    PSP_copy = PSP.copy()
    PSP_copy[PEN==0]=np.NaN

    #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1=ax.plot(TIME,P,label='P(kW)',color=measurement1,linewidth=2)
    #Plot Setpoints
    l2=ax.plot(TIME,PSP_copy,label='P Setpoint',color=setpoint1,linewidth=1)

    l3=ax.plot(TIME,PEXP,label='Pexp(kW)',color=measurement2,linewidth=2)

    lns = l1+l2+l3
    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
        #l.set_zorder(0.1)
    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    m,M=calc_minmax(P,PSP)

    ax.set_ylim(m,M)
    leg = ax.legend(bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=3,prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()
    ax.set_ylabel('P (kW)',fontdict=font)
    ax.set_xlabel('TIME',fontdict=font)
    ax.tick_params(labelsize=10)
    title = ax.set_title('Expected Power Control',fontdict=font,x=0.5,y=1.1)

    lines = [l1[0],l2[0],l3[0]]

    return (fig,fig.axes,lines,leg)

def plot_Q(TIME,Q,QSP,QEN):

    #Setpoint only when control is enabled
    QSP_copy = QSP.copy()
    QSP_copy[QEN==0]=np.NaN

    #Creat Figure
    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1=ax.plot(TIME,Q,label='Q(kVAr)',color=measurement1,linewidth=2)
    #Plot Setpoints
    l2=ax.plot(TIME,QSP_copy,label='Q Setpoint',color=setpoint1,linewidth=1)

    lns = l1+l2
    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
        #l.set_zorder(0.1)
    #Formatting axis

    m,M=calc_minmax(Q,QSP)

    ax.set_ylim(m,M)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(labelsize=10)
    ax.set_ylabel('Q (kVAr)',fontdict=font)
    ax.set_xlabel('TIME',fontdict=font)
    ax.set_title('Reactive Power Control',fontdict=font,x=0.5,y=1.1)
    leg = ax.legend(bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=2,prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    lines = [l1[0],l2[0]]

    return (fig,fig.axes,lines,leg)

def plot_PF(TIME,PF,PFSP,PFEN):

    #Setpoint only when control is enabled
    PFSP_copy = PFSP.copy()
    PFSP_copy[PFEN==0]=np.NaN

    #Creat Figure
    fig, ax = plt.subplots(figsize=(10,5))

    #Plot Measurement
    l1=ax.plot(TIME,PF,label='Power Factor',color=measurement1,linewidth=2)
    #Plot Setpoints
    l2=ax.plot(TIME,PFSP_copy,label='PF Setpoint',color=setpoint1,linewidth=1)


    lns = l1+l2
    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
        #l.set_zorder(0.1)
    #Formatting axis
    m,M=calc_minmax(PF,PFSP)

    ax.set_ylim(m,M)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.set_ylabel('PF',fontdict=font)
    ax.set_xlabel('TIME',fontdict=font)
    ax.set_title('Power Factor Control',fontdict=font,x=0.5,y=1.1)
    leg = ax.legend(bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=2,prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()
    lines = [l1[0],l2[0]]

    return (fig,fig.axes,lines,leg)

def plot_F_P(TIME,P,PSP,F,FSP,FEN):


#     #Setpoint only when control is enabled
    PSP_copy = PSP.copy()
    PSP_copy[FEN==0]=np.NaN
    P_copy = P.copy()
    P_copy[FEN==0]=np.NaN
    FSP_copy = FSP.copy()
    FSP_copy[FEN==0]=np.NaN


#     #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))
    ax2=ax.twinx()
    #Plot Measurement
    l1=ax.plot(TIME,P_copy,label='P(kVAr)',color=measurement1,linewidth=2)
    l2=ax2.plot(TIME,F,label='F(Hz)',color=measurement2,linewidth=2)
    #Plot Setpoints
    l3=ax.plot(TIME,PSP_copy,label='P Setpoint',color=setpoint1,linewidth=0.5)
    #
    l4=ax2.plot(TIME,FSP_copy,label='F Setpoint',color=setpoint2,linewidth=2)
    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    # ax.xaxis.set_major_locator(MaxNLocator(min_n_ticks=10,nbins=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=20))
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    m,M=calc_minmax(P_copy,PSP_copy)
    # ax.set_ylim(m,M)

    m,M=calc_minmax(FSP_copy)
    ax2.set_ylim(m,M)

    lns = l1+l2+l3+l4
    #l.set_zorder(0.1)
    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
    labs = [l.get_label() for l in lns]
    leg = ax.legend(lns,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lns),prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    ax.set_xlabel('TIME',fontdict=font)
    ax.set_ylabel('P (kW)',fontdict=font)
    ax2.set_ylabel('F (Hz)',fontdict=font)
    ax.tick_params(labelsize=10)
    ax.set_title('Frequency Control',fontdict=font,x=0.5,y=1.1)

    lines = [l1[0],l2[0],l3[0],l4[0]]

    return (fig,fig.axes,lines,leg)

def plot_AVR(TIME,V,AVRSP,Q,AVREN):

#     #Setpoint only when control is enabled
    AVRSP_copy = AVRSP.copy()
    AVRSP_copy[AVREN==0]=np.NaN

#     #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))
    ax2=ax.twinx()
    #Plot Measurement
    l1=ax.plot(TIME,V,label='V(V)',color=measurement1,linewidth=2)
    l2=ax2.plot(TIME,Q,label='Q(kVAr)',color=measurement2,linewidth=2)
    # Plot Setpoints
    l3=ax.plot(TIME,AVRSP_copy,label='AVR Setpoint',color=setpoint1,linewidth=0.5)

    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    m,M=calc_minmax(V,AVRSP_copy)

    ax.set_ylim(m,M)

    m,M=calc_minmax(Q)
    ax2.set_ylim(m,M)

    lns = l1+l2+l3
    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
        #l.set_zorder(0.1)
    labs = [l.get_label() for l in lns]
    leg = ax.legend(lns,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lns),prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    ax.set_xlabel('TIME',fontdict=font)
    ax.set_ylabel('Voltage (V)',fontdict=font)
    ax2.set_ylabel('Q (kVAr)',fontdict=font)
    ax.tick_params(labelsize=10)
    ax.set_title('Voltage Simulation',fontdict=font,x=0.5,y=1.1)


    lines = [l1[0],l2[0],l3[0]]

    return (fig,fig.axes,lines,leg)

def plot_QV(TIME,V,QVSP,Q,QSP,QVEN):


#     #Setpoint only when control is enabled
    QVSP_copy = QVSP.copy()
    QSP_copy = QSP.copy()
    QVSP_copy[QVEN==0]=np.NaN
    QSP_copy[QVEN==0]=np.NaN

#     #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))
    ax2=ax.twinx()
    #Plot Measurement
    l1=ax.plot(TIME,V,label='V(V)',color=measurement1,linewidth=0.5)
    l2=ax2.plot(TIME,Q,label='Q(kVAr)',color=measurement2,linewidth=2)
    #Plot Setpoints
    l3=ax.plot(TIME,QVSP_copy,label='Q(V) Setpoint',color=setpoint1,linewidth=2)
    l4=ax2.plot(TIME,QSP_copy,label='Q Setpoint',color=setpoint2,linewidth=1)



    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    m,M=calc_minmax(V,QVSP)
    ax.set_ylim(m,M)

    m,M=calc_minmax(Q,QSP)
    ax2.set_ylim(m,M)

    lns = l1+l2+l3+l4
    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
        #l.set_zorder(0.1)
    labs = [l.get_label() for l in lns]
    leg = ax.legend(lns,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lns),prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    ax.set_xlabel('TIME',fontdict=font)
    ax.set_ylabel('Voltage (V)',fontdict=font)
    ax2.set_ylabel('Q (kVAr)',fontdict=font)
    ax.tick_params(labelsize=10)
    ax.set_title('Q(V) Control',fontdict=font,x=0.5,y=1.1)

    lines = [l1[0],l2[0],l3[0],l4[0]]

    return (fig,fig.axes,lines,leg)

def plot_PQ(TIME,P,Q,QSP,QEN):

#     #Setpoint only when control is enabled
    QSP_copy = QSP.copy()
    QSP_copy[QEN==0]=np.NaN

#     #Creat Figure

    fig, ax = plt.subplots(figsize=(10,5))
    ax2=ax.twinx()
    #Plot Measurement
    l1=ax.plot(TIME,P,label='P(kW)',color=measurement1,linewidth=2)
    l2=ax2.plot(TIME,Q,label='Q(kVAr)',color=measurement2,linewidth=2)
    #Plot Setpoints
    l3=ax2.plot(TIME,QSP_copy,label='Q Setpoint',color=setpoint2,linewidth=0.5)


    #Formatting axis

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    m,M=calc_minmax(P)
    ax.set_ylim(m,M)
    m,M=calc_minmax(Q,QSP)
    ax2.set_ylim(m,M)

    lns = l1+l2+l3

    for l in lns:
        l.set_picker(5)
        l.set_alpha(1)
        #l.set_zorder(0.1)
    labs = [l.get_label() for l in lns]
    leg = ax.legend(lns,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lns),prop=legend_font,
                   fancybox=True, shadow=True)
    fig.autofmt_xdate()

    ax.set_xlabel('TIME',fontdict=font)
    ax.set_ylabel('P (kW)',fontdict=font)
    ax2.set_ylabel('Q (kVAr)',fontdict=font)
    ax.tick_params(labelsize=10)
    ax.set_title('Q Capability',fontdict=font,x=0.5,y=1.1)

    lines = [l1[0],l2[0],l3[0]]

    return (fig,fig.axes,lines,leg)

def plot_meas(TIME,meas):

    #Creat Figure
    fig, axes = plt.subplots(len(meas),1,sharex=True,figsize=(10,8))


    #Plot Measurement
    i=0
    lines=[]
    for k in meas.keys():
        if len(meas)>1:
            l,=axes[i].plot(TIME,meas[k],label=ylabels_dict[list(meas.keys())[i]],color=measurements[i],linewidth=2)
        else:
            l,=axes.plot(TIME,meas[k],label=ylabels_dict[list(meas.keys())[i]],color=measurements[i],linewidth=2)
        lines.append(l)
        i+=1

    #Formatting axis
    i=0
    if len(meas)>1:
        for y in axes:
            y.set_facecolor('#000000')
            y.grid(which='major',ls='--',lw=1,c='#b0b0b0',alpha=0.5)
            y.xaxis.set_minor_locator(AutoMinorLocator())
            y.yaxis.set_minor_locator(AutoMinorLocator())
            y.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            y.tick_params(labelsize=10,labelbottom=True)
            y.spines["top"].set_visible(False)
            y.spines["right"].set_visible(False)
            Min,Max=calc_minmax(meas[list(meas.keys())[i]].iloc[:,0])
            y.set_ylim(Min,Max)
            y.set_ylabel(ylabels_dict[list(meas.keys())[i]],fontdict=font)
            i+=1
    else:
        i=0
        axes.set_facecolor('#000000')
        axes.grid(which='major',ls='--',lw=1,c='#b0b0b0',alpha=0.5)
        axes.xaxis.set_minor_locator(AutoMinorLocator())
        axes.yaxis.set_minor_locator(AutoMinorLocator())
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        axes.tick_params(labelsize=10,labelbottom=True)
        axes.spines["top"].set_visible(False)
        axes.spines["right"].set_visible(False)
        Min,Max=calc_minmax(meas[list(meas.keys())[i]].iloc[:,0])
        axes.set_ylim(Min,Max)
        axes.set_ylabel(ylabels_dict[list(meas.keys())[i]],fontdict=font)


    if len(meas)>1:
        axes[0].set_title('Measurements',fontdict=font,x=0.5,y=1+0.1*len(meas))
        axes[-1].set_xlabel('TIME',fontdict=font)
    else:
        axes.set_title('Measurements',fontdict=font)
        axes.set_xlabel('TIME',fontdict=font)

    labs = [l.get_label() for l in lines]

    for l in lines:
        l.set_alpha(1)

    if len(meas)>1:
        leg = axes[0].legend(lines,labs,bbox_to_anchor=(0.5, 1+0.08*len(meas)),loc='upper center',ncol=len(lines),prop=legend_font,
               fancybox=True, shadow=True)
    else:
        leg = axes.legend(lines,labs,bbox_to_anchor=(0.5, 1.4),loc='upper center',ncol=len(lines),prop=legend_font,
               fancybox=True, shadow=True)


    return (fig,fig.axes,lines,leg)

def custom_plot(x,ys):
    import random
    import string

    def randstring(n):
      alphabet = string.ascii_letters[0:6] + string.digits
      hexc = ''.join(random.choice(alphabet) for i in range(n))
      return '#'+hexc

    lines=[]
    axes=[]
    fig, ax = plt.subplots(figsize=(10,5))
    axes.append(ax)

    for arg in ys:
        if arg["ax2"]==True:
            ax2 = ax.twinx()
            axes.append(ax2)
            break
    i=1
    j=1
    for arg in ys:
        if arg["ax2"]==False:
            l,=ax.plot(x,arg["tr"],label="Y1,"+str(i),color=randstring(6),linewidth=1)
            lines.append(l)
            i+=1
        else:
            l,=ax2.plot(x,arg["tr"],label="Y2,"+str(j),color=randstring(6),linewidth=1)
            lines.append(l)
            j+=1

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor('#000000')
    ax.grid(which='major',ls='--',lw=0.5,c='#b0b0b0',alpha=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    if isinstance(x[0],pd._libs.tslibs.timestamps.Timestamp):
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    else:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
        ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.set_xlabel('X Label goes here',fontdict=font)
    ax.set_ylabel('Y1 label goes here',fontdict=font)
    ax.set_title('Title goes here',fontdict=font,x=0.5,y=1.1)

    if j > 1:
        ax2.spines["top"].set_visible(False)
        ax2.yaxis.set_major_locator(MaxNLocator(nbins=20,integer=True))
        ax2.yaxis.set_minor_locator(AutoMinorLocator())
        ax2.set_ylabel('Y2 label goes here',fontdict=font)

    for l in lines:
        l.set_alpha(1)

    labs = [l.get_label() for l in lines]
    leg = axes[0].legend(lines,labs,bbox_to_anchor=(0.5, 1.1),loc='upper center',ncol=len(lines),prop=legend_font,
                   fancybox=True, shadow=True)
    try:
        m = min([min(calc_minmax(y["tr"])) for y in args if y["ax2"]==True])
        M = max([max(calc_minmax(y["tr"])) for y in args if y["ax2"]==True])
        ax2.set_ylim(m,M)
    except:pass

    try:
        m = min([min(calc_minmax(y["tr"])) for y in args if y["ax2"]==False])
        M = max([max(calc_minmax(y["tr"])) for y in args if y["ax2"]==False])
        ax.set_ylim(m,M)
    except:pass
    fig.autofmt_xdate()
    return (fig,fig.axes,lines,leg)
