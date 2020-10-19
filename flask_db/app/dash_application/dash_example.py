"""Create a Dash app within a Flask app."""
import base64
import datetime
import io
import numpy as np
import pandas as pd
import random
from .layout import html_layout

from pathlib import Path
import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
# import plotly.express as px
import plotly.graph_objects as go

typefaces =["Arial", "Balto", "Courier New", "Droid Sans", "Droid Serif", "Droid Sans Mono", "Gravitas One", "Old Standard TT","Open Sans","Overpass","PT Sans Narrow","Raleway","Times New Roman"]
first_time=True



def Add_Dash(server):
    """Create a Dash app."""
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'
    ,'/static/dist/css/styles.css?version=105%']

    external_scripts = ['/static/dist/js/includes/jquery.min.js',
                        '/static/dist/js/main.js']

    dash_app = dash.Dash(server=server,
                         external_stylesheets=external_stylesheets,
                         external_scripts=external_scripts,
                         routes_pathname_prefix='/graphs/')

    # dash_app.config.suppress_callback_exceptions = True

    fig = dict({
            "data":[],
            "layout":{}
    })
# ------------------------------------------
    title_text = 'Title'
    title_size = 30
    title_family = 'Arial'
    title_position= 0.5
    title_color = dict(r=0,g=0,b=0,a=1)
# ------------------------------------------
    xlabel_text = 'Xlabel'
    y1label_text = 'Y1_label'
    y2label_text = 'Y2_label'
    y3label_text = 'Y3_label'
    label_size = 20
    label_family = 'Arial'
    label_color = dict(r=0,g=0,b=0,a=1)
# ------------------------------------------
    legend_size = 14
    legend_family = 'Arial'
    legend_bordersize = 1
    legendfont_color = dict(r=0,g=0,b=0,a=1)
    legendborder_color = dict(r=0,g=0,b=0,a=1)
    legendbg_color = dict(r=255,g=255,b=255,a=1)
    legend_hposition = 0.5
    legend_vposition = 1.1
# ------------------------------------------
    bg_color = dict(r=0,g=0,b=0,a=0.8)
# ------------------------------------------
    grid_width = 1
    grid_color = dict(r=100,g=100,b=100,a=0.5)
# ------------------------------------------

    # Override the underlying HTML template
    dash_app.index_string = html_layout

    traces_children = []
    y_axes=[]
    for i in range(1,4):
        axis = "Y"+str(i)
        y_axes.append(axis)

    def generate_trace(id,rgb_color):
        return (html.Div(id='new-trace-'+str(id),style ={'marginTop':'10px','display':'none'},
            children=[

                html.Div(style={'backgroundColor':'#2a3f5f','border':'1px solid black','borderRadius':'5px','position':'relative','display':'flex','alignItems':'flexStart','justifyContents':'flexStart'},
                    children=[html.Div(children=['Trace '+str(id)+':'],style={'flexGrow':'8','paddingLeft':'2%','color':'white'}),
                        html.Button('X',id='close-trace-'+str(id),className='close',n_clicks=0,style={'flexGrow':'1','padding':'0','border':'none','color':'#f7f3f3','fontWeight':'bold','height':'0px','lineHeight':'200%'}),
                        html.Button('﹀',id='trace-appear-'+str(id),n_clicks=0,style={'flexGrow':'1','height':'0px','lineHeight':'200%','border':'none','color':'white','fontWeight':'bold','padding':'0px'})
                        ]),

                html.Div(id='trace-comp-'+str(id),style ={'padding':'0 10px 0 10px','display':'none','backgroundColor':'white','border':'1px solid grey','borderRadius':'5px'},
                    children=[
                        html.Div(id='trace-input'+str(id),style={'position':'relative','marginTop':'5%','display':'flex','alignItems':'flexStart','justifyContents':'flexStart'},
                            children=[html.Label('Trace Name'),
                                dcc.Input(id='trace-input-text'+str(id),value="",type='text',style={'marginTop':'0.75rem','width':'100%'}),
                                ]),
                        html.Hr(),

                        html.Div(id='xtrace-select-'+str(id),style={'position':'relative','marginTop':'5%','display':'flex','alignItems':'flexStart','justifyContents':'flexStart'},
                            children=[html.Div(children=['X:'],style={'width':'10%','paddingTop':'1%'}),
                                dcc.Dropdown(id='xtrace-input-select-'+str(id),style={'width':'80%','flex-grow':'1'},placeholder="X trace")
                                ]),
                        html.Div(id='ytrace-select-'+str(id),style={'position':'relative','marginTop':'5%','display':'flex','alignItems':'flexStart','justifyContents':'flexStart'},
                            children=[html.Div(['Y:'],style={'width':'10%','paddingTop':'1%'}),
                                dcc.Dropdown(id='ytrace-input-select-'+str(id),style={'marginRight':'2%','flex-grow':'7'},
                                placeholder="Y trace"),
                                dcc.Dropdown(id='yaxis-select-'+str(id),style={'flex-grow':'3'},
                                placeholder="Y axis",options=[{'label':y_axis,'value':y_axis} for y_axis in y_axes])
                                ]),

                        html.Hr(),
                        html.Div(id='trace-fontcolor-'+str(id),style={'display':'flex','flexWrap':'wrap'},
                            children=[html.Label('Color',style={'flexGrow':'9'}),html.Button('﹀',id='trace-color-appear'+str(id),n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                            daq.ColorPicker(id='trace-color-picker'+str(id),style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                value=dict(rgb=rgb_color)
                            ),
                            html.Div(id='trace-color-picker-output'+str(id))
                            ]),

                        html.Hr(),
                        html.Div(id='trace-width'+str(id),
                            children=[html.Label('Width'),
                            dcc.Input(id='trace-input-width'+str(id),type='number',value=2,min=1,step=1,style={'width':'30%'}),
                            html.Hr()]),

                        html.Div(id='trace-type'+str(id),
                            children=[html.Label('Type'),
                                    dcc.Dropdown(id='trace-input-type'+str(id),value='lines',style={'width':'80%'},placeholder="Select Trace Type",
                                        options=[{'label':type,'value':type} for type in ["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"]]),
                                    html.Hr()]),

                        html.Div(id='trace-deadband'+str(id),
                            children=[html.Label('Deadband'),
                            dcc.Input(id='trace-input-deadband'+str(id),type='number',value=0,min=0,style={'width':'50%'}),
                            html.Hr()])
                    ])
            ]))


    for i in range(0,15):
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        rgb = dict(r=r,g=g,b=b,a=1)
        traces_children.append(generate_trace(i,rgb))

    # print(traces_children[0])

    dash_app.layout = html.Div(

        style ={'display':'flex',
                'height':'94vh',
                'marginTop':'55px'
                },

        children=[
            #Left Panel
            html.Div(id="left-panel",
                style={
                    'flex':'1 1 25%',
                    'backgroundColor':'white',
                    'display':'flex'
                },
                children=[
                    #sidebar
                    html.Div(id="sidebar",
                        style={
                            'flex':'1 1 30%',
                            'minHeight':'100%',
                            'display':'flex',
                            'flexDirection':'column'
                        },
                        children=[
                        # Upload
                            dcc.Upload(id="upload-data",

                                style={
                                     'textAlign': 'center',
                                     'margin':'5%'
                                      },
                                multiple=True,

                                children = html.Div(
                                    ['Drag and Drop or ',
                                    html.A('Select File')],

                                    style ={'padding':'10%',
                                            'borderWidth':'1px',
                                            'borderStyle':'dashed',
                                            'borderRadius':'5px',
                                            'backgroundColor':'white'}
                                    )
                            ),
                            # Upload

                            html.Button('Title',id="Title",n_clicks=0,className="side_button"),
                            html.Button('Traces',id="Traces",n_clicks=0,className="side_button"),
                            html.Button('Labels',id="Labels",n_clicks=0,className="side_button"),
                            html.Button('Legend',id="Legend",n_clicks=0,className="side_button"),
                            html.Button('Figure',id="Figure",n_clicks=0,className="side_button"),
                            html.Button('Grid',id="Grid",n_clicks=0,className="side_button"),
                            html.Button('Axes',id="Axes",n_clicks=0,className="side_button"),
                            html.Button('Annotate',id="Annotate",n_clicks=0,className="side_button")
                        ]
                    ),
                    # sidebar

                    html.Div(id="panel",

                        style={
                            'flex':'1 1 70%',
                            'backgroundColor':'#ebf0f8',
                            'overflow':'auto'},

                        children =[
                            html.Div(id='conf',
                                children=[

                                # -----------------------------
                                    html.Div(id='conf-title',className="conf",style={'display':'none'},
                                    children=[
                                        html.Div(id='title-title',
                                            children=['Title']),
                                        html.Div(id='title-input',
                                            children=[html.Span('Text'),html.Span(' (Prefix <b>(bold),<i>(italic))',style={'fontSize':'12px'}),
                                                dcc.Input(id='title-input-text',value=title_text,type='text',style={'marginTop':'0.75rem','width':'100%'}),
                                                html.Hr()]),
                                        html.Div(id='title-fonsize',
                                            children=[html.P('FontSize'),
                                            dcc.Input(id='title-input-size',type='number',value=title_size,min=2,step=1,style={'width':'30%'}),
                                            html.Hr()]),
                                        html.Div(id='title-fontfamily',
                                            children=[html.P('FontFamily'),
                                            dcc.Dropdown(id='title-input-family',value=title_family,style={'width':'80%'},placeholder="Select a Font Family",
                                                        options=[{'label':tf,'value':tf} for tf in typefaces]
                                                        ),html.Hr()]),
                                        html.Div(id='title-fontcolor',style={'display':'flex','flexWrap':'wrap'},
                                            children=[html.Label('FontColor',style={'flexGrow':'9'}),html.Button('﹀',id='title-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                            daq.ColorPicker(id='title-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                value=dict(rgb=title_color)
                                            ),
                                            html.Div(id='title-color-picker-output')
                                            ]),
                                        html.Hr(),
                                        html.Div(id='title-position',
                                            children=[html.P('Horizontal Position'),
                                            dcc.Input(id='title-input-position',type='number',value=title_position,min=0,max=1,step=0.05,style={'width':'30%'}),
                                            html.Hr()])
                                            ]),
                                # -----------------------------
                                    html.Div(id='conf-traces',className='conf',style={'display':'none'},
                                        children=[
                                            html.Div(id='traces-title',
                                                children=['Traces']),
                                            html.Button('+ Trace',id="add-trace",style={'backgroundColor':'#0d76bf','color':'white'}),
                                            # html.Br(),
                                            html.Div(traces_children)
                                        ]),
                                # -----------------------------
                                    html.Div(id='conf-labels',className='conf',style={'display':'none'},
                                        children=[
                                            html.Div(id='labels-title',
                                                children=['Labels']),

                                            html.Div(id='xlabel',style ={'border':'1px solid black','borderRadius':'10px','padding':'10px','marginTop':'10px'},
                                                children=[
                                                    html.Label('X Label'),
                                                    html.Div(id='xlabel-input',
                                                        children=[html.Span('Text'),html.Span(' (Prefix <b>(bold),<i>(italic))',style={'fontSize':'12px'}),
                                                            dcc.Input(id='xlabel-input-text',value=xlabel_text,type='text',style={'marginTop':'0.75rem','width':'100%'}),
                                                            html.Hr()]),
                                                    html.Div(id='xlabel-fonsize',
                                                        children=[html.P('FontSize'),
                                                        dcc.Input(id='xlabel-input-size',type='number',value=label_size,min=2,step=1,style={'width':'30%'}),
                                                        html.Hr()]),
                                                    html.Div(id='xlabel-fontfamily',
                                                        children=[html.P('FontFamily'),
                                                        dcc.Dropdown(id='xlabel-input-family',value=label_family,style={'width':'80%'},placeholder="Select a Font Family",
                                                                    options=[{'label':tf,'value':tf} for tf in typefaces]
                                                                    ),html.Hr()]),
                                                    html.Div(id='xlabel-fontcolor',style={'display':'flex','flexWrap':'wrap'},
                                                        children=[html.Label('FontColor',style={'flexGrow':'9'}),html.Button('﹀',id='xlabel-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                                        daq.ColorPicker(id='xlabel-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                            value=dict(rgb=label_color)
                                                        ),
                                                        html.Div(id='xlabel-color-picker-output')
                                                        ]),
                                                    html.Hr()
                                                ]),

                                            html.Div(id='y1label',style ={'border':'1px solid black','borderRadius':'10px','padding':'10px','marginTop':'10px'},
                                                children=[
                                                    html.Label('Y1 Label'),
                                                    html.Div(id='y1label-input',
                                                        children=[html.Span('Text'),html.Span(' (Prefix <b>(bold),<i>(italic))',style={'fontSize':'12px'}),
                                                            dcc.Input(id='y1label-input-text',value=y1label_text,type='text',style={'marginTop':'0.75rem','width':'100%'}),
                                                            html.Hr()]),
                                                    html.Div(id='y1label-fonsize',
                                                        children=[html.P('FontSize'),
                                                        dcc.Input(id='y1label-input-size',type='number',value=label_size,min=2,step=1,style={'width':'30%'}),
                                                        html.Hr()]),
                                                    html.Div(id='y1label-fontfamily',
                                                        children=[html.P('FontFamily'),
                                                                dcc.Dropdown(id='y1label-input-family',value=label_family,style={'width':'80%'},placeholder="Select a Font Family",
                                                                    options=[{'label':tf,'value':tf} for tf in typefaces]),
                                                                html.Hr()]),
                                                    html.Div(id='y1label-fontcolor',style={'display':'flex','flexWrap':'wrap'},
                                                        children=[html.Label('FontColor',style={'flexGrow':'9'}),html.Button('﹀',id='y1label-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                                        daq.ColorPicker(id='y1label-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                            value=dict(rgb=label_color)
                                                        ),
                                                        html.Div(id='y1label-color-picker-output')
                                                        ]),
                                                    html.Hr()
                                                ]),
                                            html.Div(id='y2label',style ={'border':'1px solid black','borderRadius':'10px','padding':'10px','marginTop':'10px','display':'none'},
                                                children=[
                                                    html.Label('Y2 Label'),
                                                    html.Div(id='y2label-input',
                                                        children=[html.Span('Text'),html.Span(' (Prefix <b>(bold),<i>(italic))',style={'fontSize':'12px'}),
                                                            dcc.Input(id='y2label-input-text',value=y2label_text,type='text',style={'marginTop':'0.75rem','width':'100%'}),
                                                            html.Hr()]),
                                                    html.Div(id='y2label-fonsize',
                                                        children=[html.P('FontSize'),
                                                        dcc.Input(id='y2label-input-size',type='number',value=label_size,min=2,step=1,style={'width':'30%'}),
                                                        html.Hr()]),
                                                    html.Div(id='y2label-fontfamily',
                                                        children=[html.P('FontFamily'),
                                                        dcc.Dropdown(id='y2label-input-family',value=label_family,style={'width':'80%'},placeholder="Select a Font Family",
                                                                    options=[{'label':tf,'value':tf} for tf in typefaces]
                                                                    ),html.Hr()]),
                                                    html.Div(id='y2label-fontcolor',style={'display':'flex','flexWrap':'wrap'},
                                                        children=[html.Label('FontColor',style={'flexGrow':'9'}),html.Button('﹀',id='y2label-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                                        daq.ColorPicker(id='y2label-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                            value=dict(rgb=label_color)
                                                        ),
                                                        html.Div(id='y2label-color-picker-output')
                                                        ]),
                                                    html.Hr()
                                        ]),
                                            html.Div(id='y3label',style ={'border':'1px solid black','borderRadius':'10px','padding':'10px','marginTop':'10px','display':'none'},
                                                children=[
                                                    html.Label('Y3 Label'),
                                                    html.Div(id='y3label-input',
                                                        children=[html.Span('Text'),html.Span(' (Prefix <b>(bold),<i>(italic))',style={'fontSize':'12px'}),
                                                            dcc.Input(id='y3label-input-text',value=y3label_text,type='text',style={'marginTop':'0.75rem','width':'100%'}),
                                                            html.Hr()]),
                                                    html.Div(id='y3label-fonsize',
                                                        children=[html.P('FontSize'),
                                                        dcc.Input(id='y3label-input-size',type='number',value=label_size,min=2,step=1,style={'width':'30%'}),
                                                        html.Hr()]),
                                                    html.Div(id='y3label-fontfamily',
                                                        children=[html.P('FontFamily'),
                                                        dcc.Dropdown(id='y3label-input-family',value=label_family,style={'width':'80%'},placeholder="Select a Font Family",
                                                                    options=[{'label':tf,'value':tf} for tf in typefaces]
                                                                    ),html.Hr()]),
                                                    html.Div(id='y3label-fontcolor',style={'display':'flex','flexWrap':'wrap'},
                                                        children=[html.Label('FontColor',style={'flexGrow':'9'}),html.Button('﹀',id='y3label-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                                        daq.ColorPicker(id='y3label-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                            value=dict(rgb=label_color)
                                                        ),
                                                        html.Div(id='y3label-color-picker-output')
                                                        ]),
                                                    html.Hr()
                                        ])
                                    ]),
                                # -----------------------------
                                    html.Div(id='conf-figure',className="conf",style={'display':'none'},
                                        children=[
                                            html.Div(id='figure-title',
                                                children=['Figure']),

                                            html.Div(id='bg-color',style={'display':'flex','flexWrap':'wrap','marginTop':'10px'},
                                                children=[html.Label('Backround Color',style={'flexGrow':'9'}),html.Button('﹀',id='bg-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                                daq.ColorPicker(id='bg-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                    value=dict(rgb=bg_color)
                                                ),
                                                html.Div(id='bg-color-picker-output')
                                                ]),
                                            html.Hr()
                                        ]),
                                # -----------------------------
                                    html.Div(id='conf-grid',className="conf",style={'display':'none'},
                                    children=[
                                        html.Div(id='grid-title',
                                            children=['Grid']),

                                        html.Div(id='grid-show',
                                            children=[html.Label('Grid Show/Hide'),
                                            dcc.Dropdown(id='grid-input-show',value='Show',style={'width':'80%'},placeholder="Show or Hide",
                                                        options=[{'label':s,'value':s} for s in ['Show','Hide']]
                                            ),html.Hr()]),
                                        html.Div(id='grid-width',
                                            children=[html.Label('Line Width'),
                                            dcc.Input(id='grid-input-width',type='number',value=float(grid_width),min=1,step=1,style={'width':'30%'}),
                                            html.Hr()]),
                                        html.Div(id='grid-axes',
                                            children=[html.Label('Grid Axes'),
                                            dcc.Dropdown(id='grid-input-axes',value='Both',style={'width':'80%'},placeholder="Axes",
                                                        options=[{'label':a,'value':a} for a in ['Both','Xaxis','Yaxis']]
                                            ),html.Hr()]),
                                        html.Div(id='grid-color',style={'display':'flex','flexWrap':'wrap'},
                                            children=[html.Label('Color',style={'flexGrow':'9'}),html.Button('﹀',id='grid-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                            daq.ColorPicker(id='grid-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                value=dict(rgb=grid_color)
                                            ),
                                            html.Div(id='grid-color-picker-output')
                                            ])
                                        ]),
                                # -----------------------------
                                    html.Div(id='conf-legend',className="conf",style={'display':'none'},
                                    children=[
                                        html.Div(id='legend-title',
                                            children=['Legend']),

                                        html.Div(id='legend-show',
                                            children=[html.Label('Legend Show/Hide'),
                                            dcc.Dropdown(id='legend-input-show',value='Show',style={'width':'80%'},placeholder="Show or Hide",
                                                        options=[{'label':s,'value':s} for s in ['Show','Hide']]
                                            ),html.Hr()]),

                                        html.Div(id='legend-fontsize',
                                            children=[html.Label('FontSize'),
                                            dcc.Input(id='legend-input-size',type='number',value=legend_size,min=2,step=1,style={'width':'30%'}),
                                            html.Hr()]),

                                        html.Div(id='legend-fontfamily',
                                            children=[html.Label('FontFamily'),
                                            dcc.Dropdown(id='legend-input-family',value=legend_family,style={'width':'80%'},placeholder="Select a Font Family",
                                                        options=[{'label':tf,'value':tf} for tf in typefaces]
                                                        ),html.Hr()]),

                                        html.Div(id='legend-orientation',
                                            children=[html.Label('Orientation'),
                                            dcc.Dropdown(id='legend-input-orientation',value="Horizontal",style={'width':'80%'},placeholder="Legend Orientation",
                                                        options=[{'label':o,'value':o} for o in ['Horizontal','Vertical']]
                                                        ),html.Hr()]),

                                        html.Div(id='legend-fontcolor',style={'display':'flex','flexWrap':'wrap'},
                                            children=[html.Label('FontColor',style={'flexGrow':'9'}),html.Button('﹀',id='legendfont-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                            daq.ColorPicker(id='legendfont-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                value=dict(rgb=legendfont_color)
                                            ),
                                            html.Div(id='legendfont-color-picker-output')
                                            ]),
                                        html.Hr(),

                                        html.Div(id='legendbg-color',style={'display':'flex','flexWrap':'wrap'},
                                            children=[html.Label('Backround Color',style={'flexGrow':'9'}),html.Button('﹀',id='legendbg-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                            daq.ColorPicker(id='legendbg-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                value=dict(rgb=legendbg_color)
                                            ),
                                            html.Div(id='legendbg-color-picker-output')
                                            ]),
                                        html.Hr(),

                                        html.Div(id='legend-bordersize',
                                            children=[html.Label('BorderSize'),
                                            dcc.Input(id='legend-input-bordersize',type='number',value=legend_bordersize,min=0,step=1,style={'width':'30%'}),
                                            html.Hr()]),

                                        html.Div(id='legend-bordercolor',style={'display':'flex','flexWrap':'wrap'},
                                            children=[html.Label('Border Color',style={'flexGrow':'9'}),html.Button('﹀',id='legendborder-color-appear',n_clicks=0,style={'flexGrow':'1','height':'auto','lineHeight':'100%','padding':'0px'}),
                                            daq.ColorPicker(id='legendborder-color-picker',style={'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none','flexGrow':'10'},
                                                value=dict(rgb=legendborder_color)
                                            ),
                                            html.Div(id='legendborder-color-picker-output')
                                            ]),
                                        html.Hr(),

                                        html.Div(id='legend-hposition',
                                            children=[html.Label('Horizontal Position'),
                                            dcc.Input(id='legend-input-hposition',type='number',value=legend_hposition,min=0,max=1,step=0.05,style={'width':'30%'}),
                                            html.Hr()]),

                                        html.Div(id='legend-vposition',
                                            children=[html.P('Vertical Position'),
                                            dcc.Input(id='legend-input-vposition',type='number',value=legend_vposition,min=-0.2,max=1.5,step=0.05,style={'width':'30%'}),
                                            html.Hr()])


                                        ])

                            ])
                            ])
                            ]),
            #Left Panel

            # Right Panel

            html.Div(id="right-panel",
                style={
                    'flex':'1 1 75%',
                    'display':'flex',
                    'flexDirection':'column',
                    'maxWidth':'75%',
                    'backgroundColor':'#fff7000d'
                },
                children=[
                # Output -Table
                    html.Div(id='output-data-upload',
                    style={
                        'minWidth':'100%',
                        'minHeight': '25%',
                        'marginBottom':'5%',
                        'flex':'1 1 25%'
                    }),
                # ------------------------

                # Output -Plot

                    dcc.Graph(id='example-graph',

                        responsive=True,
                        style={
                            'width':'100%',
                            'flex':'1 1 70%'
                        },

                        figure=fig
                        )
                # ------------------------

                ])
                # ------------------------
        ])

    init_callbacks(dash_app,traces_children)

    return dash_app.server


def init_callbacks(dash_app,traces_children):

    def get_data_from_csv(data_csv):
        # try:
        data=pd.read_csv(io.StringIO(data_csv),sep=" ")

        if data.columns[0]!='TIME':
            data_csv=data_csv.replace(" ","_")
            data_csv=data_csv.replace(","," ")
            data=pd.read_csv(io.StringIO(data_csv),sep=" ")

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

        data_cp = data.set_index('TIME')
        time=data['TIME']
        new_days_ind = None
        try:
            new_days_ind = data_cp.index.get_loc("1900-01-01 00:00:00")
        except:
            pass
        time_new = time.copy()
        if new_days_ind:
            if len(new_days_ind)==1:
                time_new[time_new.index>=new_days_ind[0]]=time[time.index>=new_days_ind[0]]+datetime.timedelta(days=1)
            else:
                for i in range(len(new_days_ind)-1):
                    time_new[(time_new.index>=new_days_ind[i])&(time_new.index<new_days_ind[i+1])]=time[(time.index>=new_days_ind[i])&(time.index<new_days_ind[i+1])]+datetime.timedelta(days=i+1)
                    time_new[(time_new.index>=new_days_ind[i+1])]=time[(time.index>=new_days_ind[i+1])]+datetime.timedelta(days=i+2)
        data['TIME']=time_new

        return data
        # except FileNotFoundError as e:
        #     print(e)
        #     return e

    def parse_contents(contents, filename, date):
        content_type, content_string = contents.split(',')


        try:
            if 'csv' in filename:
                decoded = base64.b64decode(content_string).decode('utf-8')
                # Assume that the user uploaded a CSV file
                df = get_data_from_csv(decoded)
            elif 'xls' in filename:
                decoded = base64.b64decode(content_string)
                # print(decoded)
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return html.Div([

            dash_table.DataTable(
                id='data-table',
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                filter_action="native",
                style_table={
                'maxHeight': '200px',
                'overflowY': 'scroll'
                },
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'black',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                css = [{'selector':'input.current-page','rule':'width:40px;'}]
            )
        ])

    @dash_app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])




    def update_output(list_of_contents, list_of_names, list_of_dates):
        import string
        # print(list_of_contents)
        if list_of_contents is not None:
            children = [
                parse_contents(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)]
            return children
        else:
            params = list(string.ascii_uppercase)
            children =[
                dash_table.DataTable(
                id = 'data-table',
                columns=(
                    [{'id': p, 'name': p} for p in params]
                ),
                data=[
                    dict(Model=i, **{param: 0 for param in params})
                    for i in range(1, 1000)
                ],
                editable = True,
                filter_action = 'native',
                page_action = 'native',
                style_table={
                'maxHeight': '200px',
                'overflowY': 'scroll'
                },
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'black',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                css = [{'selector':'input.current-page','rule':'width:40px;'}]
                )
            ]
            return children
# ----------------------------------------------------------------------------------------

    @dash_app.callback([Output('conf-title','style'),
                        Output('conf-traces','style'),
                        Output('conf-labels','style'),
                        Output('conf-legend','style'),
                        Output('conf-figure','style'),
                        Output('conf-grid','style')],
                        [Input('Title','n_clicks'),
                        Input('Traces','n_clicks'),
                        Input('Labels','n_clicks'),
                        Input('Legend','n_clicks'),
                        Input('Figure','n_clicks'),
                        Input('Grid','n_clicks'),
                        Input('Axes','n_clicks'),
                        Input('Annotate','n_clicks')])

    def update_conf(btn_title,btn_traces,btn_labels,btn_legend,btn_figure,btn_grid,btn_axes,btn_annotate):
        global typefaces

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        btn_pr =  [p['value'] for p in dash.callback_context.triggered][0]

        if ('Title' in changed_id):
            return {'display':'block'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'}
        elif ('Traces' in changed_id):
            return {'display':'none'},{'display':'block'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'}
        elif ('Labels' in changed_id):
            return {'display':'none'},{'display':'none'},{'display':'block'},{'display':'none'},{'display':'none'},{'display':'none'}
        elif ('Legend' in changed_id):
            return {'display':'none'},{'display':'none'},{'display':'none'},{'display':'block'},{'display':'none'},{'display':'none'}
        elif ('Figure' in changed_id):
            return {'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'block'},{'display':'none'}
        elif ('Grid' in changed_id):
            return {'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'block'}
        else:
            return {'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'},{'display':'none'}

 # ----------------------------------------------------------------------------------------

    @dash_app.callback([Output('title-color-picker','style'),
                        Output('xlabel-color-picker','style'),
                        Output('y1label-color-picker','style'),
                        Output('y2label-color-picker','style'),
                        Output('y3label-color-picker','style'),
                        Output('bg-color-picker','style'),
                        Output('grid-color-picker','style'),
                        Output('legendfont-color-picker','style'),
                        Output('legendbg-color-picker','style'),
                        Output('legendborder-color-picker','style')]+
                        [Output('trace-color-picker'+str(i),'style') for i in range(0,len(traces_children))],
                        [Input('title-color-appear','n_clicks'),
                        Input('xlabel-color-appear','n_clicks'),
                        Input('y1label-color-appear','n_clicks'),
                        Input('y2label-color-appear','n_clicks'),
                        Input('y3label-color-appear','n_clicks'),
                        Input('bg-color-appear','n_clicks'),
                        Input('grid-color-appear','n_clicks'),
                        Input('legendfont-color-appear','n_clicks'),
                        Input('legendbg-color-appear','n_clicks'),
                        Input('legendborder-color-appear','n_clicks')]+
                        [Input('trace-color-appear'+str(i),'n_clicks') for i in range(0,len(traces_children))])

    def show_color(title_clr_btn,x_clr_btn,y1_clr_btn,y2_clr_btn,y3_clr_btn,bg_clr_btn,grid_clr_btn,lgdfont_clr_btn,lgdbg_clr_btn,lgdborder_clr_btn,*args):

        block = {'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'block'}
        nonblock = {'width':'100%','border':'none','backgroundColor':'#ebf0f8','display':'none'}

        if (title_clr_btn) & (title_clr_btn > 0):
            if (title_clr_btn%2 == 1):
                title =  block
            else:
                title = nonblock
        else:
            title = nonblock

        if (x_clr_btn) & (x_clr_btn > 0):
            if (x_clr_btn%2 == 1):
                x =  block
            else:
                x = nonblock
        else:
            x = nonblock

        if (y1_clr_btn) & (y1_clr_btn > 0):
            if (y1_clr_btn%2 == 1):
                y1 =  block
            else:
                y1 = nonblock
        else:
            y1 = nonblock

        if (y2_clr_btn) & (y2_clr_btn > 0):
            if (y2_clr_btn%2 == 1):
                y2 =  block
            else:
                y2 = nonblock
        else:
            y2 = nonblock

        if (y3_clr_btn) & (y3_clr_btn > 0):
            if (y3_clr_btn%2 == 1):
                y3 =  block
            else:
                y3 = nonblock
        else:
            y3 = nonblock

        if (bg_clr_btn) & (bg_clr_btn > 0):
            if (bg_clr_btn%2 == 1):
                bg =  block
            else:
                bg = nonblock
        else:
            bg = nonblock

        if (grid_clr_btn) & (grid_clr_btn > 0):
            if (grid_clr_btn%2 == 1):
                grid =  block
            else:
                grid = nonblock
        else:
            grid = nonblock

        if (lgdfont_clr_btn) & (lgdfont_clr_btn > 0):
            if (lgdfont_clr_btn%2 == 1):
                lfont =  block
            else:
                lfont = nonblock
        else:
            lfont = nonblock

        if (lgdbg_clr_btn) & (lgdbg_clr_btn > 0):
            if (lgdbg_clr_btn%2 == 1):
                lbg =  block
            else:
                lbg = nonblock
        else:
            lbg = nonblock

        if (lgdborder_clr_btn) & (lgdborder_clr_btn > 0):
            if (lgdborder_clr_btn%2 == 1):
                lbord =  block
            else:
                lbord = nonblock
        else:
            lbord = nonblock

        tr_colors=[]
        for arg in args:
            if (arg) & (arg>0):
                if (arg%2 == 1):
                    tr =  block
                    tr_colors.append(tr)
                else:
                    tr = nonblock
                    tr_colors.append(tr)
            else:
                tr = nonblock
                tr_colors.append(tr)

        # print(tr_colors)
        return [title]+[x]+[y1]+[y2]+[y3]+[bg]+[grid]+[lfont]+[lbg]+[lbord]+[tr for tr in tr_colors]



 # ----------------------------------------------------------------------------------------


    @dash_app.callback([Output('new-trace-'+str(i),'style') for i in range(0,len(traces_children))]+
                        [Output('trace-comp-'+str(i),'style') for i in range(0,len(traces_children))]+
                        [Output('xtrace-input-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Output('ytrace-input-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Output('yaxis-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Output('trace-input-width'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Output('trace-input-type'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Output('trace-input-deadband'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Output('trace-input-text'+str(i),'value') for i in range(0,len(traces_children))],
                        [Input('add-trace','n_clicks'),Input('upload-data', 'contents')]+
                        [Input('trace-appear-'+str(i),'n_clicks') for i in range(0,len(traces_children))]+
                        [Input('close-trace-'+str(i),'n_clicks')for i in range(0,len(traces_children))],
                        [State('new-trace-'+str(i),'style')for i in range(0,len(traces_children))]+
                        [State('xtrace-input-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [State('ytrace-input-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [State('yaxis-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [State('trace-input-width'+str(i),'value') for i in range(0,len(traces_children))]+
                        [State('trace-input-type'+str(i),'value') for i in range(0,len(traces_children))]+
                        [State('trace-input-deadband'+str(i),'value') for i in range(0,len(traces_children))]+
                        [State('trace-input-text'+str(i),'value') for i in range(0,len(traces_children))]+
                        [State('trace-comp-'+str(i),'style')for i in range(0,len(traces_children))])

    def add_trace(add,contents,*args):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        btn_pr =  [p['value'] for p in dash.callback_context.triggered][0]

        traces = len(traces_children)


        displays = list(args[2*traces:3*traces])
        x_states = list(args[3*traces:4*traces])
        y_states = list(args[4*traces:5*traces])
        yaxis_states = list(args[5*traces:6*traces])
        width_states = list(args[6*traces:+7*traces])
        type_states = list(args[7*traces:8*traces])
        dead_states = list(args[8*traces:9*traces])
        name_states = list(args[9*traces:10*traces])
        displays_comp = list(args[10*traces:])

        if (add > 0):
            if ('add-trace' in changed_id):
                for display in displays:
                    if display['display'] == 'none':
                        display['display'] = 'block'
                        break
                return displays+displays_comp+x_states+y_states+yaxis_states+width_states+type_states+dead_states+name_states
            elif ('upload-data' in changed_id):
                displays = [{'marginTop':'10px','display':'none'}]*traces
                x_states = [""]*traces
                y_states = [""]*traces
                yaxis_states = [""]*traces
                width_states = [2]*traces
                type_states = ["lines"]*traces
                dead_states = [0]*traces
                name_states = [""]*traces
                return displays+displays_comp+x_states+y_states+yaxis_states+width_states+type_states+dead_states+name_states
            elif ('close-trace' in changed_id):
                x_btn = changed_id.split('.')[0].split('-')[2]
                displays[int(x_btn)]={'marginTop':'10px','display':'none'}
                x_states[int(x_btn)]=""
                y_states[int(x_btn)]=""
                yaxis_states[int(x_btn)]=""
                width_states[int(x_btn)] = 2
                type_states[int(x_btn)] = 'lines'
                dead_states[int(x_btn)] = 0
                name_states[int(x_btn)] = ""
                return displays+displays_comp+x_states+y_states+yaxis_states+width_states+type_states+dead_states+name_states
            elif ('trace-appear' in changed_id):
                toggle_btn = changed_id.split('.')[0].split('-')[2]
                if (args[int(toggle_btn)]%2 == 1):
                    displays_comp[int(toggle_btn)]={'padding':'0 10px 0 10px','display':'block','backgroundColor':'white','border':'1px solid grey','borderRadius':'5px'}
                else:
                    displays_comp[int(toggle_btn)]={'padding':'0 10px 0 10px','display':'none','backgroundColor':'white','border':'1px solid grey','borderRadius':'5px'}
                return displays+displays_comp+x_states+y_states+yaxis_states+width_states+type_states+dead_states+name_states
        else:

            return [{'marginTop':'10px','display':'none'}]*traces+[{'padding':'0 10px 0 10px','display':'none','backgroundColor':'white','border':'1px solid grey','borderRadius':'5px'}]*traces+3*traces*[""]+traces*[1]+traces*['lines']+traces*[0]+traces*[""]

# ----------------------------------------------------------------------------------------

    @dash_app.callback([Output('y2label','style')]+
                        [Output('y3label','style')],
                        [Input('yaxis-select-'+str(i),'value') for i in range(0,len(traces_children))])

    def add_y(*args):
        block = {'border':'1px solid black','borderRadius':'10px','padding':'10px','marginTop':'10px','display':'block'}
        nonblock = {'border':'1px solid black','borderRadius':'10px','padding':'10px','marginTop':'10px','display':'none'}

        print(args)

        if ('Y2') in args:
            style_y2 = block
        else:
            style_y2 = nonblock

        if ('Y3') in args:
            style_y3 = block
        else:
            style_y3 = nonblock

        return (style_y2,style_y3)

# ----------------------------------------------------------------------------------------

    @dash_app.callback([Output('xtrace-input-select-'+str(i),'options') for i in range(0,len(traces_children))]+
                        [Output('ytrace-input-select-'+str(i),'options') for i in range(0,len(traces_children))],
                        [Input('data-table','columns')])

    def traces_select(cols):



        try:
            x_options = [[{'label':e['name'],'value':e['name']} for e in cols]]*len(traces_children)
            y_options = [[{'label':e['name'],'value':e['name']} for e in cols]]*len(traces_children)

            return x_options+y_options
        except:
            return [None]*len(traces_children)*2

# # ----------------------------------------------------------------------------------------
    axes =["x","y1","y2","y3"]
    atrs =["input-text","input-size","input-family","color-picker"]

    @dash_app.callback(Output('example-graph','figure'),
                        [Input('title-input-text','value'),
                        Input('title-input-size','value'),
                        Input('title-input-position','value'),
                        Input('title-input-family','value'),
                        Input('title-color-picker', 'value'),
                        Input('bg-color-picker', 'value'),
                        Input('grid-color-picker', 'value'),
                        Input('grid-input-width', 'value'),
                        Input('grid-input-show', 'value'),
                        Input('grid-input-axes', 'value'),
                        Input('legend-input-size', 'value'),
                        Input('legend-input-family', 'value'),
                        Input('legendfont-color-picker', 'value'),
                        Input('legendbg-color-picker', 'value'),
                        Input('legendborder-color-picker', 'value'),
                        Input('legend-input-show', 'value'),
                        Input('legend-input-bordersize', 'value'),
                        Input('legend-input-vposition', 'value'),
                        Input('legend-input-hposition', 'value'),
                        Input('legend-input-orientation', 'value')]+
                        [Input(ax+'label-'+atr,'value') for ax in axes for atr in atrs]+
                        [Input('y2label','style')]+
                        [Input('y3label','style')]+
                        [Input('data-table','data')]+
                        [Input('xtrace-input-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Input('ytrace-input-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Input('yaxis-select-'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Input('trace-color-picker'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Input('trace-input-width'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Input('trace-input-type'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Input('trace-input-deadband'+str(i),'value') for i in range(0,len(traces_children))]+
                        [Input('trace-input-text'+str(i),'value') for i in range(0,len(traces_children))],
                        [State('example-graph','figure')])

    def update_graph(title_text,title_size,title_position,title_family,title_color,bg_color,
            grid_color,grid_width,grid_show,grid_axes,legend_size,legend_family,legendfont_color,legendbg_color,legendborder_color,legend_show,legend_bordersize,legend_vposition,legend_hposition,legend_or,
            xlabel_text,xlabel_size,xlabel_family,xlabel_color,
            y1label_text,y1label_size,y1label_family,y1label_color,
            y2label_text,y2label_size,y2label_family,y2label_color,
            y3label_text,y3label_size,y3label_family,y3label_color,
            y2label_style,
            y3label_style,
            data,*args):


        ysels=args[30:45]
        line_colors=args[45:60]
        line_widths=args[60:75]
        line_types=args[75:90]
        line_deads=args[90:105]
        names = args[105:120]

        figure = args[120]
        # print(figure['layout'])

        yaxes=[]
        for yaxis in ysels:
            try:
                y=yaxis.split('Y')[1]
                yaxes.append(y)
            except:
                yaxes.append(yaxis)

        print(yaxes)

        xytraces = list(zip(args[0:15],args[15:30],yaxes,line_colors,line_widths,line_types,line_deads,args[105:]))

        data = pd.DataFrame(data)
        traces = []

        if grid_axes == "Both":
            visible_x = True
            visible_y = True
        elif grid_axes == "Xaxis":
            visible_x = True
            visible_y = False
        else:
            visible_x = False
            visible_y = True

        if grid_show == "Hide":
            visible_x = False
            visible_y = False

        if legend_show == "Show":
            lgd_show = True
        else:
            lgd_show = False

        if legend_or == "Horizontal":
            orientation = "h"
        else:
            orientation = "v"


        layout = {
                    "title":{"text":title_text,"x":title_position,"font":{"size":title_size,"family":title_family,"color":title_color['rgb']}},
                    "xaxis":{"title":{"text":xlabel_text,"font":{"size":xlabel_size,"family":xlabel_family,"color":xlabel_color['rgb']}},'gridcolor':grid_color['rgb'],'gridwidth':float(grid_width),'zeroline':False,'showgrid':visible_x,
                        'tickangle':90,'tickformat':"","domain": [0,1],'tickprefix':'<b>'
                        },
                    "yaxis":{"title":{"text":y1label_text,"font":{"size":y1label_size,"family":y1label_family,"color":y1label_color['rgb']}},
                            'gridcolor':grid_color['rgb'],'gridwidth':float(grid_width),'zeroline':False,'showgrid':visible_y,
                            'tickprefix':'<b>'},
                    "showlegend":lgd_show,
                    "legend":{"orientation":orientation,"xanchor":'auto',"yanchor":'auto',"x":legend_hposition,"y":legend_vposition,"autosize":True,"bgcolor":legendbg_color['rgb'],"borderwidth":legend_bordersize,"bordercolor":legendborder_color['rgb'],
                        "font":{"family":legend_family,"size":legend_size,"color":legendfont_color['rgb']}},
                    "plot_bgcolor":bg_color['rgb'],
                    "uirevision":data[data.columns[0]][0]
                }


        for x,y,yaxis,color,width,type,dead,name in xytraces:
            if x and y and yaxis and color and width:

                try:
                    data[x] = [el.split('T')[1] for el in data[x]]
                except:
                    pass
                r = color['rgb']['r']
                g = color['rgb']['g']
                b = color['rgb']['b']
                a = color['rgb']['a']

                dead_color = color['rgb']
                dead_color['a']= color['rgb']['a']/3
                if dead == 0:
                    visible=False
                    error_y={}
                else:
                    visible=True
                    error_y={'visibile':visible,'type':'constant','symmetric':True,'value':dead,'color':dead_color,'width':0,'thickness':1}

                traces.append(dict(x=data[x],y=data[y],mode="lines",type="scatter",xaxis="x",yaxis="y"+yaxis,name=name,error_y=error_y,opacity=1,line={'color':'rgba({},{},{},{})'.format(r,g,b,a),'width':width,'simplify':False,'dash':type}))

                if yaxis == "3":
                    side = 'left'
                    layout['yaxis'+yaxis] ={'side':side,'overlaying':'y1','anchor':"free","title":{"text":y3label_text,"font":{"size":y3label_size,"family":y3label_family,"color":y3label_color['rgb']}},
                                            'gridcolor':grid_color['rgb'],'gridwidth':0,'zeroline':False,'showgrid':False,'position':0,'tickprefix':'<b>'}
                    layout['xaxis']['domain'] = [0.06,1]
                elif yaxis == "2":
                    side = 'right'
                    layout['yaxis'+yaxis] ={'side':side,'anchor':"x",'overlaying':'y1',"title":{"text":y2label_text,"font":{"size":y2label_size,"family":y2label_family,"color":y2label_color['rgb']}},
                                            'gridcolor':grid_color['rgb'],'gridwidth':0,'zeroline':False,'showgrid':False,'tickprefix':'<b>'}


        print(figure['layout'])

        if not traces:
            traces.append(dict(x=[],y=[],mode="lines"))

        return {"data": traces,
                "layout":layout}
