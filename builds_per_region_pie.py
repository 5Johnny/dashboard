from files import filter
import pandas as pd
import altair as alt
import datetime
from datetime import timezone 
from datetime import date
# Pie Chart
def pie(df, selected_color_theme='magma'):
        chart =alt.Chart(df).mark_arc(

        ).encode(
            theta=alt.Theta(field="build_count", type="quantitative"),
            color=alt.Color(field="region", type="nominal",
            scale = alt.Scale(scheme = selected_color_theme))).properties(
                title = "Current Builds per Region",
            )   
        chart = chart.configure_title(fontSize = 23, orient = 'top', anchor = 'middle' )
        chart = chart
        return chart