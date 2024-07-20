from files import filter
import pandas as pd
import altair as alt
import streamlit as st



#filtered_logins_df
def main(df):
    ### Top Apps Dataframe
    
    if not df.empty:
        top_apps_data = df.groupby(['projname'])['total_time_spent'].sum().reset_index(name='total_time_spent').sort_values(by='total_time_spent', ascending=False)
        st.dataframe(top_apps_data ,
                    column_order=("projname","total_time_spent"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "projname": st.column_config.TextColumn(
                            "Project Name",
                        ),
                        "total_time_spent": st.column_config.ProgressColumn(
                            "Time Spent (hours)",
                            format='',
                            min_value=0,
                            max_value=max(top_apps_data.total_time_spent),
                        )}
                    )
        
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        
        #### Select a Project
        project_names = top_apps_data['projname'].unique()
        selected_project = st.selectbox('##### Select a project:', project_names, index = None)

        #### Show time spent on each project
        if selected_project:
            project_data = df[df['projname'] == selected_project]
            st.write("")
            project_time_chart = alt.Chart(project_data).mark_line().encode(
            x='log_on_date:T',
            y='total_time_spent:Q',
            tooltip=['log_on_date:T', 'total_time_spent:Q']
        ).properties(
            title=f'Consumer Usage - {selected_project.capitalize()}',
            width=700,
            height=400
        )
            project_time_chart = project_time_chart.configure_title(fontSize = 20, orient = 'top', anchor = 'middle' )
            st.altair_chart(project_time_chart, use_container_width=True) 
        else:
            st.write("No project selected")
    else:
        st.markdown("# You filtered too much!!!")
        st.markdown("## No App Data to show")