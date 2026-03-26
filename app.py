import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. Налаштування сторінки
st.set_page_config(page_title="Система оцінки ризику", layout="wide")

# 2. Формування CSV даних (фінансові, податкові, публічні ознаки)
@st.cache_data
def get_data():
    data = {
        'Компанія': ['ТОВ "Альфа"', 'ПП "Браво"', 'ТОВ "Гамма"', 'АТ "Дельта"', 'ТОВ "Епсилон"'],
        'Борг_млн': [0.2, 5.5, 1.2, 10.1, 0.1],         # Фінансова ознака
        'Податковий_борг': [0, 1, 0, 1, 0],            # Податкова (0 - ні, 1 - так)
        'Судові_справи': [1, 18, 4, 30, 2],            # Публічна ознака
        'Стаж_років': [12, 2, 7, 1, 20]                # Додатковий фактор
    }
    return pd.DataFrame(data)

df = get_data()

# 3. Обчислення інтегрального індексу ризику (0-100)
def calculate_integral_risk(row):
    # Формула: вага кожного фактора
    score = (row['Борг_млн'] * 4) + (row['Податковий_борг'] * 35) + (row['Судові_справи'] * 1.5) - (row['Стаж_років'] * 1.5)
    return int(min(max(score, 0), 100)) # Результат цілим числом від 0 до 100

df['Індекс_ризику'] = df.apply(calculate_integral_risk, axis=1)

# 4. Інтерфейс додатка
st.title("🛡️ Моніторинг ризиків підприємств")
st.markdown("---")

# Вибір компанії
selected_company = st.selectbox("Оберіть компанію для аналізу:", df['Компанія'])
c_data = df[df['Компанія'] == selected_company].iloc[0]
risk_score = c_data['Індекс_ризику']

# 5. Візуалізація Gauge-chart (Виправлено для стабільної роботи)
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = risk_score,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': f"Рівень ризику: {selected_company}", 'font': {'size': 24}},
    gauge = {
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "black"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 40], 'color': '#69b3a2'},   # Зелений (Низький)
            {'range': [40, 70], 'color': '#ff
