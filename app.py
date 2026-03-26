import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Налаштування сторінки
st.set_page_config(page_title="GitHub Project Monitor", layout="wide")

# 2. Функція для отримання даних через GitHub API
@st.cache_data(ttl=3600) # Кешуємо дані на годину, щоб не перевищити ліміти API
def get_github_data(username):
    # Отримуємо список публічних репозиторіїв
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# 3. Інтерфейс
st.title("📊 Моніторинг проєктів у GitHub")
st.markdown("---")

# Ввід імені користувача (наприклад: streamlit, google, apple або твій нік)
target_user = st.text_input("Введіть нікнейм користувача GitHub:", value="streamlit")

if target_user:
    with st.spinner('Отримання даних з GitHub API...'):
        raw_data = get_github_data(target_user)
    
    if raw_data:
        # Створюємо DataFrame з потрібними нам полями
        df = pd.DataFrame(raw_data)
        
        # Вибираємо тільки необхідні колонки для аналізу
        # stargazers_count (зірки), forks_count (форки), open_issues_count (активні задачі)
        analysis_df = df[['name', 'stargazers_count', 'forks_count', 'open_issues_count', 'updated_at']]
        analysis_df.columns = ['Проєкт', 'Зірки ⭐', 'Форки 🍴', 'Issues 🛠', 'Оновлено']
        
        # --- БЛОК 1: РЕЙТИНГ ЗА ЗІРКАМИ ---
        st.subheader("🏆 Рейтинг проєктів за популярністю (Stars)")
        top_stars = analysis_df.sort_values('Зірки ⭐', ascending=False).head(10)
        
        fig_stars = px.bar(
            top_stars, 
            x='Зірки ⭐', 
            y='Проєкт', 
            orientation='h',
            color='Зірки ⭐',
            color_continuous_scale='Viridis',
            text='Зірки ⭐'
        )
        fig_stars.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_stars, use_container_width=True)

        # --- БЛОК 2: ГРАФ АКТИВНОСТІ (Issues vs Stars) ---
        st.subheader("📈 Аналіз динаміки та активності розробки")
        # Розмір бульбашки залежить від кількості форків
        fig_activity = px.scatter(
            analysis_df, 
            x='Зірки ⭐', 
            y='Issues 🛠',
            size='Форки 🍴', 
            hover_name='Проєкт',
            color='Issues 🛠',
            title="Співвідношення зірок та відкритих Issues (Розмір = Форки)",
            labels={'Issues 🛠': 'Відкриті задачі (Issues)', 'Зірки ⭐': 'Кількість зірок'}
        )
        st.plotly_chart(fig_activity, use_container_width=True)

        # --- БЛОК 3: ДЕТАЛЬНА ТАБЛИЦЯ ТА АНАЛІЗ ---
        st.subheader("🔍 Детальний аналіз репозиторіїв")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Всього проєктів", len(df))
        with col2:
            st.metric("Загальна к-сть зірок", analysis_df['Зірки ⭐'].sum())
        with col3:
            st.metric("Активних Issues", analysis_df['Issues 🛠'].sum())

        st.dataframe(analysis_df.sort_values('Зірки ⭐', ascending=False), use_container_width=True)
        
    else:
        st.error("Користувача не знайдено або ліміт запитів GitHub API вичерпано. Спробуйте пізніше.")

st.markdown("---")
st.caption("Дані завантажуються в реальному часі через GitHub REST API v3")
