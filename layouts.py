import plotly.offline as py
import plotly.graph_objs as go
import pickle
from plotly import tools
import sys

def main():



    layout_P = {
      #"autosize": True,
      'height': 800,
      "legend": {
        "x": 0.485,
        "y": 1.07,
        "font": {
          "family": "Arial",
          "size": 18
        },
        "orientation": "h",
        "traceorder": "normal",
        "xanchor": "center",
        "yanchor": "auto"
      },
      "title": {
        "x": 0.49,
        "font": {"size": 24},
        "text": "<b>Active Power Control&nbsp;</b>"
      },
      "xaxis": {
        #"autorange": True,
        #"fixedrange": False,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "linecolor": "rgb(0, 0, 0)",
        "showgrid": True,
        "showline": True,
        "range" : ['02:58:23','02:59:50'],
        "showspikes": False,
        "tickangle": 45,
        "tickfont": {"size": 15},
        "tickmode": "auto",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<br><br><b>Time</b>",
        },
        # 'rangeslider': {'visible': True},
        'type': 'time',
      },
      "yaxis": {
        "autorange": True,
        #"dtick": 10000,
        "linecolor": "rgb(0, 0, 0)",
         "gridcolor": "rgb(255, 255, 255)",
         "gridwidth": 1,
        # "range": [arg1, arg2],
        "showline": True,
        "tickfont": {"size": 15},
        ##"tickmode": "linear",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Active Power(kW)</b>",
          "position": 0.95
        },
        "type": "linear"
      },

      'plot_bgcolor': '#E6E6E6',
      #'paper_bgcolor': 'rgb(128.133.133)'
    }

    layout_PF = {
      'height': 800,
      "autosize": True,
      "dragmode": "zoom",
      "font": {
        "family": "Arial",
        "size": 12
      },
      "legend": {
        "x": 0.48,
        "y": 1.07,
        "font": {"size": 15},
        "orientation": "h",
        "xanchor": "center",
        "yanchor": "auto"
      },
      "margin": {
        "t": 100,
        "b": 80,
        "l": 80
      },
      "title": {
        "x": 0.485,
        "font": {"size": 24},
        "text": "<b>Power Factor Control&nbsp;</b>"
      },
      #"width": 1392,
      "xaxis": {
       "anchor":"y",
       #"domain": [0.1,0.9],
        #"autorange": True,
        #"fixedrange": False,
        "linewidth": 1,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"nticks": 0,
        #"range": [104, 397.7142857142857],
        #},
        "showline": True,
        "automargin":True,
        "showspikes": False,
        "tickangle": 45,
        "tickfont": {"size": 15},
        "tickmode": "auto",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<br><b>Local</b> <b>Time&nbsp;</b>"
        },
        "type": "category",
        "zeroline": True
      },
      "yaxis": {
       #domain": [0,0.265],
        "automargin": True,
        "autorange": True,
        #"tick0":0,
        "dtick": 0.01,
        "tickangle":45,
        "tickprefix": "<b>",
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"range": [0.9, 1.05],
        "separatethousands": False,
        "showline": True,
        "side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Power Factor</b>"
        },
        "type": "linear"
      },
      'plot_bgcolor': '#E6E6E6',
    }


    layout_Q = {
      'height': 800,
      #"autosize": True,
      "legend": {
        "x": 0.485,
        "y": 1.07,
        "font": {
          "family": "Arial",
          "size": 18
        },
        "orientation": "h",
        "traceorder": "normal",
        "xanchor": "center",
        "yanchor": "auto"
      },
      "title": {
        "x": 0.49,
        "font": {"size": 22},
        "text": "<b>Reactive Power Control&nbsp;</b>"
      },
      "xaxis": {
        #"autorange": True,
        #"fixedrange": False,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "linecolor": "rgb(0, 0, 0)",
        #"range": [0, 1486.2222222222222],
        "showgrid": True,
        "showline": True,
        "showspikes": False,
        "tickangle": 45,
        "tickfont": {"size": 15},
        "tickmode": "auto",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Local Time</b>"
        },
        "type": "category"
      },
      "yaxis": {
        #"autorange": True,
        "dtick": 1000,
        "linecolor": "rgb(0, 2, 5)",
        #"range": [86.33333333333331, 2159.6666666666665],
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "showline": True,
        "tickfont": {"size": 15},
        #"tickmode": "linear",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Reactive Power(kVar)</b>"
        },
        "type": "linear"
      },
      'plot_bgcolor': '#E6E6E6',
    }

    layout_QP = {
      'height': 800,
      #"autosize": True,
      "legend": {
        "x": 0.485,
        "y": 1.07,
        "font": {
          "family": "Arial",
          "size": 18
        },
        "orientation": "h",
        "traceorder": "normal",
        "xanchor": "center",
        "yanchor": "auto"
      },
      "title": {
        "x": 0.49,
        "font": {"size": 22},
        "text": "<b>Q Capability&nbsp;</b>"
      },
      "xaxis": {
        #"autorange": True,
        #"fixedrange": False,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "linecolor": "rgb(0, 0, 0)",
        #"range": [0, 1486.2222222222222],
        "showgrid": True,
        "showline": True,
        "showspikes": False,
        "tickangle": 45,
        "tickfont": {"size": 15},
        "tickmode": "auto",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Local Time</b>"
        },
        "type": "category"
      },
      "yaxis": {
        "autorange": True,
        #"dtick": 1000,
        "linecolor": "rgb(0, 2, 5)",
        #"range": [86.33333333333331, 2159.6666666666665],
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "showline": True,
        "tickfont": {"size": 15},
        #"tickmode": "linear",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Reactive Power(kVar)</b>"
        },
        "type": "linear"
      },
      "yaxis2": {
        #"automargin": True,
        "autorange": True,
        # "dtick": 1000,
        #"tickangle":45,
        "tickprefix": "<b>",
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"range": [50000, 60000],
        #"separatethousands": False,
        "showline": True,
        #"side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Active Power(kW)</b>"
        },
        "overlaying":'y',
         "side":'right',
        "type": "linear"
      },
      'plot_bgcolor': '#E6E6E6',
    }


    layout_V = {
      'height': 800,
      #"autosize": True,
      "dragmode": "zoom",
      "font": {
        "family": "Arial",
        "size": 12
      },
      "legend": {
        "x": 0.48,
        "y": 1.07,
        "font": {"size": 15},
        "orientation": "h",
        "xanchor": "center",
        "yanchor": "auto"
      },
      "margin": {
        "t": 100,
        "b": 80,
        "l": 80
      },
      "title": {
        "x": 0.485,
        "font": {"size": 24},
        "text": "<b>Voltage Control&nbsp;</b>"
      },
      #"width": 1392,
      "xaxis": {
        #"autorange": True,
        #"fixedrange": False,
        "linewidth": 1,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"nticks": 0,
        #"range": [104, 397.7142857142857],
        #},
        "showline": True,
        "automargin":True,
        "showspikes": False,
        "tickangle": 45,
        "tickfont": {"size": 15},
        "tickmode": "auto",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<br><b>Local</b> <b>Time&nbsp;</b>"
        },
        "type": "category",
        "zeroline": True
      },
      "yaxis": {
        "automargin": True,
        ##"autorange": True,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"dtick": 500,
        #"tickangle":45,
        "range": [225000, 235000],
        #"separatethousands": False,
        "showline": True,
        "side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        #"tickmode": "linear",
        "tickprefix": "<b>",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Voltage (V)</b>"
        },
        "type": "linear"
      },
      "yaxis2": {
        #"automargin": True,
        ##"autorange": True,
        #"dtick": 1000,
        #"tickangle":45,
        "tickprefix": "<b>",
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "range": [-15000, 15000],
        "separatethousands": False,
        "showline": True,
        #"side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Reactive Power(kVar)</b>"
        },
        "overlaying":'y',
         "side":'right',
        "type": "linear"
      },
      'plot_bgcolor': '#E6E6E6',
    }

    layout_F = {
     'height': 800,
     # "autosize": True,
      "dragmode": "zoom",
      "font": {
        "family": "Arial",
        "size": 12
      },
      "legend": {
        "x": 0.48,
        "y": 1.07,
        "font": {"size": 15},
        "orientation": "h",
        "xanchor": "center",
        "yanchor": "auto"
      },
      "margin": {
        "t": 100,
        "b": 80,
        "l": 80
      },
      "title": {
        "x": 0.485,
        "font": {"size": 24},
        "text": "<b>Frequency Control - Underfrequency &nbsp;</b>"
      },
      #"width": 1392,
      "xaxis": {
        #"autorange": True,
        #"fixedrange": False,
        "linewidth": 1,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"nticks": 0,
        #"range": [104, 397.7142857142857],
        #},
        "showline": True,
        "automargin":True,
        "showspikes": False,
        "tickangle": 45,
        "tickfont": {"size": 15},
        "tickprefix": "<b>",
        "tickmode": "auto",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<br><b>Local</b> <b>Time&nbsp;</b>"
        },
        "type": "category",
        "zeroline": True
      },
      "yaxis": {
        #"automargin": True,
        #"autorange": True,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "dtick": 0.1,
        #"tickangle":45,
        #"range": [97.44444444444443, 648.718482905983],
        "range": [49, 52],
        "separatethousands": False,
        "showline": True,
        "side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        "tickprefix": "<b>",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Frequency Setpoint(Hz)</b>"
        },
        "type": "linear"
      },
      "yaxis2": {
        "automargin": True,
        #"autorange": True,
        "dtick": 1000,
        #"tickangle":45,
        "tickprefix": "<b>",
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        "range": [15000, 25000],
        "separatethousands": False,
        "showline": True,
        #"side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Active Power(kW)</b>"
        },
        "overlaying":'y',
         "side":'right',
        "type": "linear"
      },
      'plot_bgcolor': '#E6E6E6',
    }

    layout_PQV = {
     'height': 800,
     # "autosize": True,
     #'width' : 1500,
      "dragmode": "zoom",
      "font": {
        "family": "Arial",
        "size": 12
      },
      "legend": {
        "x": 0.48,
        "y": 1.07,
        "font": {"size": 15},
        "orientation": "h",
        "xanchor": "center",
        "yanchor": "auto"
      },
      "margin": {
        "t": 100,
        "b": 80,
        "l": 80
      },
      "title": {
        "x": 0.485,
        "font": {"size": 24},
        "text": "<b>P_Q_V&nbsp;</b>"
      },
      #"width": 1392,
      "xaxis": {
        "domain" : [0, 0.9],
        #"autorange": True,
        #"fixedrange": False,
        "linewidth": 1,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"nticks": 0,
        #"range": [104, 397.7142857142857],
        #},
        "showline": True,
        "automargin":True,
        "showspikes": False,
        "tickangle": 45,
        "tickfont": {"size": 15},
        "tickprefix": "<b>",
        "tickmode": "auto",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<br><b>Local</b> <b>Time&nbsp;</b>"
        },
        "type": "category",
        "zeroline": True
      },
      "yaxis": {
        "automargin": True,
        "autorange": True,
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        #"dtick": 0.05,
        #"tickangle":45,
        #"range": [97.44444444444443, 648.718482905983],
        "separatethousands": False,
        "showline": True,
        "side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        "tickprefix": "<b>",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Active Power</b>"
        },
        "type": "linear"
      },
      "yaxis2": {
        "automargin": True,
        "autorange": True,
        # "dtick": 1000,
        #"tickangle":45,
        "tickprefix": "<b>",
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        # "range": [18000, 28000],
        "separatethousands": False,
        "showline": True,
        #"side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Reactive Power(kVAr)</b>"
        },
        "overlaying":'y',
        "anchor":"x",
         "side":'right',
        "type": "linear"
      },
      "yaxis3": {
        "automargin": True,
        "autorange": True,
        # "dtick": 1000,
        #"tickangle":45,
        "tickprefix": "<b>",
        "gridcolor": "rgb(255, 255, 255)",
        "gridwidth": 1,
        # "range": [18000, 28000],
        "separatethousands": False,
        "showline": True,
        #"side": "left",
        "tickfont": {"size": 15},
        "tickformat": "",
        #"tickmode": "linear",
        "ticks": "outside",
        "title": {
          "font": {"size": 18},
          "text": "<b>Voltage(V)</b>"
        },
        "anchor":"free",
        "overlaying":"y",
        "side":"right",
        "position": 0.95
      },
      'plot_bgcolor': '#E6E6E6',
    }

    with open('layouts.pickle', 'wb') as f:
        pickle.dump([layout_P,layout_Q,layout_PF,layout_V,layout_F,layout_QP,layout_PQV], f)

if __name__=='__main__':
    sys.exit(main())
