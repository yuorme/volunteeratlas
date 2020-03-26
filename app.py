#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

import pickle
import os
import json

import pygsheets

import folium
from folium.plugins import LocateControl, MarkerCluster

import dash
import dash_core_components as dcc
import dash_html_components as html

#initialize app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
# gc = pygsheets.authorize(service_file='volunteeratlas-service.json') #hack (local): windows env double quotes issue
gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS') #web

def get_sheets_df(gc, sheet_id):
    '''get and process google sheets into a dataframe
    '''

    sh = gc.open_by_key(sheet_id) #TODO: hide ID as env var
    df = sh.sheet1.get_as_df()

    #process df
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Radius'] = df['Radius'].str.replace('km','').astype(float)

    df['Latitude'] = df['Latitude'].replace('', np.nan, regex=False) \
        .astype(float)
    df['Longtitude'] = df['Longtitude'].replace('', np.nan, regex=False) \
        .astype(float) 
    
    start_index=100000
    df['VID'] = list(range(start_index, start_index+len(df)))

    return df

def build_folium_map(df, jitter=0.005):
    
    def get_popup_html(row):
        '''Builds a folium HTML popup to display in folium marker objects
        row (pandas Series): row from the google sheets dataframe
        '''
        email_subject = f"Delivery%20Request%20for%20{row['Given Name']}"
        va_email = 'volunteers.atlas@gmail.com'
        
        return folium.Popup(
            f"<b>Name:</b> {row['Given Name']} <br>" +  
            f"<b>Country:</b> {row['Country']} <br>" +
            f"<b>City:</b> {row['City/Town']} <br>" +
#             f"<b>Neighborhood:</b> {row['Neighborhood']} <br>" + #get from geocode
            f"<b>Transportation:</b> {row['Mode of Transportation']} <br>" +
            f"<b>Services:</b> {row['Type of Services']} <br>" +
            f"<b>Radius:</b> {int(row['Radius'])} km <br>" +
            f"<b>Day of Week:</b> {row['Preferred Day of Week']} <br>" +
            f"<b>Time of Day:</b> {row['Preferred Time of Day']} <br>" +
            f"<b>Languages:</b> {row['Languages Spoken']} <br>" +
            f"<b>Payment:</b> {row['Reimbursement Method']} <br>" +
            f"<b>About Me:</b> {row['About Me']} <br>" +
            f"<a href='mailto:{row['Email Address']}?cc={va_email}&Subject={email_subject}' target='_blank'>Contact {row['Given Name']}</a>  <br>"
            , max_width = 200
            )
    
    dff = df.dropna(axis=0, how='any', subset=['Latitude','Longtitude'])
    dff = dff.loc[(dff.Health == 'Yes') & (dff.Availability == 'Yes')]
    dff['Latitude'] = dff['Latitude'].apply(lambda x: x+np.random.uniform(-jitter,jitter)) 
    dff['Longtitude'] = dff['Longtitude'].apply(lambda x: x+np.random.uniform(-jitter,jitter))
    
    #build map
    m = folium.Map(
        location=[53.981843, -97.564298], #Canada
        tiles='Stamen Terrain',
        zoom_start=4,
        control_scale=True
    )

    #add marker cluster
    mc = MarkerCluster(
        name='Volunteers', 
        control=True,
        overlay=True,
        showCoverageOnHover=False
    )

    #add circle markers
    for idx, row in dff.iterrows():
        mc.add_child(
            folium.Circle(
#                 radius=row['Radius']*250,
                radius=400,
                location=[row['Latitude'], row['Longtitude']],
                popup=get_popup_html(row),
                color='#00d700',
                fill=True,
                fill_color='#00d700'
            )
        ).add_to(m)

    #add layer control
    folium.LayerControl(
        collapsed=True
    ).add_to(m)

    #add location control
    LocateControl(
        flyTo=True, 
        keepCurrentZoomLevel=False,
        showPopup=True,
        returnToPrevBounds=True,
        locateOptions=dict(maxZoom=13)
    ).add_to(m)

    m.save('index.html')
    
    return m._repr_html_()

df = get_sheets_df(gc, '16EcK3wX-bHfLpL3cj36j49PRYKl_pOp60IniREAbEB4') #TODO: hide sheetname

app.layout = html.Div(children=[
    html.H1('Volunteer Atlas'),
    html.Iframe(id='folium-map', srcDoc=build_folium_map(df), style=dict(width='100%', height=1000, overflow='hidden')), #DEBUG: Fix IFrame y-scroll bar
    html.A('Code on Github', href='https://github.com/yuorme/volunteeratlas'),
])

if __name__ == '__main__':
    app.run_server(debug=True, port= 5000)


