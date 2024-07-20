from files import filter
from files import builds_per_region_pie
from files import key_percentages
from files import donut
from files import log_on_scatter
from files import number_of_builds_scatter
from files import team_usage_builds
from files import top_apps_time
from files import monthly_metrics

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from datetime import timezone
from datetime import date
import streamviz
import altair as alt
import numpy as np

st.set_page_config(
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
with open('style.css') as file:
    css = file.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

#######################
# Load data

df = pd.read_csv('data/log_on_data.csv')

df['date_of_build'] = pd.to_datetime(df['date_of_build'], errors='coerce', dayfirst=True, format='%d/%m/%Y').dt.date
df['log_on'] = pd.to_datetime(df['log_on'], errors='coerce', dayfirst=True, format='%d/%m/%Y %H:%M:%S')
df['log_off'] = pd.to_datetime(df['log_off'], errors='coerce', dayfirst=True, format='%d/%m/%Y %H:%M:%S')

df['time_spent'] = (df['log_off'] - df['log_on']).dt.total_seconds() / 3600
df['time_spent'] = df['time_spent'].fillna(0)

builds_df = df[df['log_on'].isna() & df['log_off'].isna()]
logins_df = df[df['log_on'].notna() & df['log_off'].notna()]

#######################
# Sidebar
with st.sidebar:
    st.title('Mock Data Finstrat Observability Dashboard')

    with st.expander("🧭 Menu"):
        st.page_link("fin_dashboard_streamlit.py", label="Live Dashboard", icon="🏠", use_container_width=True)
        st.page_link("./pages/mock_data_dashboard.py", label="Mock Data Dashboard", icon="1️⃣",
                     use_container_width=True)
        st.page_link("./pages/old.py", label="Old Dashboard", icon="1️⃣", use_container_width=True)

    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input("#### Date Range", [], format="DD/MM/YYYY",
                                       min_value=builds_df['date_of_build'].min(),
                                       max_value=builds_df['date_of_build'].max())
    periodic_filter = st.selectbox("#### Periodic Filter", ["Daily", "Weekly", "Monthly"])
    region_filter = st.sidebar.multiselect("#### Region", options=["EMEA", "APAC", "AMER"])
    env_filter = st.sidebar.multiselect("#### Environment", options=df['environment'].unique())
    status_filter = st.sidebar.multiselect("#### Status", options=["Success", "Faliure"])
    builds_per_team_filter = st.sidebar.slider("#### Builds per Team view", 0, len(df['teamname'].unique()), 10)
    time_count_filter = st.selectbox("#### Time Count", ["total_time_spent", "logins_count"])

    st.sidebar.header("Colour :smile:")
    color_theme_list = ['magma', 'cividis', 'greens', 'inferno', 'blues', 'plasma', 'reds', 'rainbow', 'turbo',
                        'viridis']
    selected_color_theme = st.sidebar.selectbox("#### Select a Colour Theme", color_theme_list)

    color_schemes = {
        'blues': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],
        'cividis': ['#00204c', '#302a6b', '#64386b', '#9c5a73', '#cc8964', '#f0b256', '#fdda41'],
        'greens': ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#006d2c', '#00441b'],
        'inferno': ['#000004', '#160b39', '#420a68', '#6a176e', '#932667', '#bc3754', '#dd513a', '#f3771b', '#fca50a'],
        'magma': ['#000004', '#1d0a35', '#4f0c66', '#812581', '#b5367a', '#e55063', '#fb8761', '#fec287', '#f6efa6'],
        'plasma': ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26'],
        'reds': ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d'],
        'rainbow': ['#e70000', '#ff6900', '#ffdf00', '#94c11f', '#35a043', '#0d8c7f', '#0073cf', '#4d51d1', '#8e1bc4'],
        'turbo': ['#23171b', '#4b1d38', '#772355', '#a52c6c', '#ce4073', '#ed5d68', '#fa8155', '#fba341', '#f8c230'],
        'viridis': ['#440154', '#46337e', '#365c8d', '#277f8e', '#1fa187', '#4ac16d', '#a0da39', '#fde725']
    }
    selected_colors = color_schemes[selected_color_theme]

    if st.button("Clear Filters"):
        date_range = []
        status_filter = []
        builds_per_team_filter = 10
        periodic_filter = 'Daily'
        time_count_filter = 'total_time_spent'

######################
# Dashboard Main Panel

filtered_builds_df = filter.filter_df(builds_df, date_range, status_filter, region_filter, env_filter)
logins_df, min_date, max_date = filter.login_filter(logins_df, region_filter, env_filter)
filtered_logins_df = filter.login_filter_date(logins_df, date_range)
col = st.columns((1.5, 4.5, 2), gap='medium')
print("hi")

with col[0]:
    st.title("Current")
    st.markdown("#### Monthly Metrics")

    monthly_metrics.main(builds_df)

    st.markdown("#### Key Percentages")
    key_percentages.show(filtered_builds_df)

with col[1]:
    st.markdown(f'#### Top {builds_per_team_filter} Teams - No. of Builds')
    st.altair_chart(team_usage_builds.bar_chart(filtered_builds_df, builds_per_team_filter, selected_color_theme),
                    use_container_width=True)
    st.altair_chart(log_on_scatter.scatter(filtered_logins_df, periodic_filter, time_count_filter, selected_colors),
                    use_container_width=True)
    st.altair_chart(number_of_builds_scatter.scatter(filtered_builds_df, periodic_filter, selected_colors),
                    use_container_width=True)

with col[2]:
    st.markdown('#### Top Apps: Time Spent')
    top_apps_time.main(filtered_logins_df)

    with st.expander('##### :orange[**Latest News:**]', expanded=True):
        st.write('''
            - :orange[**Headline 1**]: 11 Apps on the AppsStore
            - :orange[**Headline 2**]: Some really really cool info about finstrat here
            - :orange[**Headline 3**]: Finstrat is growing.
            ''')     