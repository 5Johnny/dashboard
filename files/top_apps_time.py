import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px


def calculate_env_durations(build_df):
    build_df['date_of_build'] = pd.to_datetime(build_df['date_of_build'], errors='coerce')
    env_durations = build_df.groupby(['projname', 'environment']).agg(
        start_date=('date_of_build', 'min'),
        end_date=('date_of_build', 'max')
    ).reset_index()

    env_durations['days_in_env'] = (env_durations['end_date'] - env_durations['start_date']).dt.days

    env_durations_pivot = env_durations.pivot(index='projname', columns='environment',
                                              values='days_in_env').reset_index()
    env_durations_pivot.columns.name = None  # remove the index name
    env_durations_pivot.fillna(0, inplace=True)  # fill NaN with 0 for environments not present in the project

    for env in ['dev', 'stg', 'prd']:
        if env not in env_durations_pivot.columns:
            env_durations_pivot[env] = 0

    return env_durations_pivot


def display_metrics(env_durations_pivot):
    avg_dev = env_durations_pivot['dev'].mean()
    avg_stg = env_durations_pivot['stg'].mean()
    avg_prd = env_durations_pivot['prd'].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Time in Dev (days)", round(avg_dev, 2))
    with col2:
        st.metric("Average Time in Stg (days)", round(avg_stg, 2))
    with col3:
        st.metric("Average Time in Prd (days)", round(avg_prd, 2))


def prepare_top_apps_data(df, env_durations_pivot):
    top_apps_data = df.groupby(['projname'])['total_time_spent'].sum().reset_index(name='total_time_spent').sort_values(
        by='total_time_spent', ascending=False)
    top_apps_data = pd.merge(top_apps_data, env_durations_pivot, on='projname', how='left')
    top_apps_data = top_apps_data.replace([float('inf'), -float('inf')], 0).fillna(0)
    return top_apps_data


def display_top_apps_data(top_apps_data):
    st.dataframe(top_apps_data,
                 column_order=["projname", "total_time_spent", "dev", "stg", "prd"],
                 hide_index=True,
                 column_config={
                     "projname": st.column_config.TextColumn("Project Name"),
                     "total_time_spent": st.column_config.ProgressColumn(
                         "Time Spent (hours)",
                         format='',
                         min_value=0,
                         max_value=max(top_apps_data['total_time_spent'])
                     ),
                     "dev": st.column_config.NumberColumn(
                         "Days in Dev",
                         format='',
                         min_value=0,
                         max_value=max(top_apps_data['dev'])
                     ),
                     "stg": st.column_config.NumberColumn(
                         "Days in Stg",
                         format='',
                         min_value=0,
                         max_value=max(top_apps_data['stg'])
                     ),
                     "prd": st.column_config.NumberColumn(
                         "Days in Prd",
                         format='',
                         min_value=0,
                         max_value=max(top_apps_data['prd'])
                     )
                 })


def display_project_time_chart(df, selected_project):
    project_data = df[df['projname'] == selected_project]
    project_time_chart = alt.Chart(project_data).mark_line().encode(
        x='log_on_date:T',
        y='total_time_spent:Q',
        tooltip=['log_on_date:T', 'total_time_spent:Q']
    ).properties(
        title=f'Time Spent Over Time - {selected_project.capitalize()}',
        width=700,
        height=400
    )
    project_time_chart = project_time_chart.configure_title(fontSize=20, orient='top', anchor='middle')
    st.altair_chart(project_time_chart, use_container_width=True)


def display_env_barchart(project_data, selected_project):
    env_data = project_data.groupby('environment').agg(
        total_time_spent=('total_time_spent', 'sum'),
        logins_count=('logins_count', 'sum')
    ).reset_index()

    fig = px.bar(env_data, x='environment', y=['total_time_spent', 'logins_count'],
                 title=f'Time Spent and Logins Count per Environment for {selected_project}',
                 labels={'environment': 'Environment'},
                 barmode='group')
    st.plotly_chart(fig, use_container_width=True)


def main(df, build_df):
    if not df.empty:
        env_durations_pivot = calculate_env_durations(build_df)
        display_metrics(env_durations_pivot)
        top_apps_data = prepare_top_apps_data(df, env_durations_pivot)
        display_top_apps_data(top_apps_data)

        st.write("")
        st.write("")
        st.write("")
        st.write("")

        project_names = top_apps_data['projname'].unique()
        selected_project = st.selectbox('##### Select a project:', project_names, index=None)

        if selected_project:
            project_data = df[df['projname'] == selected_project]
            display_project_time_chart(df, selected_project)
            display_env_barchart(project_data, selected_project)
        else:
            st.write("No project selected")
    else:
        st.markdown("# You filtered too much!!!")
        st.markdown("## No App Data to show")
