from files import donut
import pandas as pd
import altair as alt
import streamlit as st


def convert_duration(duration):
    try:
        h, m, s = map(int, duration.split(':'))
        return h + m / 60 + s / 3600
    except:
        return 0


def show(df):
    # Convert duration from hh:mm:ss to total hours
    df['duration_of_build'] = df['duration_of_build'].apply(convert_duration)

    # Calculate regional exposure metrics
    total_builds = df.shape[0]
    regions = ['AMER', 'EMEA', 'APAC']
    region_data = {region: df[df['region'] == region] for region in regions}
    region_metrics = {}

    for region, data in region_data.items():
        if data.shape[0]:
            region_metrics[region] = {
                'exposure': (data.shape[0] / total_builds) * 100,
                'success_rate': (data[data['status'] == 'Success'].shape[0] / data.shape[0]) * 100,
                'unique_projects': data['projname'].nunique()
            }

    # Setting up Streamlit columns for visualization
    inners = st.columns(3)

    # Loop through each region and display metrics
    for i, (region, metrics) in enumerate(region_metrics.items()):
        with inners[i]:
            st.markdown(f'##### {region} Metrics')
            st.altair_chart(donut.make_donut(round(metrics['exposure']), 'Build Exposure', 'blue'))
            st.markdown(f'##### {region} Number of Builds')
            st.altair_chart(donut.make_donut(round(metrics['success_rate']), 'Success Rate', 'orange'))
            st.metric("Unique Projects", metrics['unique_projects'])

# Assuming df is already loaded and cleaned before passing to show function
# Example usage:
# df = pd.read_csv('your_data.csv')
# show(df)

def calculate_metrics(total_df, filtered_df):
    # Number of Builds
    number_of_builds = filtered_df.shape[0]

    # Unique Projects
    total_projects = total_df['projname'].nunique()
    filtered_projects = filtered_df['projname'].nunique()
    new_projects = filtered_projects - total_df[total_df['projname'].isin(filtered_df['projname'])]['projname'].nunique()

    # Total Developers
    total_developers = filtered_df['user_id'].nunique()

    # New Developers
    total_dev_ids = set(total_df['user_id'])
    filtered_dev_ids = set(filtered_df['user_id'])
    new_developers = len(filtered_dev_ids - total_dev_ids)

    return {
        "number_of_builds": number_of_builds,
        "new_projects": new_projects,
        "total_developers": total_developers,
        "new_developers": new_developers
    }
    new_key.show(filtered_builds_df)

    metrics = new_key.calculate_metrics(builds_df, filtered_builds_df)

    st.metric("Number of Builds", metrics["number_of_builds"])
    st.metric("New Projects Created", metrics["new_projects"])
    st.metric("Total Developers", metrics["total_developers"])
    st.metric("New Developers", metrics["new_developers"])

