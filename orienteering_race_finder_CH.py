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

st.sidebar.subheader('How to')
st.sidebar.markdown('Apply the filters from top to bottom and find your races ...')
st.sidebar.markdown('data is from https://www.o-l.ch/cgi-bin/fixtures')

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



