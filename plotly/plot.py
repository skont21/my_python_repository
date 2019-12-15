#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pickle
from plotly import tools
import plotly.graph_objs as go
from sys import argv
import traces_v2
import layouts
import re
import os

reg = re.compile('.*csv')

if argv[1] not in list(filter(reg.search, os.listdir("."))) :
    print("Wrong File")
    exit()

layouts.main()
traces_v2.main(argv[1])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


with open('layouts.pickle', 'rb') as f:
    layout_P, layout_Q,layout_PF,layout_V,layout_F, layout_QP,layout_PQV= pickle.load(f)

with open('traces.pickle', 'rb') as f:
    P,Q,PF,V,F,PSP,QSP,VSP,PFSP,FSP,Pf,Pq,Qv,PQV_P,PQV_Q,PQV_V= pickle.load(f)

colors = {
    'background': '#FFFFFF',
    'text': '#7FDBFF'
}

if argv[2] == 'P' :
    app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[


        dcc.Graph(
            id='Active Power',
            config = {'editable': True},
            figure={
                'data': [P,PSP],
                'layout': layout_P}
        )
    ])

elif  argv[2] == 'Q' :

    app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[


        dcc.Graph(
            id='Active Power',
            config = {'editable': True,},
            figure={
                'data': [Q,QSP],
                'layout': layout_Q    }
        )
    ])


elif  argv[2] == 'PF' :

    app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[


        dcc.Graph(
            id='Active Power',
            config = {'editable': True,},
            figure={
                'data': [PF,PFSP],
                'layout': layout_PF    }
        )
    ])

elif  argv[2] == 'F' :

    app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[


        dcc.Graph(
            id='Active Power',
            config = {'editable': True,},
            figure={
                'data': [FSP,Pf],
                'layout': layout_F  }
        )
    ])

elif  argv[2] == 'V' :

    app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[


        dcc.Graph(
            id='Active Power',
            config = {'editable': True,},
            figure={
                'data': [VSP,V,Qv],
                'layout': layout_V   }
        )
    ])

elif  argv[2] == 'QP' :

    app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[


        dcc.Graph(
            id='Active Power',
            config = {'editable': True,},
            figure={
                'data': [QSP,Q,Pq],
                'layout': layout_QP   }
        )
    ])

elif  argv[2] == 'PQV' :

    app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[


        dcc.Graph(
            id='Active Power',
            config = {'editable': True,},
            figure={
                'data': [PQV_P,PQV_Q,PQV_V],
                'layout': layout_PQV   }
        )
    ])

else:
    print("Wrong Parameters")
    exit()

if __name__ == '__main__':
    app.run_server(debug=True)
