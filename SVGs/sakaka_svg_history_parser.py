import pandas as pd
data = pd.read_csv('sakaka_svg_history.csv',header=None)
E =list(data[0].str.split())
# Time=[]
# Setpoints=[]
# SVG=[]
entry = {"Time":"","Setpoint":"","SVG":""}
data_dict=[]
for e in E:
    try:
        Setpoint = int(e[-1])
        Time = e[2]
        id = -2
        if e[-2]=="--":
            id = -3
        if e[id][-1]=='0':
            SVG="SVG1"
        else:
            SVG="SVG2"
        data_dict.append({"Time":Time,"Setpoint":Setpoint,"SVG":SVG})
    except:
        pass
data_fixed=pd.DataFrame(data_dict)
data_fixed.to_csv('sakaka_svg_history_fixed.csv')
