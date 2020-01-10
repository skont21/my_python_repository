import pandas as pd
data = pd.read_csv('svg_test_q.csv')
start = data.columns[0]
T = [start]
T = T + list(data[data[start].str.startswith("Mon")][start])
Time = [t.split()[3] for t in T]
keys_ = ['Time']+list(set(list(data[data[start].str.startswith('SVG')][start])))
entry = dict([(k," ") for k in keys_])
data_dict = []
j=0
for i in range(len(Time)):
    data_dict.append({keys_[0]:Time[i],keys_[1]:data.iloc[j+1,0],keys_[2]:data.iloc[j+3,0],
                      keys_[3]:data.iloc[j+5,0],keys_[4]:data.iloc[j+7,0]})
    j=j+9

data_fixed = pd.DataFrame(data_dict)
data_fixed.to_csv('svg_test_q_fixed.csv')
