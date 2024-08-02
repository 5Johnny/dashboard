from files import donut
import plotly.express as px
import altair as alt
import streamlit as st

def show(df, selected_colors):
    colour1 = [selected_colors[3], selected_colors[5]]
    colour2 = [selected_colors[2], selected_colors[4]]
    amer_exposure = 0
    emea_exposure = 0
    apac_exposure = 0
    if df.shape[0]:
        amer_exposure = (df[df['region'] == 'AMER'].shape[0] / df.shape[0]) * 100
        emea_exposure = (df[df['region'] == 'EMEA'].shape[0] / df.shape[0]) * 100
        apac_exposure = (df[df['region'] == 'APAC'].shape[0] / df.shape[0]) * 100

    inners = st.columns(2)
    with inners[0]:
        st.markdown('##### AMER Exposure')
        st.altair_chart(donut.make_donut(round(amer_exposure), 'New Users this month', colour2))
        st.markdown('##### EMEA Exposure')
        st.altair_chart(donut.make_donut(round(emea_exposure), 'New Users this month', colour1))
        st.markdown('##### APAC Exposure')
        st.altair_chart(donut.make_donut(round(apac_exposure), 'New Users this month', colour2))
    with inners[1]:
        print(df)
        st.markdown('##### Dev Projects')
        st.altair_chart(donut.make_donut(10, 'New Users this month', colour1, False))
        st.markdown('##### Stg Builds')
        st.altair_chart(donut.make_donut(34, 'New Users this month', colour2, False))
        st.markdown('##### Metric 6')
        st.altair_chart(donut.make_donut(50, 'New Users this month', colour1, False))
        
