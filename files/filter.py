import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import timezone
from datetime import date
import streamviz
import altair as alt
import numpy as np


def filter_df(df, date_range, status_filter, region_filter, env_filter):
    print(df, "hi")
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['date_of_build'] >= start_date) & (df['date_of_build'] <= end_date)]
    if status_filter:
        df = df[df['status'].isin(status_filter)]
    if region_filter:
        df = df[df['region'].isin(region_filter)]
    if env_filter:
        df = df[df['environment'].isin(env_filter)]
        print(4)

    return df


def login_filter(df, region_filter, env_filter):
    # Group by project and date to get the total time spent and number of logins for each project

    if region_filter:
        df = df[df['region'].isin(region_filter)]
    if env_filter:
        df = df[df['environment'].isin(env_filter)]

    df = df.groupby(['projname', df['log_on'].dt.date]).agg(
        total_time_spent=('time_spent', 'sum'),
        logins_count=('log_on', 'count')
    ).reset_index()
    df.columns = ['projname', 'log_on_date', 'total_time_spent', 'logins_count']
    df['log_on_date'] = pd.to_datetime(df['log_on_date'])

    min_date = df['log_on_date'].min()
    max_date = df['log_on_date'].max()
    return df, min_date, max_date


# Only neccessary for log_on_scatter
def merge_dates(df, periodic_filter):
    df['log_on_date'] = pd.to_datetime(df['log_on_date'])
    df['log_on_date'] = df['log_on_date'].dt.to_period(periodic_filter[0])
    df = df.groupby('log_on_date')[['total_time_spent', 'logins_count']].sum().sort_values('log_on_date',
                                                                                           ascending=True).reset_index()
    return df


def login_filter_date(df, date_range):
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0], dayfirst=True)
        end_date = pd.to_datetime(date_range[1], dayfirst=True)
        df['log_on_date'] = pd.to_datetime(df['log_on_date'], dayfirst=True)
        df = df[(df['log_on_date'] >= start_date) & (df['log_on_date'] <= end_date)].reset_index(drop=True)

    return df


# Create new dataframed which is grouped to achieve number of builds
def groupby(df, groupby, name='build_count'):
    scatter_data = df.groupby(groupby).size().reset_index(name=name)
    return scatter_data


def count_new_projects(df, env):
    '''Count unique projects in each environment'''
    dev_projects = df[df['environment'] == env]['projname'].nunique()
    return dev_projects