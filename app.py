import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. Налаштування сторінки ---
st.set_page_config(page_title="Система оцінки ризику підприємств", layout="wide")

# --- 2. Створення бази даних (CSV ознаки згідно з умовою) ---
@st.cache_data
def load_data():
    # Фінансові (борг), Податкові (заборгованість), Публічні (суди) ознаки
    data = {
        'Назва підприємства': [
            'ТОВ "Вектор"', 'ПП "Оріон"', 'АТ "Старт"', 
            'ТОВ "Меркурій"', 'ПАТ "Зеніт"', 'ТОВ "Атлант"'
        ],
        'Борг (млн грн)': [0.2, 5.5, 1.1, 9.8, 0.05, 1.5],         # Фінансова ознака
        'Податковий борг': [0, 1, 0, 1, 0, 0],                   # Податкова (0-ні, 1-так)
        'Судові справи': [2, 18, 4, 35, 1, 6],                  # Публічна ознака
        'Стаж (років)': [10, 2, 8, 1, 15, 7]
    }
    return pd.DataFrame(data)

df = load_data()

# --- 3. Обчислення інтегрального індексу ризику ---
def calculate_risk(row):
    # Формула зі зваженими коефіцієнтами
    score = (row['Борг (млн грн)'] * 5) + (row['Податковий борг'] * 35) + (row['Судові справи'] * 1.5) - (row['Стаж (років)'] * 1.5)
    return int(min(max(score, 0), 100))

df['Індекс ризику'] = df.apply(calculate_risk, axis=1)

# --- 4. Інтерфейс ---
st.title("🛡️ Система оцінки ризику підприємств")
st.markdown("---")

# Вибір компанії
selected_company = st.selectbox("Оберіть компанію для аналізу:", df['Назва підприємства'])
c_data = df[df['Назва підприємства'] == selected_company].iloc[0]
risk_score = c_data['Індекс ризику']

col1, col2 = st.columns([1, 1])

with col1:
    # --- 5. Візуалізація: Gauge-chart ---
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_score,
        title = {'text': f"Рівень ризику: {selected_company}"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 40], 'color': "#2ecc71"},   # Низький (Зелений)
                {'range': [40, 70], 'color': "#f1c40f"}, # Середній (Жовтий)
                {'range': [70, 100], 'color': "#e74c3c"} # Високий (Червоний)
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'value': risk_score
            }
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Деталі перевірки")
    st.write(f"**Фінансовий борг:** {c_data['Борг (млн грн)']} млн грн")
    st.write(f"**Податковий борг:** {'⚠️ Є заборгованість' if c_data['Податковий борг'] == 1 else '✅ Відсутній'}")
    st.write(f"**Судові справи:** {c_data['Судові справи']} проваджень")
    
    if risk_score > 70:
        st.error("❗ ВИСОКИЙ РИЗИК: Рекомендується відмовити у співпраці.")
    elif risk_score > 40:
        st.warning("⚠️ СЕРЕДНІЙ РИЗИК: Потрібна додаткова перевірка документів.")
    else:
        st.success("✅ НИЗЬКИЙ РИЗИК: Контрагент надійний.")

# --- 6. Підсвічування компаній з високим ризиком (Умова №4) ---
st.markdown("---")
st.subheader("📊 Повний реєстр з маркуванням ризиків")

def highlight_risk(val):
    if val > 70: return 'background-color: #ffcccc; color: #cc0000; font-weight: bold'
    if val > 40: return 'background-color: #fff4cc'
    return ''

# Відображення таблиці з автоматичним підсвічуванням
st.dataframe(
    df.style.applymap(highlight_risk, subset=['Індекс ризику']),
    use_container_width=True
)
