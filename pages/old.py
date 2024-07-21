import pandas as pd
import streamlit as st
import altair as alt

# Load data
df = pd.read_csv('data/new_mock_data.csv', parse_dates=["date_of_build", "log_on", "log_off"], dayfirst=True)

# Ensure date columns are correctly parsed
df['date_of_build'] = pd.to_datetime(df['date_of_build'], errors='coerce').dt.date
df['log_on'] = pd.to_datetime(df['log_on'], errors='coerce')
df['log_off'] = pd.to_datetime(df['log_off'], errors='coerce')

# Calculate time spent (in hours) for login-related rows
df['time_spent'] = (df['log_off'] - df['log_on']).dt.total_seconds() / 3600
df['time_spent'] = df['time_spent'].fillna(0)  # Replace NaNs with 0

# Separate build-related rows and login-related rows
builds_df = df[df['log_on'].isna() & df['log_off'].isna()]
logins_df = df[df['log_on'].notna() & df['log_off'].notna()]

# Group by project and date to get the total time spent and number of logins for each project
time_spent_per_project = logins_df.groupby(['projname', logins_df['log_on'].dt.date]).agg(
    total_time_spent=('time_spent', 'sum'),
    logins_count=('log_on', 'count')
).reset_index()
time_spent_per_project.columns = ['projname', 'date', 'total_time_spent', 'logins_count']

# Calculate the total time spent and total logins for each project
total_metrics_per_project = time_spent_per_project.groupby('projname').agg(
    total_time_spent=('total_time_spent', 'sum'),
    logins_count=('logins_count', 'sum')
).reset_index()

# Add a selectbox for interval selection in the sidebar
interval = st.sidebar.selectbox("Select Interval", ["daily", "weekly", "monthly"])

# Resample data based on selected interval
time_spent_per_project['date'] = pd.to_datetime(time_spent_per_project['date'])
if interval == 'weekly':
    resampled_time_spent = time_spent_per_project.set_index('date').groupby('projname').resample('W').sum().reset_index()
elif interval == 'monthly':
    resampled_time_spent = time_spent_per_project.set_index('date').groupby('projname').resample('M').sum().reset_index()
else:
    resampled_time_spent = time_spent_per_project

# Add a selectbox for metric selection for project popularity
popularity_metric = st.sidebar.selectbox("Select Metric for Project Popularity", ["Total Time Spent", "Number of Logins"])

# Sort projects based on the selected popularity metric
if popularity_metric == "Total Time Spent":
    sorted_projects = total_metrics_per_project.sort_values(by='total_time_spent', ascending=False)['projname']
else:
    sorted_projects = total_metrics_per_project.sort_values(by='logins_count', ascending=False)['projname']

# Add a selectbox to select a project from the sorted list
selected_project = st.selectbox("Select Project", options=sorted_projects)

# Filter data for the selected project
project_data = resampled_time_spent[resampled_time_spent['projname'] == selected_project]
project_logins = logins_df[logins_df['projname'] == selected_project]
project_builds = builds_df[builds_df['projname'] == selected_project]

# Display metrics for the selected project
st.write(f"Metrics for {selected_project}")
st.write("Total Time Spent:", project_data['total_time_spent'].sum())
st.write("Number of Logins:", project_data['logins_count'].sum())

# Create visualizations for the selected project
project_time_chart = alt.Chart(project_data).mark_line().encode(
    x='date:T',
    y='total_time_spent:Q',
    tooltip=['date:T', 'total_time_spent:Q']
).properties(
    title=f'Total Time Spent Over Time for {selected_project}',
    width=700,
    height=400
)

project_logins_chart = alt.Chart(project_data).mark_bar().encode(
    x='date:T',
    y='logins_count:Q',
    tooltip=['date:T', 'logins_count:Q']
).properties(
    title=f'Number of Logins Over Time for {selected_project}',
    width=700,
    height=400
)

project_builds_chart = alt.Chart(project_builds).mark_bar().encode(
    x='date_of_build:T',
    y='duration:Q',
    tooltip=['date_of_build:T', 'duration:Q']
).properties(
    title=f'Build Durations for {selected_project}',
    width=700,
    height=400
)

# Display the visualizations in Streamlit
st.altair_chart(project_time_chart, use_container_width=True)
st.altair_chart(project_logins_chart, use_container_width=True)
st.altair_chart(project_builds_chart, use_container_width=True)

# Create the first column for the selected metric per project over time
col1, col2 = st.columns(2)

with col1:
    # Add a selectbox for metric selection for top projects
    metric = st.selectbox("Select Metric", ["Total Time Spent", "Number of Logins"])

    # Filter top 10 projects based on the selected metric
    if metric == "Total Time Spent":
        top_projects = total_metrics_per_project.sort_values(by='total_time_spent', ascending=False).head(10)
        y_axis = 'total_time_spent'
        title = 'Total Time Spent by Top 10 Projects'
    else:
        top_projects = total_metrics_per_project.sort_values(by='logins_count', ascending=False).head(10)
        y_axis = 'logins_count'
        title = 'Number of Logins by Top 10 Projects'

    # Filter the original data to include only the top projects based on the selected metric
    filtered_time_spent = resampled_time_spent[resampled_time_spent['projname'].isin(top_projects['projname'])]

    # Visualization: Selected metric per project over time for top projects
    project_metric_chart = alt.Chart(filtered_time_spent).mark_line().encode(
        x='date:T',
        y=alt.Y(f'{y_axis}:Q', title=metric),
        color='projname:N',
        tooltip=['projname:N', 'date:T', f'{y_axis}:Q']
    ).properties(
        title=title,
        width=350,
        height=400
    )
    st.altair_chart(project_metric_chart, use_container_width=True)

with col2:
    # Group by project and date to get the total time spent on each project
    time_spent_per_project_all = df.groupby(['projname', df['log_on'].dt.date]).agg({'time_spent': 'sum'}).reset_index()
    time_spent_per_project_all.columns = ['projname', 'date', 'total_time_spent']

    # Group by date to get the total time spent across all projects
    total_time_spent = df.groupby(df['log_on'].dt.date).agg({'time_spent': 'sum'}).reset_index()
    total_time_spent.columns = ['date', 'total_time_spent']

    # Calculate the total time spent at the beginning and end of the timeframe
    start_date = time_spent_per_project_all['date'].min()
    end_date = time_spent_per_project_all['date'].max()
    start_time_spent = time_spent_per_project_all[time_spent_per_project_all['date'] == start_date]
    end_time_spent = time_spent_per_project_all[time_spent_per_project_all['date'] == end_date]
    growth = pd.merge(start_time_spent, end_time_spent, on='projname', suffixes=('_start', '_end'))
    growth['growth'] = growth['total_time_spent_end'] - growth['total_time_spent_start']
    top_growing_projects = growth.sort_values(by='growth', ascending=False).head(10)['projname']
    filtered_time_spent_growing = time_spent_per_project_all[time_spent_per_project_all['projname'].isin(top_growing_projects)]

    # Visualization: Total time spent per project over time for top growing projects
    project_time_chart = alt.Chart(filtered_time_spent_growing).mark_line().encode(
        x='date:T',
        y='total_time_spent:Q',
        color='projname:N',
        tooltip=['projname:N', 'date:T', 'total_time_spent:Q']
    ).properties(
        title='Total Time Spent on Top Growing Projects Over Time',
        width=350,
        height=400
    )

    # Visualization: Total time spent across all projects over time
    total_time_chart = alt.Chart(total_time_spent).mark_line().encode(
        x='date:T',
        y='total_time_spent:Q',
        tooltip=['date:T', 'total_time_spent:Q']
    ).properties(
        title='Total Time Spent Across All Projects Over Time',
        width=350,
        height=400
    )

    # Integrate the charts into your Streamlit app
