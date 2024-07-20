from files import filter
import pandas as pd
import altair as alt
import datetime
from datetime import timezone 
from datetime import date

# Prepare data for the team usage chart
def prepare_data(df, n):
    df = df.groupby('teamname').size().reset_index(name='total')
    team_usage_sorted = df.sort_values(by='total', ascending=False).head(n).reset_index(drop=True)
    return team_usage_sorted

def bar_chart(df, n, selected_color_theme='magma'):
    team_usage_data = prepare_data(df, n)

    melted_team_usage = pd.melt(team_usage_data, id_vars=['teamname'], value_vars=['total'], value_name='count')
    chart = (
        alt.Chart(melted_team_usage)
        .mark_bar()
        .encode(
            x=alt.X('count:Q', title=''),
            y=alt.Y('teamname:N', title='Team', sort=alt.EncodingSortField(field='total', order='descending')),
            color=alt.Color('count:Q', scale=alt.Scale(scheme=selected_color_theme), title='Count'),
            tooltip=['teamname:N', 'count:Q']
        )
        .properties(height=400)
    )
    return chart
