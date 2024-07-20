from files import filter
import pandas as pd
import altair as alt
import datetime
from datetime import timezone 
from datetime import date

def scatter(df, periodic_filter, selected_colors):
    if not df.empty:
        # Filter the date periodic timestamp
        scatter_data = filter.groupby(df, ['date_of_build'])
        scatter_data['date_of_build'] = pd.to_datetime(scatter_data['date_of_build']) 
        scatter_data['date_of_build'] = scatter_data['date_of_build'].dt.to_period(periodic_filter[0])
        scatter_data = scatter_data.groupby('date_of_build')[['build_count']].sum().sort_values('date_of_build', ascending = True).reset_index()
        
        
        if len(df['date_of_build']):
            smallest_date = scatter_data["date_of_build"].min().strftime("%d-%m-%Y")
            largest_date = scatter_data["date_of_build"].max().strftime("%d-%m-%Y")

        ## Create scatter plot using Altair
            scatter_plot = alt.Chart(scatter_data).mark_point(color=selected_colors[1]).encode(
                x=alt.X('date_of_build:T', title='Date'),
                y=alt.Y('build_count:Q', title='Number of Builds'),
                tooltip=['date_of_build:T', 'build_count:Q']
            ).properties(
                title=f'Developer Usage - No. of Builds:   {smallest_date} to {largest_date}.',
                height=400
            )
            # Add a smooth trendline using Loess smoothing
            trendline = scatter_plot.transform_loess(
                'date_of_build', 'build_count'
            ).mark_line(color=selected_colors[3])
            chart = scatter_plot + trendline
            chart = chart.configure_title(fontSize = 23, orient = 'top', anchor = 'middle' )
            return chart
    return alt.Chart().mark_bar().encode()


