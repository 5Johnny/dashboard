from files import donut
import plotly.express as px
import altair as alt
import streamlit as st

def show(df):
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
        st.altair_chart(donut.make_donut(round(amer_exposure), 'New Users this month', 'blue'))
        st.markdown('##### EMEA Exposure')
        st.altair_chart(donut.make_donut(round(emea_exposure), 'New Users this month', 'orange'))
        st.markdown('##### APAC Exposure')
        st.altair_chart(donut.make_donut(round(apac_exposure), 'New Users this month', 'green'))
    with inners[1]:
        st.markdown('##### Metric 2')
        st.altair_chart(donut.make_donut(10, 'New Users this month', 'red'))
        st.markdown('##### Metric 4')
        st.altair_chart(donut.make_donut(34, 'New Users this month', 'orange'))
        st.markdown('##### Metric 6')
        st.altair_chart(donut.make_donut(99, 'New Users this month', 'green'))