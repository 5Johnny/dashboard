import pandas as pd
import streamlit as st
import altair as alt

# Load data
df = pd.read_csv('data/data.csv', parse_dates=["date_of_build", "log_on", "log_off"], dayfirst=True)

# Ensure date columns are correctly parsed
df['date_of_build'] = pd.to_datetime(df['date_of_build'], errors='coerce')
df['log_on'] = pd.to_datetime(df['log_on'], errors='coerce')
df['log_off'] = pd.to_datetime(df['log_off'], errors='coerce')

# Sort the data by project name and build date
df = df.sort_values(by=['projname', 'date_of_build'])

# Calculate durations in each environment
df['next_env_date'] = df.groupby('projname')['date_of_build'].shift(-1)
df['duration_in_env'] = (df['next_env_date'] - df['date_of_build']).dt.days

# Handle last stage durations as zero (since there's no next stage)
df['duration_in_env'] = df['duration_in_env'].fillna(0).astype(int)

# Filter relevant columns
builds_df = df[['projname', 'environment', 'date_of_build', 'duration_in_env']]

# Calculate average, shortest, and longest times for each environment
env_stats = builds_df.groupby('environment')['duration_in_env'].agg(['mean', 'min', 'max']).reset_index()
env_stats.columns = ['environment', 'average_time', 'shortest_time', 'longest_time']

# Visualize the progression and statistics for each environment
progression_chart = alt.Chart(builds_df).mark_bar().encode(
    x='projname:N',
    y='duration_in_env:Q',
    color='environment:N',
    tooltip=['projname:N', 'environment:N', 'duration_in_env:Q']
).properties(
    title='Time Spent in Each Environment by Project',
    width=700,
    height=400
)

# Visualize average, shortest, and longest times for each environment
stats_chart = alt.Chart(env_stats).transform_fold(
    ['average_time', 'shortest_time', 'longest_time'],
    as_=['statistic', 'value']
).mark_bar().encode(
    x='environment:N',
    y='value:Q',
    color='statistic:N',
    tooltip=['environment:N', 'statistic:N', 'value:Q']
).properties(
    title='Average, Shortest, and Longest Time in Each Environment',
    width=700,
    height=400
)

# Display the charts in Streamlit
st.altair_chart(progression_chart, use_container_width=True)
st.altair_chart(stats_chart, use_container_width=True)
