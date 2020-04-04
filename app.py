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
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from about import get_about_text

#initialize app
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
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
        df['City/Town'] = df['City/Town'].str.title()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Latitude'] = df['Latitude'].replace('', np.nan, regex=False)\
            .astype(float).apply(lambda x: x+np.random.uniform(-jitter,jitter)) 
        df['Longtitude'] = df['Longtitude'].replace('', np.nan, regex=False)\
            .astype(float).apply(lambda x: x+np.random.uniform(-jitter,jitter)) 

        return df

    return process_df(df1), process_df(df2)

def translator(word, language):
    translate_dict = {
        'Volunteers':{'fr':'Bénévole'},
        'Requests':{'fr':'Demandes'},
        'Interactive Map':{'fr':'Carte interactive'},
        'Volunteer Signup Form':{'fr':'Inscription des bénévoles'},
        'Delivery Request Form':{'fr':'Demande de livraison'},
        'About Us':{'fr':'À propos de nous'},
        'Name':{'fr':'Nom'},
        'Country':{'fr':'Pays'},
        'City':{'fr':'Ville'},
        'Services':{'fr':'Services'},
        'Transportation':{'fr':'Transport'},
        'Radius':{'fr':'Radius'},
        'Day of Week':{'fr':'Jour de la semaine'},
        'Time of Day':{'fr':'Moment de la journée'},
        'Languages':{'fr':'Langues'},
        'Payment':{'fr':'Paiement'},
        'About Me':{'fr':'À propos de moi'},
        'Type':{'fr':'Type'},
        # '':{'fr':''},
        }
    if language != 'en':
        return translate_dict[word][language]
    else:
        return word

def build_folium_map(language):

    df_vol, df_req = get_sheets_df(gc, '16EcK3wX-bHfLpL3cj36j49PRYKl_pOp60IniREAbEB4') #TODO: hide sheetname
    # df_vol, df_req = get_sheets_df(gc, '1CmhMm_RnnIfP71bliknEYy8HWDph2kUlXoIhAbYeJQE') #Uncomment this sheet for testing (links to public sheet) and comment out line above

    def get_popup_html(row, category):
        '''Builds a folium HTML popup to display in folium marker objects
        row (pandas Series): row from the google sheets dataframe
        '''

        va_email = 'volunteers.atlas@gmail.com'

        if category == 'Volunteers':
            email_subject = f"Delivery%20Request%20for%20{row['Given Name']}"
            html = "<head><style>body{font-size:14px;font-family:sans-serif}</style></head><body>"+\
                f"<b>{translator('Volunteers', language)}</b> <br>" + \
                f"<b>{translator('Name', language)}:</b> {row['Given Name']} <br>" +  \
                f"<b>{translator('Country', language)}:</b> {row['Country']} <br>" +\
                f"<b>{translator('City', language)}:</b> {row['City/Town']} <br>" +\
                f"<b>{translator('Services', language)}:</b> {row['Type of Services']} <br>" +\
                f"<b>{translator('Transportation', language)}:</b> {row['Mode of Transportation']} <br>" +\
                f"<b>{translator('Radius', language)}:</b> {int(row['Radius'])} km <br>" +\
                f"<b>{translator('Day of Week', language)}:</b> {row['Preferred Day of Week']} <br>" +\
                f"<b>{translator('Time of Day', language)}:</b> {row['Preferred Time of Day']} <br>" +\
                f"<b>{translator('Languages', language)}:</b> {row['Languages Spoken']} <br>" +\
                f"<b>{translator('Payment', language)}:</b> {row['Reimbursement Method']} <br>" +\
                f"<b>{translator('About Me', language)}:</b> {row['About Me']} <br>" +\
                f"<a href='mailto:{row['Email Address']}?cc={va_email}&Subject={email_subject}' target='_blank'>Contact {row['Given Name']}</a>  <br></body>"
        elif category == 'Requests':
            html = "<head><style>body{font-size:14px;font-family:sans-serif}</style></head><body>"+\
                f"<b>{translator('Requests', language)}</b> <br>" + \
                f"<b>{translator('Country', language)}:</b> {row['Country']} <br>" +\
                f"<b>{translator('City', language)}:</b> {row['City/Town']} <br>" +\
                f"<b>{translator('Services', language)}:</b> {row['Type of Services']} <br>" +\
                f"<b>{translator('Type', language)}:</b> {row['Type of Request']} <br>" +\
                f"<b>{translator('Day of Week', language)}:</b> {row['Preferred Day of Week']} <br>" +\
                f"<b>{translator('Time of Day', language)}:</b> {row['Preferred Time of Day']} <br>" +\
                f"<b>{translator('Languages', language)}:</b> {row['Languages Spoken']} <br>" +\
                f"<b>{translator('Payment', language)}:</b> {row['Reimbursement Method']} <br>" +\
                f"<a href='https://docs.google.com/forms/d/e/1FAIpQLSfw3LFsXtCCmr-ewkUuIltKIP5PKNY8Xn8h3MjVrFrvfvktPw/viewform?embedded=true' target='_blank'>Sign Up to Help</a>  <br></body>"
 
        iframe = folium.IFrame(html = folium.Html(html, script=True), width=260, height=len(html)/2.25)
        popup = folium.Popup(iframe)
    
        return popup

    def build_marker_cluster(m, df, category):

        dff = df.dropna(axis=0, how='any', subset=['Latitude','Longtitude']).copy()

        if category == 'Volunteers':
            dff = dff.loc[(dff.Health == 'Yes') & (dff.Availability == 'Yes')]
            marker_color = '#00d700'
        elif category == 'Requests':
            marker_color = '#d77a00'

        #add marker cluster
        mc = MarkerCluster(
            name=translator(category, language),
            control=True,
            overlay=True,
            showCoverageOnHover=False
        )

        #add circle markers
        for idx, row in dff.iterrows():

            dense_cities = ['Montreal','Toronto','Ottawa','Montréal','Cote St Luc','Gatineau'] #HACK: make people outside major clusters reflect their true radius
            if category == 'Volunteers' and row['City/Town'] not in dense_cities:
                radius = row['Radius']*1000
            else:
                radius = 250

            mc.add_child(
                folium.Circle(
                    radius=radius,
                    location=[row['Latitude'], row['Longtitude']],
                    popup=get_popup_html(row, category),
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color
                )
            ).add_to(m)

    #build map
    m = folium.Map(
        location=[42, -97.5], #Canada
        tiles='Stamen Terrain',
        min_zoom=3,
        zoom_start=4,
        control_scale=True
    )

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

app.layout = html.Div(
    children=[
        dcc.Location(id='url'),
        dbc.NavbarSimple(
            children=[
                html.Img(src=app.get_asset_url('va-logo.png'), height=35, width=35),
                dbc.DropdownMenu(
                    children=[
                        
                        dbc.DropdownMenuItem('EN', href='/en', id='en-link', active=True),
                        dbc.DropdownMenuItem('FR', href='/fr', id='fr-link', active=True),
                    ],
                    nav=True,
                    in_navbar=True,
                    id='language-dropdown'
                ),
            ],
            color='light',
            light=True,
            brand='VolunteerAtlas'
        ), 
        dcc.Tabs(id='tabs', value='tab-map', style={'height':'20%','width':'100%'} 
        ),
        html.Div(id='tabs-content', style={'height':'50%','width':'100%'} ),
        html.Div(id='footer', children=[], style={'height':'10%','width':'100%'})
])

@app.callback(
    Output('tabs', 'children'),
    [Input('url', 'pathname')]
)
def render_tabs(url):

    language = get_url_language(url)

    return [
        dcc.Tab(label=translator('Interactive Map', language), value='tab-map', className='custom-tab', selected_className='custom-tab--selected-map'),
        dcc.Tab(label=translator('Volunteer Signup Form', language), value='tab-volunteer', className='custom-tab', selected_className='custom-tab--selected-volform'),
        dcc.Tab(label=translator('Delivery Request Form', language), value='tab-request', className='custom-tab', selected_className='custom-tab--selected-delform'),
        dcc.Tab(label=translator('About Us', language), value='tab-about', className='custom-tab', selected_className='custom-tab--selected-about'),
    ]

@app.callback(
    Output('language-dropdown', 'label'),
    [Input('url', 'pathname')],
)
def update_label(url):
    return get_url_language(url).upper()

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
languages = ['en','fr']
@app.callback(
    [Output(f'{i}-link', 'active') for i in languages],
    [Input('url', 'pathname')],
)
def toggle_active_links(pathname):
    if pathname == '/':
        # Treat first item in list as the homepage / index
        return True, False
    return [pathname == f'/{i}' for i in languages]

def get_url_language(url):
    '''get the language from the url with 
    '''
    language = url.replace('/','')
    if language == '':
        language = 'en'

    return language

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
    Input('url', 'pathname')]
)
def render_content(tab, url, iframe_height=800):

    language = get_url_language(url)

    if tab == 'tab-map':
        return html.Iframe(
            id='folium-map', 
            srcDoc=build_folium_map(language),
            height=iframe_height,
            width='100%',
            style={'overflow':'hidden','overflow-x':'hidden','overflow-y':'hidden'} #ISSUE: Fix IFrame y-scroll bar
            ) 
    elif tab == 'tab-volunteer':
        return html.Iframe(
            id='volunteer-form', 
            src='https://docs.google.com/forms/d/e/1FAIpQLSfw3LFsXtCCmr-ewkUuIltKIP5PKNY8Xn8h3MjVrFrvfvktPw/viewform?embedded=true',
            style={'width':'100%', 'height':iframe_height, 'margin-left':'auto', 'margin-right':'auto'}
            )
    elif tab == 'tab-request':
        return html.Iframe(
            id='request-form', 
            src='https://docs.google.com/forms/d/e/1FAIpQLSfFkdsyhiPTQDA5LtnJFzHUFzTL-aQaO-9koXIkOir2K2Lw7g/viewform?embedded=true',
            style={'width':'100%', 'height':iframe_height, 'margin-left':'auto', 'margin-right':'auto'}
            ) 
    elif tab == 'tab-about':
        return html.Div(
            children=[
                get_about_text(language),
                html.A('Code on Github', href='https://github.com/yuorme/volunteeratlas', target='_blank')
            ],
            style={'width':'90%', 'margin-left':'auto', 'margin-right':'auto'}
        )
        
if __name__ == '__main__':
    app.run_server(debug=True, port=5000)