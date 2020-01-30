# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 08:46:19 2020

@author: ttb
"""

#%%
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
#import base64
#from datetime import datetime, timedelta
#import os
import pathlib
import plotly.graph_objs as go
import pandas as pd
#import numpy as np
#import json

#%%    
    
# get relative data folder
PATH = pathlib.Path(__file__)#.parent
#PATH = os.chdir("C:\\Users\\ttb\\Desktop\\projects\\python\\app\\data")
#PATH = os.chdir("C:\\Users\\ttb\\Desktop\\projects\\git\\adic_dash\\data")
DATA_PATH = PATH.joinpath("../data").resolve()

#df_current_prices = pd.read_csv("User Interface Exercise.csv")
df_current_prices = pd.read_csv(DATA_PATH.joinpath("User Interface Exercise.csv"))
df_current_prices = df_current_prices.drop(df_current_prices.columns[0],axis=1)

df_current_prices = df_current_prices.set_index("Dates")
df_current_prices.index = pd.DatetimeIndex(df_current_prices.index)

index_name = ["S&P 500", "Euro STOXX","TOPIX"]

returns = df_current_prices[df_current_prices.columns[:3]]
returns.columns = index_name

bar_notes = df_current_prices[df_current_prices.columns[3:]].copy()
bar_notes.columns = index_name

notes = df_current_prices[df_current_prices.columns[3:]].copy()
notes.columns = index_name
notes.loc[notes.index,"year"] = notes.index.year.tolist()
notes.loc[notes.index,"month"] = notes.index.month.tolist()
notes = notes.reset_index()
notes = notes.drop('Dates',axis=1)
notes = notes.set_index(['year','month'])


################################################
# APP START
    
app = dash.Dash('ADIC')


app.layout = html.Div([
    html.Div([
        html.Div([
                html.Img(src=app.get_asset_url("ADICcl.jpg"),width=250),
                ],className="two columns"),

        html.Div([
                html.H5("Select Index"),
                
                ],className="two columns"),

        html.Div([
                dcc.Dropdown(
                        id='dropdown_menu',
                        options=[{'label':index_name[i], 'value':index_name[i] } for i in range(len(index_name))],    
                        value=index_name[0])                        
                ],className="two columns"),

        html.Div([
                html.H5("Search Comentary"),
            
            ],className="two columns"),
            
        html.Div([
                dcc.Input(id="search_input", type="text", placeholder="search"),
                html.H6("Please use the following format: Index Mmm-YY e.g. S&P 500 Jan-14")
            
                ],className="two columns"),

        html.Div([
                html.H5(" "),
                
                ],className="two columns"),

        ],className="row"),


    html.Div([
            html.Div([
                    dcc.Graph(id="return-tbl", config={'displayModeBar': False}),
                    html.Table(id='table_perf',style={"margin-bottom": "0px","margin-top": "0px"})
                    ],className="six columns"),

            html.Div([
                    html.H4('Results'),
                    html.Div(id="output"),
                    ],className="six columns"),
            
            ],className="row")
])


    
### create bar plot displaying the 1, 3, 5 year return
@app.callback(Output('return-tbl', 'figure'),[Input('dropdown_menu', 'value')])
def update_return_tbl(value):
    
    
    returns_idx = returns[value]
    
    #returns_idx.loc[returns_idx.index >= str(returns_idx.index.year[-1])+'-01-01' ]
    
    figure={
        "data": [
            go.Bar(
                x=returns_idx.index,
                y= returns_idx.round(2),
                marker={
                    "color": "#6161FF",
                    "line": {
                        "color": "rgb(255, 255, 255)",
                        "width": 2,
                    },
                },
                name=value,
                hovertext=bar_notes[value].tolist(),
            ),

        ],
        "layout": go.Layout(
            autosize=False,
            bargap=0,#.35
            font={"family": "Raleway", "size": 10},
            #height=200,
            hovermode="closest",
            legend={
                "x": -0.0228945952895,
                "y": -0.189563896463,
                "orientation": "h",
                "yanchor": "top",
            },
            margin={
                "r": 0,
                "t": 20,
                "b": 10,
                "l": 20,
            },
            showlegend=True,
            title="",
            #width=330,
            xaxis={
                "autorange": True,
                #"range": [-0.5, 4.5],
                "showline": True,
                "title": "",
                "type": "date",
            },
            yaxis={
                "autorange": True,
                #"range": [returns_idx.min*0.9, returns_idx.max*1.1],
                "showgrid": True,
                "showline": True,
                "title": "",
                "type": "linear",
                "zeroline": False,
            },
        ),
    }

    return figure


@app.callback(Output('table_perf', 'children'), [Input('dropdown_menu', 'value')])
def update_table2(value):


    returns_idx = returns[value]

    m1 = returns_idx[-1]
    m3 = ((1+returns_idx[-3:]/100).cumprod()[-1]-1)*100
    m6 = ((1+returns_idx[-6:]/100).cumprod()[-1]-1)*100
    y1 = ((1+returns_idx[-12:]/100).cumprod()[-1]-1)*100
    y3 = ((1+returns_idx[-3*12:]/100).cumprod()[-1]-1)*100
    y5 = ((1+returns_idx[-5*12:]/100).cumprod()[-1]-1)*100
    
    return_periods = pd.Series({"1 Month":m1,
                               "3 Month":m3,
                               "6 Month":m6,
                               "1 Year":y1,
                               "3 Year":y3,
                               "5 Year":y5
                            }).round(2)
    
    out_df = return_periods.to_frame(value).T

    out_df = out_df.reset_index()
    out_df.columns = ["Index"] + out_df.columns[1:].tolist()
    
    data = out_df.to_dict('rows')
    columns =  [{"name": i, "id": i,} for i in (out_df.columns)]
    
    # create datatable 
    table = dt.DataTable(data=data, columns=columns, style_cell={'fontSize':14, 'font-family':'sans-serif'} ) 
    
    return table
    
    

@app.callback(
    Output("output", "children"),
    [Input("search_input", "value")],
)
def update_output(input1):
    
    month_conv = pd.Series([1,2,3,4,5,6,7,8,9,10,11,12],index=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    
    
    if input1 is None:
        search_out = " "
        
    if input1 is not None:    
        # date
        date = input1[-6:]
    
        # index name
        idx = input1[:-7]
        
        # try and search for notes
        try:
            search_out = notes.loc[(float('20'+date[4:]),month_conv[date[:3]] ) , idx]    
        except:
            search_out = " "

    return search_out


server = app.server
app.title="ADIC"

if __name__ == '__main__':
    app.run_server()

    # Open browser and go to
    # http://127.0.0.1:8050/
    # or
    # http://127.0.0.1:5000/
