import pickle
import numpy as np
import sys
import pandas as pd
import datetime
#
# def bounds(l1,l2):
#     lb=min(min(l1),min(l2))
#     ub=max(max(l2),max(l2))
#     range = ub-lb
#     ticks = 15
#     tick_range = round((range/ticks)/1000)*1000
#     lb_n=tick_range*round(lb/tick_range)
#     ub_n=tick_range*round(1+ (ub+1)/tick_range)
#     return lb_n
#     return ub_n

def main(arg1):

    # csv = np.genfromtxt (arg1, dtype= 'str' ,delimiter=" ",invalid_raise = False)
    data = pd.read_csv(arg1,delimiter= " ")
    # tr = []
    # for i in range(1,16):
    #     trace = csv[1:,i].astype(np.float)
    #     tr.append(trace)
    # P,F,Q,V,PF,PSP,FSP,QSP,VSP,PFSP=[]

    # cols=data.columns.tolist()
    # tr=[]
    # for i in range(1,len(cols)):
    #     trace = data[cols[i]].astype('float').tolist()
    #     #trace = trace[0:len(trace):10]
    #     tr.append(trace)

    try:
        Pt= data['ppc:P0'].tolist()
    except KeyError:
        Pt=[]
    try:
        Ft= data['ppc:F'].tolist()
    except KeyError:
        Ft=[]
    try:
        Qt= data['ppc:Q0'].tolist()

    except KeyError:
        Qt= []
    try:
        Vt= data['ppc:V0'].tolist()

    except KeyError:
        Vt= []
    try:
        PFt= data['ppc:PF'].tolist()

    except KeyError:
        PFt= []
    try:
        Pen=data['apc:En'].tolist()

    except KeyError:
        Pen= []
    try:
        Fen=data['apc:FCEn'].tolist()

    except KeyError:
        Fen= []
    try:
        Qen=data['rpc:En'].tolist()

    except KeyError:
        Qen= []
    try:
        Ven=data['avr:En'].tolist()

    except KeyError:
        Ven= []
    try:
        PFen= data['pfc:En'].tolist()

    except KeyError:
        PFEn= []
    try:
        PSPt=data['apc:PSP0_eff'].tolist()

    except KeyError:
        PSPt= []
    try:
        FSPt=data['apc:FSP'].tolist()

    except KeyError:
        FSPt= []
    try:
        QSPt=data['rpc:QSP0'].tolist()

    except KeyError:
        QSPt= []
    try:
        VSPt=data['avr:VSP0'].tolist()

    except KeyError:
        VSPt= []
    try:
        PFSPt= data['pfc:PFSP'].tolist()
    except KeyError:
        PFSPt= []


    # time = csv[1:,0]
    t = data['TIME']

    td=[]
    for i in range(0,len(t)):
        td.append(t[i].split(".")[0])

    time=[]
    for t in td:
        time.append(datetime.datetime.strptime(t, '%H:%M:%S').time())
    #time = time[0:len(time):10]

    # # Pind=np.where(tr[5]==0)
    try:
        Pind=data.index[data['apc:En']==0].tolist()
    except KeyError:
        Pind=[]
    # # Find=np.where(tr[6]==0)
    try:
        Find=data.index[data['apc:FCEn']==0].tolist()
    except KeyError:
        Find=[]
    # # Qind=np.where(tr[7]==0)
    try:
        Qind=data.index[data['rpc:En']==0].tolist()
    except KeyError:
        Qind=[]
    # # Vind=np.where(tr[8]==0)
    try:
        Vind=data.index[data['avr:En']==0].tolist()
    except KeyError:
        Vind=[]
    # # PFind=np.where(tr[9]==0)
    try:
        PFind=data.index[data['pfc:En']==0].tolist()
    except KeyError:
        PFind=[]

    # tr[10][Pind]=np.nan
    for i in Pind:
        PSPt[i] = np.nan
    # tr[11][Find]=np.nan
    for i in Find:
        FSPt[i] = np.nan
    # tr[12][Qind]=np.nan
    for i in Qind:
        QSPt[i] = np.nan
    # tr[13][Vind]=np.nan
    for i in Vind:
        VSPt[i] = np.nan
    # tr[14][PFind]=np.nan
    for i in PFind:
        PFSPt[i] = np.nan



    colors = {"measurement" : "rgb(0,0,104)",
              "Setpoints" : "rgb(234,0,0)" ,
              "measurement_2" : "rgb(62,150,81)",
              "Setpoints_2" : "rgb(250,150,0)"
              }

    P = {"x" :time,
            "y":Pt,
            "mode": "lines",
            "name": "<b>Active Power</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "line",
            "line": {"width":2,"color": colors["measurement"]}
            }

    F = {"x" :time,
        "y":Ft,
        "mode": "lines",
        "name": "<b>Frequency</b>",
        "opacity": 1,
        "showlegend": True,
        "type": "scatter",
        "line": {"color": colors["measurement"]}
        }

    Q = {"x":time,
            "y":Qt,
            "mode": "lines",
            "name": "<b>Reactive Power</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "scatter",
            "line": {"width":2,"color": colors["measurement"]}
            }

    V = {"x":time,
            "y":Vt,
            "mode": "lines",
            "name": "<b>Voltage</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "scatter",
            "line": {"width":2,"color": colors["measurement_2"]}
            }

    PF = {"x":time,
        "y":PFt,
        "mode": "lines",
        "name": "<b>Power Factor</b>",
        "opacity": 1,
        "showlegend": True,
        "type": "scatter",
        "line": {"width":3,"color": colors["measurement"]}
        }


    PSP = {"x" :time,
        "y":PSPt,
        "mode": "lines",
        "name": "<b>Active Power Setpoint</b>",
        "opacity": 0.5,
        "showlegend": True,
        "type": "line",
        "line": {"width":1,"color": colors["Setpoints"]},
        "error_y":{
        "array":PSPt,
        "symmetric": True,
        "thickness": 5,
        "type": "constant",
        "value": 1500,
        "visible": True},

        }

    FSP = {"x" :time,
        "y":FSPt,
        "mode": "lines",
        "name": "<b>Frequency Setpoint</b>",
        "opacity": 0.5,
        "showlegend": True,
        "type": "scatter",
        "line": {"width":2,"color": colors["Setpoints"]}

        }


    QSP = {"x":time,
            "y":QSPt,
            "mode": "lines",
            "name": "<b>Reactive Power Setpoint </b>",
            "opacity": 0.5,
            "showlegend": True,
            "type": "scatter",
            "line": {"width":10,"color": colors["Setpoints"]},
            "error_y":{
            "array":QSPt,
            "symmetric": True,
            "thickness": 5,
            "type": "constant",
            "value": 220,
            "visible": True},
            }

    VSP = {"x" :time,
        "y":VSPt,
        "mode": "lines",
        "name": "<b>Voltage Setpoint</b>",
        "opacity": 0.5,
        "showlegend": True,
        "type": "scatter",
        #"mode": "markers",
        "yaxis": "y",
        "line": {"width":5,"color": colors["Setpoints"]},
        # "error_y":{
        # "array":PFSP,
        # "symmetric": True,
        # "thickness": 5,
        # "type": "constant",
        # "value": 115,
        # "visible": True},
        }

    PFSP = {"x":time,
        "y":PFSPt,
        "mode": "lines",
        "name": "<b>Power Factor Setpoint</b>",
        "opacity": 0.5,
        "showlegend": True,
        #"line": {"width": 15},
        "type": "scatter",
        "line": {"width":5,"color": colors["Setpoints"]},
        "error_y":{
        "array":PFSPt,
        "symmetric": True,
        "thickness": 15,
        "type": "constant",
        "value": 0.002,
        "visible": True},
        }

    Pf = {"x" :time,
            "y":Pt,
            "mode": "lines",
            "name": "<b>Active Power</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "line",
            "yaxis": "y2",
            "line": {"width":2,"color": colors["measurement_2"]}
            }


    Pq = {"x" :time,
            "y":Pt,
            "mode": "lines",
            "name": "<b>Active Power</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "scatter",
            "yaxis": "y2",
            "line": {"width":2,"color": colors["measurement_2"]}
            }

    Qv = {"x":time,
            "y":Qt,
            "mode": "lines",
            "name": "<b>Reactive Power</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "line",
            "yaxis": "y2",
            "line": {"width":2,"color": colors["Setpoints_2"]}
            }
    PQV_P = {"x" :time,
            "y":Pt,
            "mode": "lines",
            "name": "<b>Active Power</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "line",
            "yaxis": "y",
            "line": {"width":2,"color": colors["measurement_2"]}
            }

    PQV_Q = {"x":time,
            "y":Qt,
            "mode": "lines",
            "name": "<b>Reactive Power</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "line",
            "yaxis": "y2",
            "line": {"width":2,"color": colors["Setpoints_2"]}
            }
    PQV_V = {"x":time,
            "y":Vt,
            "mode": "lines",
            "name": "<b>Voltage</b>",
            "opacity": 1,
            "showlegend": True,
            "type": "line",
            "yaxis": "y3",
            "line": {"width":2,"color": colors["Setpoints"]}
            }



    with open('traces.pickle', 'wb') as f:
        pickle.dump([P,Q,PF,V,F,PSP,QSP,VSP,PFSP,FSP,Pf,Pq,Qv,PQV_P,PQV_Q,PQV_V], f)

if __name__=='__main__':
    sys.exit(main(sys.argv[1]))
