import streamlit as st
import pandas as pd
import plotly.express as px

# Data loading function from CSV

st.set_page_config(layout='wide')
def load_data(file_path):
    return pd.read_csv(file_path, parse_dates=['date_of_build'])

# Load data
df = load_data('data/new_mock_data.csv')

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Title
st.title("Jenkins Build Dashboard")

# Filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date Range", [], format="DD/MM/YYYY")
env_filter = st.sidebar.multiselect("Environment", options=df['environment'].unique())
status_filter = st.sidebar.multiselect("Status", options=df['status'].unique())

# Apply filters to data
filtered_df = df.copy()
if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df['date_of_build'] >= start_date) & (df['date_of_build'] <= end_date)]
if env_filter:
    df = df[df['environment'].isin(env_filter)]
if status_filter:
    df = df[df['status'].isin(status_filter)]

# Summary metrics
st.header("Summary Metrics")

total_builds = len(filtered_df)
successful_builds = filtered_df['status'].value_counts().get('Success', 0)
failed_builds = filtered_df['status'].value_counts().get('Failed', 0)
new_projects = filtered_df['projname'].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Builds", total_builds)
with col2:
    st.metric("Successful Builds", successful_builds)
with col3:
    st.metric("Failed Builds", failed_builds)
with col4:
    st.metric("New Projects", new_projects)

# Function to display detailed view

def show_detailed_view(metric, filtered_df):


    if metric == "Total Builds":
        with bottom1:
            st.subheader("Total Builds Over Time")
            builds_over_time = filtered_df.groupby(filtered_df['date_of_build'].dt.date).size().reset_index(name='counts')
            fig = px.line(builds_over_time, x='date_of_build', y='counts', title="Total Builds Over Time")
            st.plotly_chart(fig)
        with bottom2:
            st.subheader("Detailed Data")
            st.dataframe(filtered_df)

    elif metric == "Successful Builds":

        with bottom1:
            st.subheader("Successful Builds Over Time")
            success_df = filtered_df[filtered_df['status'] == 'Success']
            success_over_time = success_df.groupby(success_df['date_of_build'].dt.date).size().reset_index(name='counts')
            fig = px.line(success_over_time, x='date_of_build', y='counts', title="Successful Builds Over Time")
            st.plotly_chart(fig)
        with bottom2:
            st.subheader("Detailed Data")
            st.dataframe(success_df)
    elif metric == "Failed Builds":
        with bottom1:
            st.subheader("Failed Builds Over Time")
            failed_df = filtered_df[filtered_df['status'] == 'Failed']
            failed_over_time = failed_df.groupby(failed_df['date_of_build'].dt.date).size().reset_index(name='counts')
            fig = px.line(failed_over_time, x='date_of_build', y='counts', title="Failed Builds Over Time")
            st.plotly_chart(fig)
        with bottom2:
            st.subheader("Detailed Data")
            st.dataframe(failed_df)
    elif metric == "New Projects":
        with bottom1:
            st.subheader("New Projects")
            project_counts = filtered_df['project'].value_counts().reset_index()
            project_counts.columns = ['project', 'counts']
            fig = px.bar(project_counts, x='project', y='counts', title="New Projects")
            st.plotly_chart(fig)
        with bottom2:
            st.subheader("Detailed Data")
            st.dataframe(filtered_df[['projname', 'date_of_build']].drop_duplicates())

# Flag to check if detailed view is shown
show_details = False
selected_metric = None

# Buttons for detailed view
st.subheader("Click on a metric to see detailed view")

col1, col2, col3, col4 = st.columns(4)
if col1.button("Total Builds"):
    show_details = True
    selected_metric = "Total Builds"
if col2.button("Successful Builds"):
    show_details = True
    selected_metric = "Successful Builds"
if col3.button("Failed Builds"):
    show_details = True
    selected_metric = "Failed Builds"
if col4.button("New Projects"):
    show_details = True
    selected_metric = "New Projects"

# Show detailed view if a metric button is clicked
if show_details and selected_metric:
    bottom1, bottom2 = st.columns((7,4))
    show_detailed_view(selected_metric, filtered_df)
else:
    # Additional visual elements
    st.header("Additional Visualizations")

    # Build status pie chart
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'counts']
    fig = px.pie(status_counts, values='counts', names='status', title="Build Status Distribution")
    st.plotly_chart(fig)

    # Environment bar chart
    env_counts = filtered_df['environment'].value_counts().reset_index()
    env_counts.columns = ['environment', 'counts']
    fig = px.bar(env_counts, x='environment', y='counts', title="Builds by Environment")
    st.plotly_chart(fig)
