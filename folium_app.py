#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import folium
from folium.plugins import LocateControl, MarkerCluster


# In[2]:


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
    
    return result


# In[3]:


def get_popup_html(row):
    '''Builds an HTML popup to display in folium marker objects
    row (pandas Series): row from the google sheets dataframe
    '''
    return folium.Popup(
        f"<b>Name:</b> <a href='{row['Facebook Profile Link']}' target='_blank'>{row['Given Name']} {row['Family Name']}</a> <br>" +  
        f"<b>Country:</b> {row['Country']} <br>" +
        f"<b>City:</b> {row['City/Town']} <br>" +
        f"<b>Area:</b> {row['Neighborhood']} <br>" +
        f"<b>Availability:</b> {row['Preferred Day of Week']} <br>" +
        f"<b>Languages:</b> {row['Languages Spoken']} <br>" +
        f"<b>Payment:</b> {row['Payment Method']} <br>" +
        f"<b>Email:</b> <a href='mailto:{row['Email Address']}' target='_blank'>{row['Email Address']}</a> <br>" 
        , max_width = 200
    ) 


# In[17]:


result = get_google_sheet('16EcK3wX-bHfLpL3cj36j49PRYKl_pOp60IniREAbEB4', 'Form Responses 1!A1:R10000000')

df = pd.DataFrame(data=result['values'][1:], columns=result['values'][0])

#process df
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['Radius'] = df['Radius'].str.replace('km','').astype(float)*10

jitter = 0.002 #jitter lat/lon by ~200m
df['GPS Latitude'] = df['GPS Latitude'].astype(float) + np.random.uniform(-jitter, jitter)
df['GPS Longtitude'] = df['GPS Longtitude'].astype(float) + np.random.uniform(-jitter, jitter)


#build map
m = folium.Map(
    location=[45.53, -73.58],
    tiles='Stamen Terrain',
    zoom_start=12,
    control_scale=True
)

#add marker cluster
mc = MarkerCluster(
    name='Volunteers', 
    control=True)

#add circle markers
for idx, row in df.iterrows():
    mc.add_child(
        folium.Circle(
            radius=row['Radius'],
            location=[row['GPS Latitude'], row['GPS Longtitude']],
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
    keepCurrentZoomLevel=True,
    showPopup=True
).add_to(m)

m.save('index.html')


# In[16]:


m


# In[ ]:





# In[ ]:




