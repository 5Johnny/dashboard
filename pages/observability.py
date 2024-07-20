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
    page_title="Finstrat Observability Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

######################
# CSS styling
st.markdown("""
<style>
.block-container {
    padding-top: 3rem;
    padding-bottom: 0rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
    color: white;
}

[data-testid="stMetricLabel"] {
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
}

[data-testid="element-container"] {
    text-align: center;
}

[data-testid="stFullScreenFrame"] {
    text-align: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}
</style>
""", unsafe_allow_html=True)

######################
# Load data
df = pd.read_csv('data/new_mock_data.csv', parse_dates=["date_of_build"], dayfirst=True)
df["date_of_build"] = (df["date_of_build"]).dt.date

######################
# Sidebar
with st.sidebar:
    st.title('Finstrat Observability Dashboard')

    with st.expander("☰ Menu"):
        st.page_link("fin_dashboard_streamlit.py", label="Home", icon="🏠", use_container_width=True)
        st.page_link("./pages/observability.py", label="Newer Dashboard", icon="📊", use_container_width=True)

    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input("Date Range", [], format="DD/MM/YYYY")
    env_filter = st.sidebar.multiselect("Environment", options=df['environment'].unique())
    status_filter = st.sidebar.multiselect("Status", options=df['status'].unique())

    st.sidebar.header("Colour :smile:")
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.sidebar.selectbox("Select a color theme", color_theme_list)
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
    selected_color1 = selected_colors[2]
    selected_color2 = selected_colors[4]

    if st.button("Clear Filters"):
        date_range = []
        env_filter = []
        status_filter = []

######################
# Filter data
def filter_df(df=df, date_range=date_range, env_filter=env_filter, status_filter=status_filter):
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['date_of_build'] >= start_date) & (df['date_of_build'] <= end_date)]
        print("Filtering Date", len(df))

    if env_filter:
        df = df[df['environment'].isin(env_filter)]
        print("Filtering Environment", len(df))

    if status_filter:
        df = df[df['status'].isin(status_filter)]
        print("Filtering Status", len(df))

    return df

filtered = filter_df()


# Donut chart
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F39C12', '#875A12']
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']

    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100 - input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)

    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700,
                          fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text

# Prepare data for the scatter plot
def prepare_scatter_data(df):
    scatter_data = df.groupby('date_of_build').size().reset_index(name='build_count')
    return scatter_data

def create_scatter(df):
    scatter_data = prepare_scatter_data(df)
    ## Create scatter plot using Altair
    scatter_plot = alt.Chart(scatter_data).mark_point(color=selected_color1).encode(
        x=alt.X('date_of_build:T', title='Date'),
        y=alt.Y('build_count:Q', title='Number of Builds'),
        tooltip=['date_of_build:T', 'build_count:Q']
    ).properties(
        title='Number of Builds Over Time',
        width=600,
        height=400
    )

    # Add a smooth trendline using Loess smoothing
    trendline = scatter_plot.transform_loess(
        'date_of_build', 'build_count'
    ).mark_line(color=selected_color2)

    st.altair_chart(scatter_plot + trendline, use_container_width=True)


# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

# Count unique projects in 'dev' environment
def count_new_projects(df, env):
    dev_projects = df[df['environment'] == env]['projname'].nunique()
    return dev_projects

with col[0]:
    successful_builds = filtered['status'].value_counts().get('Success', 0)
    print(len(filtered))
    st.title("Current")
    st.markdown("#### Monthly Metrics")
    st.metric("Successful Builds", successful_builds, "")
    st.metric("New Projects in Dev", count_new_projects(filtered, 'dev'))
    st.metric("New Projects in Prd", count_new_projects(filtered, 'prod'))
    st.metric("New Projects in Stg", count_new_projects(filtered, 'stg'))
    st.markdown("#### Cool Percentages")

    inners = st.columns(2)
    with inners[0]:
        st.markdown("#### Metric 1")
        st.altair_chart(make_donut(-7, 'New Users this month', 'blue'))
        st.markdown("#### Metric 3")
        st.altair_chart(make_donut(27, 'New Users this month', 'orange'))

    with inners[1]:
        st.markdown("#### Metric 2")
        st.altair_chart(make_donut(10, 'New Users this month', 'red'))
        st.markdown("#### Metric 4")
        st.altair_chart(make_donut(54, 'New Users this month', 'green'))


with col[1]:
    st.markdown("#### Team Usage")
    chart_data = pd.DataFrame(
        np.random.rand(9, 4),
        index=['FINSTRAT', 'DAG', 'FCQ', 'GCA', 'MBSQ', 'GMLAB', 'MLFLOW', 'TRS', 'USDEC']
    )
    data = pd.melt(chart_data.reset_index(), id_vars=['index'])

    # Horizontal stacked bar chart
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X('value', type='quantitative', title=''),
            y=alt.Y('index', type='nominal', title=''),
            color=alt.Color('variable', scale=alt.Scale(scheme=selected_color_theme)),
            order=alt.Order('variable', sort='descending'),
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)


    create_scatter(filtered)


    # Prepare data for the team usage chart
    def prepare_team_usage_data(df, n=10):
        team_usage = df.groupby(['teamname', 'environment']).size().reset_index(name='count')
        team_usage_pivot = team_usage.pivot(index='teamname', columns='environment', values='count').fillna(0)
        team_usage_pivot['total'] = team_usage_pivot.sum(axis=1)
        team_usage_sorted = team_usage_pivot.sort_values(by='total', ascending=False).reset_index().head(n)
        return team_usage_sorted

    team_usage_data = prepare_team_usage_data(filtered)

    # Melt the data for Altair
    melted_team_usage = pd.melt(team_usage_data, id_vars=['teamname'], value_vars=['dev', 'stg', 'prod'], var_name='environment', value_name='count')

    # Create the horizontal stacked bar chart
    chart = (
        alt.Chart(melted_team_usage)
        .mark_bar()
        .encode(
            x=alt.X('count:Q', title=''),
            y=alt.Y('teamname:N', title='Team', sort=alt.EncodingSortField(field='total', order='descending')),
            color=alt.Color('environment:N', scale=alt.Scale(scheme=selected_color_theme), title='Environment'),
            order=alt.Order('environment', sort='descending'),
            tooltip=['teamname:N', 'environment:N', 'count:Q']
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    # Prepare data for the line graph

# Prepare data for the scatter plot
