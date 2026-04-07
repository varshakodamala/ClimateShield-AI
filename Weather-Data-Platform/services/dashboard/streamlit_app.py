import streamlit as st, pandas as pd
st.title("Weather Dashboard")
df = pd.read_csv("data/processed/weather.csv")
st.dataframe(df)
st.line_chart(df["temperature"])
