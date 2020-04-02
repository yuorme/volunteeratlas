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
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

#initialize app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'VolunteerAtlas'
server = app.server

if os.environ.get('GDRIVE_API_CREDENTIALS') is not None and '`' not in os.environ.get('GDRIVE_API_CREDENTIALS'):
    gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS') #web
else:
    gc = pygsheets.authorize(service_file='volunteeratlas-service.json') #local: hack due to windows env double quotes issue

def get_sheets_df(gc, sheet_id):
    '''get and process google sheets into a dataframe
    '''

    sh = gc.open_by_key(sheet_id) 
    df1 = sh.worksheet_by_title("Volunteers").get_as_df()
    df2 = sh.worksheet_by_title("Requests").get_as_df()

    #process df
    df1['Radius'] = df1['Radius'].str.replace('km','').astype(float)

    def process_df(df, jitter=0.005):
        '''process columns common to volunteer and request dataframes
        '''
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Latitude'] = df['Latitude'].replace('', np.nan, regex=False)\
            .astype(float).apply(lambda x: x+np.random.uniform(-jitter,jitter)) 
        df['Longtitude'] = df['Longtitude'].replace('', np.nan, regex=False)\
            .astype(float).apply(lambda x: x+np.random.uniform(-jitter,jitter)) 

        return df

    return process_df(df1), process_df(df2)

def build_folium_map():

    #df_vol, df_req = get_sheets_df(gc, '16EcK3wX-bHfLpL3cj36j49PRYKl_pOp60IniREAbEB4') #TODO: hide sheetname
    df_vol, df_req = get_sheets_df(gc, '1CmhMm_RnnIfP71bliknEYy8HWDph2kUlXoIhAbYeJQE') #Uncomment this sheet for testing (links to public sheet) and comment out line above

    def get_popup_html(row, category):
        '''Builds a folium HTML popup to display in folium marker objects
        row (pandas Series): row from the google sheets dataframe
        '''
        email_subject = f"Delivery%20Request%20for%20{row['Given Name']}"
        va_email = 'volunteers.atlas@gmail.com'

        if category == 'Volunteers':
            html = '<head><style>body{font-size:14px;font-family:sans-serif}</style></head><body>'+\
                f"<b>Name:</b> {row['Given Name']} <br>" +  \
                f"<b>Country:</b> {row['Country']} <br>" +\
                f"<b>City:</b> {row['City/Town']} <br>" +\
                f"<b>Services:</b> {row['Type of Services']} <br>" +\
                f"<b>Transportation:</b> {row['Mode of Transportation']} <br>" +\
                f"<b>Radius:</b> {int(row['Radius'])} km <br>" +\
                f"<b>Day of Week:</b> {row['Preferred Day of Week']} <br>" +\
                f"<b>Time of Day:</b> {row['Preferred Time of Day']} <br>" +\
                f"<b>Languages:</b> {row['Languages Spoken']} <br>" +\
                f"<b>Payment:</b> {row['Reimbursement Method']} <br>" +\
                f"<b>About Me:</b> {row['About Me']} <br>" +\
                f"<a href='mailto:{row['Email Address']}?cc={va_email}&Subject={email_subject}' target='_blank'>Contact {row['Given Name']}</a>  <br></body>"
        elif category == 'Requests':
            html = '<head><style>body{font-size:14px;font-family:sans-serif}</style></head><body>'+\
                f"<b>Name:</b> {row['Given Name']} <br>" +  \
                f"<b>Country:</b> {row['Country']} <br>" +\
                f"<b>City:</b> {row['City/Town']} <br>" +\
                f"<b>Services:</b> {row['Type of Services']} <br>" +\
                f"<b>Transportation:</b> {row['Mode of Transportation']} <br>" +\
                f"<b>Radius:</b> {int(row['Radius'])} km <br>" +\
                f"<b>Day of Week:</b> {row['Preferred Day of Week']} <br>" +\
                f"<b>Time of Day:</b> {row['Preferred Time of Day']} <br>" +\
                f"<b>Languages:</b> {row['Languages Spoken']} <br>" +\
                f"<b>Payment:</b> {row['Reimbursement Method']} <br>" +\
                f"<b>About Me:</b> {row['About Me']} <br>" +\
                f"<a href='mailto:{row['Email Address']}?cc={va_email}&Subject={email_subject}' target='_blank'>Contact {row['Given Name']}</a>  <br></body>"
 
        iframe = folium.IFrame(html = folium.Html(html, script=True), width=250, height=300)
        popup = folium.Popup(iframe)
    
        return popup
      
    #build map
    m = folium.Map(
        location=[42, -97.5], #Canada
        tiles='Stamen Terrain',
        zoom_start=4,
        control_scale=True
    )

    def build_marker_cluster(m, df, category):

        dff = df.dropna(axis=0, how='any', subset=['Latitude','Longtitude']).copy()
        dff = dff.loc[(dff.Health == 'Yes')]
        
        if category == 'Volunteers':
            dff = dff.loc[(dff.Availability == 'Yes')]
            marker_color = '#00d700'
        elif category == 'Requests':
            marker_color = '#d77a00'

        #add marker cluster
        mc = MarkerCluster(
            name=category, 
            control=True,
            overlay=True,
            showCoverageOnHover=False
        )

        #add circle markers
        for idx, row in dff.iterrows():
            mc.add_child(
                folium.Circle(
    #                 radius=row['Radius']*250,
                    radius=300,
                    location=[row['Latitude'], row['Longtitude']],
                    popup=get_popup_html(row, category),
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color
                )
            ).add_to(m)

    build_marker_cluster(m, df_vol, 'Volunteers')
    build_marker_cluster(m, df_req, 'Requests')

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
    
    return m._repr_html_()

app.layout = html.Div(children=[
    html.Center(html.Img(src=app.get_asset_url('banner.png'), height=40)),
    dcc.Tabs(id="tabs", value='tab-map', children=[
        dcc.Tab(label='Interactive Map', value='tab-map', className='custom-tab', selected_className='custom-tab--selected-map'),
        dcc.Tab(label='Volunteer Signup Form', value='tab-volunteer', className='custom-tab', selected_className='custom-tab--selected-volform'),
        dcc.Tab(label='Delivery Request Form', value='tab-delivery', className='custom-tab', selected_className='custom-tab--selected-delform'),
        dcc.Tab(label='About Us', value='tab-about', className='custom-tab', selected_className='custom-tab--selected-about'),
    ]),
    html.Div(id='tabs-content'),
    html.Div(id='footer', children=[])
])

about_text = dcc.Markdown('''

    ##### About Us
    COVID-19 is a global problem requiring large-scale local responses. VolunteerAtlas is trying to create a global online repository of volunteers to help deal with this growing crisis. Self isolation for the most at-risk individuals in our community will require essentials like food and medicine be delivered to their doorsteps. If you're a young, healthy person with no dependents, and have been practicing social distancing, maybe you’d like to help.

    ##### Privacy
    We take your privacy seriously. Only your **Given Name, Email Address** and **About Me** sections will be shared on the website. All additional personal information will only be accessible by admins and will be used solely to confirm identities and protect those we are seeking to help.
    Our system is also designed to protect your physical location. We only ask for a postal code (not your home address) to get your approximate location. We then add an additional 500m of random noise to further protect your privacy.

    ##### FAQs
    **Why might posting my information on this website be more helpful than just posting on Facebook/Twitter?**

    Vulnerable people needing help the most are likely those who do not live in the same city as their close relatives/friends. Close relatives who live outside of the locality are less likely to see or be aware of Facebook groups or Twitter posts from localized help groups. Also, social media is ephemeral, if you are offering to help over a course of weeks or months, putting your information into a central repository is a more effective way to do it.

    **What is the process for connecting volunteers with recipients?**

    Your approximate location will populate an interactive map and certain details from your responses will be available on your 'public profile'. Recipients will navigate through the map to select the most suitable volunteer based on their profile. A small group of admin will be involved in facilitating your volunteer effort behind the scenes.

    **Buying groceries for more than just yourself might look to others like panic buying. What can I do if I'm confronted/prevented from shopping based on such suspicions?**

    We are thinking about ways to implement a verification and authentication program. For the time being, we recommend you speak with store staff/management about your volunteerism and show them your registration on this website.
''')

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab, iframe_height=800):
    if tab == 'tab-map':
        return html.Div([
            dcc.Markdown('### Filter by day, time, service type and payment type '),
            html.Div(style={'width':'49%',
                    'display':'inline-block',
                    'float':'left',
                              },
                        children=[
            dcc.Dropdown(
                id='filters-day',
                               options=[
                    {'label':'Monday', 'value':'Mon'},
                    {'label':'Tuesday', 'value':'Tue'},
                    {'label':'Wednesday', 'value':'Wed'},
                    {'label':'Thursday', 'value':'Thu'},
                    {'label':'Friday', 'value':'Fri'},
                    {'label':'Saturday', 'value':'Sat'},
                    {'label':'Sunday', 'value':'Sun'},
                    ], #TODO: have it assign labels programmatically based on availibilities of current volunteers (ie, if nobody is free on mondays, that option will not be available for the filter)
                multi=True,
                placeholder='Select days of availability',
                value=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                )]),
            html.Div(style={'width':'49%',
                        'display':'inline-block',
                        'float':'right',
                        },
                    children=[
            dcc.Dropdown(
                id='filters-time',
                 options=[
                    {'label':'Morning', 'value':'Morning'},
                    {'label':'Afternoon', 'value':'Afternoon'},
                    {'label':'Evening', 'value':'Evening'},
                    ],
                multi=True,
                placeholder='Select times of availability',
                value=['Morning', 'Afternoon', 'Evening']
                )]),
            html.Div(style={'width':'49%',
                    'display':'inline-block',
                    'float':'left',
                              }, children=[
            dcc.Dropdown(
                id='filters-servicetype',
                options=[
                    {'label':'Groceries', 'value':'Groceries'},
                    {'label':'Pharmacy', 'value':'Pharmacy'},
                    {'label':'Household Supplies', 'value':'Household Supplies'},
                    {'label':'Other Errands', 'value':'Other Errands'}
                    ],
                multi=True,
                placeholder='Select type of service',
                value=['Groceries', 'Pharmacy', 'Household Supplies', 'Other Errands']),
                
            ]),
            html.Div(style={'width':'49%',
                    'display':'inline-block',
                    'float':'right',
                              }, children=[
            dcc.Dropdown(
                id='filters-finance',
                options=[
                    {'label':'Cash', 'value':'Cash'},
                    {'label':'Cheque', 'value':'Cheque'},
                    {'label':'Electronic Money Transfer', 'value':'Electronic Money Transfer'},
                    ],
                multi=True,
                placeholder='Select reimbursment type',
                value=['Cash', 'Cheque', 'Electronic Money Transfer'])
            ]),
            html.Iframe(
            id='folium-map', 
            srcDoc=build_folium_map(), 
            style=dict(width='100%', height=iframe_height, overflow='hidden') #DEBUG: Fix IFrame y-scroll bar
            )
            ])
    elif tab == 'tab-volunteer':
        return html.Iframe(
            id='volunteer-form', 
            src='https://docs.google.com/forms/d/e/1FAIpQLSfw3LFsXtCCmr-ewkUuIltKIP5PKNY8Xn8h3MjVrFrvfvktPw/viewform?embedded=true', 
            style=dict(width='100%', height=iframe_height,)
            )
    elif tab == 'tab-delivery':
        return html.Iframe(
            id='request-form', 
            src='https://docs.google.com/forms/d/e/1FAIpQLSfFkdsyhiPTQDA5LtnJFzHUFzTL-aQaO-9koXIkOir2K2Lw7g/viewform?embedded=true', 
            style=dict(width='100%', height=iframe_height,)
            ) 
    elif tab == 'tab-about':
        return html.Div(
            children=[
                about_text,
                html.A('Code on Github', href='https://github.com/yuorme/volunteeratlas', target='_blank')
            ]
        )



if __name__ == '__main__':
    app.run_server(debug=True, port= 5000)


