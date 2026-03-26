import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Налаштування сторінки
st.set_page_config(page_title="GitHub Monitor", layout="wide")

# 2. Отримання даних через GitHub API (Виконання умови 1)
@st.cache_data
def get_github_data(user):
    # Запит до API GitHub для отримання списку репозиторіїв
    url = f"https://api.github.com/users/{user}/repos?per_page=100"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

st.title("📊 Моніторинг проєктів у GitHub")
st.write("Аналітика репозиторіїв у реальному часі")

# Поле для введення нікнейму
username = st.text_input("Введіть нікнейм користувача GitHub:", value="streamlit")

if username:
    data = get_github_data(username)
    
    if data:
        # Створення таблиці (DataFrame)
        df = pd.DataFrame(data)
        # Вибираємо потрібні дані: назва, зірки, форки, відкриті задачі
        df = df[['name', 'stargazers_count', 'forks_count', 'open_issues_count']]
        df.columns = ['Проєкт', 'Зірки ⭐', 'Форки 🍴', 'Issues 🛠']

        # --- КРОК 2: РЕЙТИНГ ПРОЄКТІВ ЗА ЗІРКАМИ (Виконання умови 3) ---
        st.subheader("🏆 ТОП-10 проєктів за зірками")
        top_10 = df.sort_values('Зірки ⭐', ascending=False).head(10)
        fig_stars = px.bar(top_10, x='Зірки ⭐', y='Проєкт', orientation='h', 
                           color='Зірки ⭐', color_continuous_scale='Viridis')
        fig_stars.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_stars, use_container_width=True)

        # --- КРОК 3: ГРАФ АКТИВНОСТІ (Виконання умови 2) ---
        st.subheader("📈 Граф активності (Популярність vs Задачі)")
        # Бульбашкова діаграма: X - зірки, Y - Issues, Розмір - Форки
        fig_activity = px.scatter(df, x='Зірки ⭐', y='Issues 🛠', size='Форки 🍴',
                                 hover_name='Проєкт', color='Issues 🛠',
                                 title="Співвідношення зірок та активних задач")
        st.plotly_chart(fig_activity, use_container_width=True)

        # --- КРОК 4: АНАЛІЗ ДИНАМІКИ РОЗРОБКИ (Виконання умови 4) ---
        st.subheader("🔍 Аналіз показників розробки")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Кількість репозиторіїв", len(df))
        with col2:
            st.metric("Загальний рейтинг (зірок)", df['Зірки ⭐'].sum())
        with col3:
            avg_issues = round(df['Issues 🛠'].mean(), 1)
            st.metric("Сер. кількість задач (Issues)", avg_issues)

        st.write("---")
        st.write("### 📋 Повна таблиця даних")
        st.dataframe(df.sort_values('Зірки ⭐', ascending=False), use_container_width=True)
        
    else:
        st.error("Користувача не знайдено або перевищено ліміт запитів API.")
