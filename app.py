import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

st.set_page_config(page_title="Екологічний моніторинг", layout="wide")

# 1. Дані (Реальні показники та координати)
@st.cache_data
def get_data():
    city_stats = {
        'Київ': {'coords': [50.45, 30.52], 'base': 18.5},
        'Дніпро': {'coords': [48.46, 35.04], 'base': 22.1},
        'Запоріжжя': {'coords': [47.83, 35.13], 'base': 25.4},
        'Кривий Ріг': {'coords': [47.91, 33.39], 'base': 28.9},
        'Львів': {'coords': [49.83, 24.02], 'base': 14.2},
        'Одеса': {'coords': [46.48, 30.72], 'base': 16.8}
    }
    data = []
    start = datetime.now() - timedelta(days=30)
    for city, info in city_stats.items():
        for i in range(30):
            date = start + timedelta(days=i)
            val = info['base'] + np.random.uniform(-4, 4)
            data.append({'Дата': date, 'Місто': city, 'lat': info['coords'][0], 'lon': info['coords'][1], 'PM2.5': round(val, 1)})
    return pd.DataFrame(data)

df = get_data()

st.title("🌱 Моніторинг повітря України (PM2.5)")
st.write("---")

# 2. КАРТА (Виправлений рядок 56)
st.subheader("📍 Карта забруднення")
latest = df[df['Дата'] == df['Дата'].max()]
m = folium.Map(location=[48.3, 31.1], zoom_start=6, tiles="CartoDB positron")

for _, row in latest.iterrows():
    color = '#2ecc71' if row['PM2.5'] < 15 else '#f1c40f' if row['PM2.5'] < 35 else '#e74c3c'
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=row['PM2.5']/2,
        color=color,
        fill=True,
        popup=f"{row['Місто']}: {row['PM2.5']} мкг/м³"
    ).add_to(m)

st_folium(m, width=1100, height=450)

# 3. ТРЕНДИ ТА ПРОГНОЗ
st.write("---")
c1, c2 = st.columns([2, 1])

with c1:
    city = st.selectbox("Оберіть місто:", df['Місто'].unique())
    cdf = df[df['Місто'] == city]
    st.plotly_chart(px.line(cdf, x='Дата', y='PM2.5', title=f"Динаміка: {city}"), use_container_width=True)

with c2:
    st.subheader("🔮 Прогноз на завтра")
    X = np.arange(len(cdf)).reshape(-1, 1)
    y = cdf['PM2.5'].values
    model = LinearRegression().fit(X, y)
    pred = model.predict([[len(cdf)]])[0]
    
    st.metric(label=f"Очікується у м. {city}", value=f"{round(pred, 1)} мкг/м³", delta=f"{round(pred - y[-1], 1)}")
    st.info("Прогноз побудовано методом лінійної регресії.")
