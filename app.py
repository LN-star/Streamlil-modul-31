import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="CSV Анализатор", layout="wide")
st.title("📊 Анализ CSV-файла")

# -----------------------------
# Загрузка файла
# -----------------------------
st.sidebar.header("Загрузка данных")
uploaded_file = st.sidebar.file_uploader("Загрузите CSV-файл", type=["csv"])

@st.cache_data
def load_csv(file):
    try:
        # Попытка угадать кодировку
        return pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(file, encoding="cp1251")
    except Exception as e:
        st.error(f"Ошибка загрузки файла: {e}")
        return None

if uploaded_file is None:
    st.info("Загрузите CSV-файл слева, чтобы начать.")
    st.stop()

df = load_csv(uploaded_file)
if df is None:
    st.stop()

# Попытка преобразовать строки в даты
for col in df.columns:
    if df[col].dtype == object:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass

# -----------------------------
# Отображение таблицы
# -----------------------------
st.subheader("📄 Содержимое файла")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Статистический анализ
# -----------------------------
st.markdown("---")
st.subheader("📈 Статистический анализ столбца")

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if len(numeric_cols) == 0:
    st.warning("В таблице нет числовых столбцов.")
else:
    col = st.selectbox("Выберите числовой столбец", numeric_cols)
    series = df[col].dropna()

    c1, c2, c3 = st.columns(3)
    c1.metric("Среднее", f"{series.mean():.3f}")
    c2.metric("Медиана", f"{series.median():.3f}")
    c3.metric("Стандартное отклонение", f"{series.std():.3f}")

    # Гистограмма
    st.markdown("### 📊 Гистограмма распределения")
    fig, ax = plt.subplots()
    ax.hist(series, bins=20, edgecolor="black")
    ax.set_title(f"Распределение: {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Частота")
    st.pyplot(fig)

    # Кнопка скачивания графика
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        "Скачать гистограмму",
        data=buf,
        file_name="histogram.png",
        mime="image/png"
    )

# -----------------------------
# Графики по двум столбцам
# -----------------------------
st.markdown("---")
st.subheader("📉 Построение графика по двум столбцам")

all_cols = df.columns.tolist()

x_col = st.selectbox("Столбец по оси X", all_cols)
y_col = st.selectbox("Столбец по оси Y", all_cols)

chart_type = st.radio("Тип графика", ["Линейный", "Диаграмма рассеяния"])

plot_df = df[[x_col, y_col]].dropna()

fig2, ax2 = plt.subplots()

if chart_type == "Линейный":
    ax2.plot(plot_df[x_col], plot_df[y_col])
else:
    ax2.scatter(plot_df[x_col], plot_df[y_col])

ax2.set_xlabel(x_col)
ax2.set_ylabel(y_col)
ax2.set_title(f"{chart_type}: {y_col} от {x_col}")
plt.xticks(rotation=30)

st.pyplot(fig2)
