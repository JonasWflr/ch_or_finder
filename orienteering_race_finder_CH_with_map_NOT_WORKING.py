#!/usr/bin/env python
# coding: utf-8

# # orienteering race finder CH
# 

# ## read file
# csv might be corrupt, i.e. have illegal characters ';' in fields

import pandas as pd
import io
import requests
import re
from datetime import datetime
import streamlit as st
import pydeck as pdk

import numpy as np
import altair as alt

st.beta_set_page_config(
    page_title="Race finder",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("CH Orienteering Race Finder")

url="https://www.o-l.ch/cgi-bin/fixtures?&csv=1"

##############################################################
# all about the map

## https://github.com/ValentinMinder/Swisstopo-WGS84-LV03/blob/master/scripts/py/wgs84_ch1903.py
# WGS84 <-> LV03 converter based on the scripts of swisstopo written for python2.7
# Aaron Schmocker [aaron@duckpond.ch]
# Convert CH y/x to WGS lat
@st.cache
def CHtoWGSlat(input):
    y = input['coord_x']
    x = input['coord_y']
    if y == '' or x == '':
        return 600000
    else:
        # Axiliary values (% Bern)
        # (!)
        y = float(y)
        x = float(x)
        y_aux = (y - 600000) / 1000000
        x_aux = (x - 200000) / 1000000
        lat = (16.9023892 + (3.238272 * x_aux)) + \
                - (0.270978 * pow(y_aux, 2)) + \
                - (0.002528 * pow(x_aux, 2)) + \
                - (0.0447 * pow(y_aux, 2) * x_aux) + \
                - (0.0140 * pow(x_aux, 3))
        # Unit 10000" to 1" and convert seconds to degrees (dec)
        lat = (lat * 100) / 36
        return lat

# Convert CH y/x to WGS long
@st.cache
def CHtoWGSlng(input):
    # (!)
    y = input['coord_x']
    x = input['coord_y']
    if y == '' or x == '':
        return 200000
    else:
        # Axiliary values (% Bern)
        y = float(y)
        x = float(x)
        y_aux = (y - 600000) / 1000000
        x_aux = (x - 200000) / 1000000
        lng = (2.6779094 + (4.728982 * y_aux) + \
                + (0.791484 * y_aux * x_aux) + \
                + (0.1306 * y_aux * pow(x_aux, 2))) + \
                - (0.0436 * pow(y_aux, 3))
        # Unit 10000" to 1" and convert seconds to degrees (dec)
        lng = (lng * 100) / 36
        return lng
            
##############################################################
@st.cache
def load_data():
    s=requests.get(url).content
    f=io.StringIO(s.decode('iso-8859-1'))

    input_list = []
    NUMBER_OF_COLUMNS = 18
    for line in f:
        #print(line)
        row = line.strip().split(';')
        #print(len(row))
        if len(row) != NUMBER_OF_COLUMNS:
            #print(row)
            print('INFO: illegal character \';\' in line in input csv',end=' ')
            line = re.sub(r'&[\w#]{3};',' ',line)
            row = line.strip().split(';')
            
            if len(row) != NUMBER_OF_COLUMNS:
                print('... could not fix')
                print('ERROR: could not parse line, illegal character could not be removed')
                continue
            
            print('... fixed: removed illegal character')
        input_list.append(row)
    df = pd.DataFrame(input_list[1:], columns=input_list[0])

    # convert date to datetime
    df['date'] = df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))

    ## check if it is in future
    today = datetime.today()
    df['is_future_date'] = df['date'].apply(lambda x: (x-today).total_seconds()>=0)

    ## get week number
    df['week'] = df['date'].apply(lambda x: x.isocalendar()[1])
    
    ## get month
    df['month'] = df['date'].apply(lambda x: x.month)
    
    ## LV03 --> WGS84
    df['latitude'] = df[['coord_y','coord_x']].apply(CHtoWGSlat, axis=1)
    df['longitude'] = df[['coord_y','coord_x']].apply(CHtoWGSlng, axis=1)
    
    return df



df = load_data()

##############################################################
st.sidebar.header('choose time')

# Add a selectbox to the sidebar:
#future_race = st.sidebar.selectbox('only upcoming races?', ['only future races', 'all races this year'], 0)
future_race = st.sidebar.radio('only upcoming races?', ['only future races', 'all races this year'], 0)

## future race
if future_race == 'only future races':
    df = df[df['is_future_date']]
else:
    df = df 

## month slider    
month_min, month_max = st.sidebar.slider('Choose months', int(df['month'].min()),int(df['month'].max()),[int(df['month'].min()), int(df['month'].max())],1)
#month_min, month_max = st.sidebar.slider('Choose months', 1, 12,[int(df_1['month'].min()), int(df_1['month'].max())],1)
df = df[(df['month']>=month_min) & (df['month']<=month_max )]

## weeknumber slider    
week_min, week_max = st.sidebar.slider('Choose Weeks', 1,53,[int(df['week'].min()), int(df['week'].max())],1)
df = df[(df['week']>=week_min) & (df['week']<=week_max )]

##############################################################
st.sidebar.header('choose location')

## choose region

canton_list = ['all'] + df['region'].unique().tolist()
canton = st.sidebar.selectbox('Select region', canton_list, 0)
if canton == 'all':
    df = df
else:
    df = df[df['region']== canton]
 
##############################################################
st.sidebar.header('choose details')


## only national
if st.sidebar.checkbox('only national races?'):
    df = df[df['national']== '1']
else:
    df = df
    
## foot / bike / ski
kind = st.sidebar.radio('kind of race', ['all', 'foot', 'bike', 'ski'], 1)

if kind == 'all':
    df = df
else:
    df = df[df['kind']==kind]
    
## night / day
day_race = st.sidebar.radio('day and night races', ['all', 'only day races ', 'only night races'], 0)

if day_race == 'only day races':
    df = df[df['day_night']=='day']
elif day_race == 'only night races':
    df = df[df['day_night']=='night']
else:
    df = df 

##############################################################
## print map
# not working
#st.map(df[['latitude','longitude']])

lat_avg = df['latitude'].mean()
lng_avg = df['longitude'].mean()

lat_avg = 47.15
lng_avg = 8.8

# st.pydeck_chart(
    # pdk.Deck(
        # map_style='mapbox://styles/mapbox/light-v9',
        # initial_view_state=pdk.ViewState(
            # latitude=lat_avg,
            # longitude=lng_avg,
            # zoom=5,
            # pitch=0,
        # ),
        # layers=[
            # pdk.Layer(
                # 'HexagonLayer',
                # data=df,
                # get_position='[lon, lat]',
                # radius=200,
                # elevation_scale=4,
                # elevation_range=[0, 1000],
                # pickable=True,
                # extruded=True,
            # ),
            # pdk.Layer(
                # 'ScatterplotLayer',
                # data=df,
                # get_position='[longitude, latitude]',
                # get_color='[200, 30, 0, 160]',
                # get_radius=100,
            # ),
        # ],
    # )
# )

st.deck_gl_chart(
    viewport={
        'latitude': lat_avg,
        'longitude': lng_avg,
        'zoom': 11,
        'pitch': 0,
    },
    layers=[{
        'type': 'ScatterplotLayer',
        'data': df,
        'radiusScale': 5,
        'radiusMinPixels': 5,
        'getFillColor': [248, 24, 148],
    }]
)

##############################################################
## reduce columns and print
displayed_columns = ['week', 'date', 'event_name', 'region', 'location', 'day_night', 'national', 'map', 'club', 'event_link', 'deadline']
df = df[displayed_columns]


# convert the link name into an html link (if it exists)
def make_clickable(link):
    # target _blank to open new window
    # check if it exists
    if len(link) > 0:
        link_text = f'<a target="_blank" href="{link}">link</a>'
    else:
        link_text = ''
    return link_text

df['event_link'] = df['event_link'].apply(make_clickable)
# convert df to html
df = df.to_html(escape=False)
# output as simple table (see also very first command at top for styling options
st.write(df, unsafe_allow_html=True)

st.write('data is from https://www.o-l.ch/cgi-bin/fixtures')


## do some plotting

# df_mr = df.groupby(by=['club','region']).count()[['unique_id','date']]
# df_mr = pd.DataFrame(df_mr.to_records()).drop(columns=['date'])

# c = alt.Chart(df_mr).mark_circle().encode(
    # x='club', y='region', size='unique_id', color='c', tooltip=['a', 'b', 'c'])

# st.altair_chart(c, use_container_width=True)

#st.map(df_end)
