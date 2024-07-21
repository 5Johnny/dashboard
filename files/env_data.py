import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px

def main(df, builds_df):
    ### Top Apps Dataframe

    if not df.empty:
        # Display top apps based on total time spent
        top_apps_data = df.groupby(['projname'])['total_time_spent'].sum().reset_index(name='total_time_spent').sort_values(by='total_time_spent', ascending=False)
        st.dataframe(top_apps_data,
                     column_order=["projname", "total_time_spent"],
                     hide_index=True,
                     column_config={
                         "projname": st.column_config.TextColumn("Project Name"),
                         "total_time_spent": st.column_config.ProgressColumn(
                             "Time Spent (hours)",
                             format='',
                             min_value=0,
                             max_value=max(top_apps_data['total_time_spent'])
                         )
                     })

        st.write("")
        st.write("")
        st.write("")
        st.write("")

        #### Select a Project
        project_names = top_apps_data['projname'].unique()
        selected_project = st.selectbox('##### Select a project:', project_names, index=None)

        #### Show time spent on each project
        if selected_project:
            project_data = df[df['projname'] == selected_project]
            st.write("")
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

            # Filter builds_df for the selected project
            selected_builds = builds_df[builds_df['projname'] == selected_project]

            # Calculate the number of days in each environment
            env_durations = selected_builds.groupby('environment').agg(
                first_build=('date_of_build', 'min'),
                last_build=('date_of_build', 'max')
            ).reset_index()
            env_durations['days_in_env'] = (env_durations['last_build'] - env_durations['first_build']).dt.days

            # Bar chart for the number of days in each environment
            fig = px.bar(env_durations, x='environment', y='days_in_env',
                         title=f'Days in Each Environment for {selected_project}',
                         labels={'days_in_env': 'Days in Environment', 'environment': 'Environment'})
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.write("No project selected")
    else:
        st.markdown("# You filtered too much!!!")
        st.markdown("## No App Data to show")
