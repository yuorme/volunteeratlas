#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import folium
from folium.plugins import LocateControl, MarkerCluster

import dash
import dash_core_components as dcc
import dash_html_components as html

#initialize app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

def get_google_sheet(spreadsheet_id, range_name):
    """Shows basic usage of the Sheets API.
    spreadsheet_id (string): google sheets id 
    range_name (string): sheetname and range 
    """
    
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        sys.exit()
    
    return process_sheets_df(result)

def process_sheets_df(result):
    '''process google sheets json into a dataframe
    result (dict): Object returned by get_google_sheet function
    '''

    df = pd.DataFrame(data=result['values'][1:], columns=result['values'][0])

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
            f"<b>Payment:</b> {row['Payment Method']} <br>" +
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

    # m.save('index.html')
    print(type(m))
    
    return m._repr_html_()


df = get_google_sheet('16EcK3wX-bHfLpL3cj36j49PRYKl_pOp60IniREAbEB4', 'Form Responses 1!A1:Z10000000')

app.layout = html.Div(children=[
    html.H1('Volunteer Atlas'),
    html.Iframe(id='map', srcDoc=build_folium_map(df), width='100%', height=1000),
    html.A('Code on Github', href='https://github.com/yuorme/volunteeratlas'),
])

if __name__ == '__main__':
    app.run_server(debug=True, port= 5000)