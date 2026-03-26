import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Налаштування інтерфейсу
st.set_page_config(page_title="GitHub Monitor", layout="wide")
st.title("📊 Моніторинг проєктів у GitHub")

# Введення імені користувача (як на твоєму скріншоті)
username = st.text_input("Введіть нікнейм користувача GitHub:", value="streamlit")

# 1. ОТРИМАННЯ ДАНИХ ЧЕРЕЗ GITHUB API (Пункт 1 ТЗ)
@st.cache_data
def get_data(user):
    # Отримуємо основні дані репозиторіїв
    url = f"https://api.github.com/users/{user}/repos?per_page=100"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

if username:
    data = get_data(username)
    
    if data:
        # Перетворюємо JSON у таблицю для аналізу
        df = pd.DataFrame(data)
        # Вибираємо: назва, зірки (popularity), форки (PR/community), задачі (issues)
        df = df[['name', 'stargazers_count', 'forks_count', 'open_issues_count']]
        df.columns = ['Проєкт', 'Зірки ⭐', 'Форки 🍴', 'Issues 🛠']

        # 2. ПОБУДОВА ГРАФА АКТИВНОСТІ (Пункт 2 ТЗ)
        st.subheader("📈 Граф активності (Issues vs Stars)")
        # Бульбашкова діаграма: показує зв'язок між популярністю та кількістю задач
        fig_activity = px.scatter(df, x='Зірки ⭐', y='Issues 🛠', size='Форки 🍴',
                                 hover_name='Проєкт', color='Issues 🛠',
                                 labels={'Issues 🛠': 'Відкриті задачі', 'Зірки ⭐': 'Кількість зірок'})
        st.plotly_chart(fig_activity, use_container_width=True)

        # 3. РЕЙТИНГ ПРОЄКТІВ ЗА ЗІРКАМИ (Пункт 3 ТЗ)
        st.subheader("🏆 Рейтинг проєктів за популярністю")
        top_10 = df.sort_values('Зірки ⭐', ascending=False).head(10)
        fig_stars = px.bar(top_10, x='Зірки ⭐', y='Проєкт', orientation='h', 
                           color='Зірки ⭐', text='Зірки ⭐')
        fig_stars.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_stars, use_container_width=True)

        # 4. АНАЛІЗ ДИНАМІКИ РОЗРОБКИ (Пункт 4 ТЗ)
        st.subheader("🔍 Аналіз показників")
        c1, c2 = st.columns(2)
        with c1:
            # Аналіз через середню кількість задач
            avg_issues = round(df['Issues 🛠'].mean(), 1)
            st.metric("Середня активність (Issues)", avg_issues)
        with c2:
            # Аналіз через загальну залученість
            total_forks = df['Форки 🍴'].sum()
            st.metric("Загальна кількість форків", total_forks)

        st.write("---")
        st.dataframe(df.sort_values('Зірки ⭐', ascending=False), use_container_width=True)
    else:
        st.error("Користувача не знайдено або перевищено ліміт API.")
