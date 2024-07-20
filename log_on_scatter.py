from files import filter
import pandas as pd
import altair as alt
import datetime
from datetime import timezone 
from datetime import date




def scatter(df, periodic_filter, time_count_filter, selected_colors):
    if not (df.empty):
        grouped_data = filter.merge_dates(df, periodic_filter)
        scatter_plot = alt.Chart(grouped_data).mark_point(color=selected_colors[3]).encode(
            x=alt.X(f'log_on_date:T', title='Date'),
            y=alt.Y(f'{time_count_filter}:Q', title='Time Spent'),
            tooltip=[f'log_on_date:T', f'{time_count_filter}:Q']
        ).properties(
            title=f'Consumer Usage - Time Spent:   {(grouped_data["log_on_date"].min().strftime("%d-%m-%Y"))} to {(grouped_data["log_on_date"].max().strftime("%d-%m-%Y"))}.',
            height=400
        )
        # Add a smooth trendline using Loess smoothing
        trendline = scatter_plot.transform_loess(
            f'log_on_date', f'{time_count_filter}'
        ).mark_line(color=selected_colors[5])
        chart = scatter_plot + trendline
        chart = chart.configure_title(fontSize = 23, orient = 'top', anchor = 'middle' )
        return chart
    return alt.Chart().mark_bar().encode()
