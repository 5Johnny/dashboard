import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import timezone 
from datetime import date
import streamviz
import altair as alt
import numpy as np


def main(builds_df):
    builds_df['date_of_build'] = pd.to_datetime(builds_df['date_of_build'])
    current_date = datetime.datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    current_day = current_date.day


    # Filter builds for this month and last month up to the current day
    this_month_builds = builds_df[(builds_df['date_of_build'].dt.month == current_month) & (builds_df['date_of_build'].dt.year == current_year) & (builds_df['date_of_build'].dt.day <= current_day)]
    last_month_builds = builds_df[(builds_df['date_of_build'].dt.month == current_month - 1) & (builds_df['date_of_build'].dt.year == current_year) & (builds_df['date_of_build'].dt.day <= current_day)]
    # If the current month is January, we need to consider the previous year for last month's builds
    if current_month == 1:
        last_month_builds = builds_df[(builds_df['date_of_build'].dt.month == 12) & (builds_df['date_of_build'].dt.year == current_year - 1) & (builds_df['date_of_build'].dt.day <= current_day)]

    # Initialize variables to 0 to avoid errors if there are no builds
    this_month_new_projects = 0
    last_month_new_projects = 0
    this_month_successful_builds = 0
    last_month_successful_builds = 0
    this_month_new_developers = 0
    last_month_new_developers = 0

    # Calculate the number of new projects created this month and last month up to the current day
    if not this_month_builds.empty:
        this_month_new_projects = this_month_builds['projname'].nunique()
        this_month_successful_builds = this_month_builds[this_month_builds['status'] == 'Success'].shape[0]
        this_month_new_developers = this_month_builds['user_id'].nunique()

    if not last_month_builds.empty:
        last_month_new_projects = last_month_builds['projname'].nunique()
        last_month_successful_builds = last_month_builds[last_month_builds['status'] == 'Success'].shape[0]
        last_month_new_developers = last_month_builds['user_id'].nunique()


    successful_builds = builds_df['status'].value_counts().get('Success', 0)
    st.metric("Successful Builds", this_month_successful_builds, this_month_successful_builds -last_month_successful_builds )
    st.metric("New Projects created - Dev", this_month_new_projects, this_month_new_projects - last_month_new_projects )
    st.metric("New Developers", this_month_new_developers, this_month_new_developers-last_month_new_developers)
    st.metric("Number of Users", 0, 0)