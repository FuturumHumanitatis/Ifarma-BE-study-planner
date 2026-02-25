import streamlit as st
import time
from core_logic import calculate_sample_size, determine_study_design

# Настройка страницы (должна быть первой командой)
st.set_page_config(
    page_title="AI Protocol Planner | Bioequivalence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Строгий корпоративный CSS (убираем лишнее, задаем цвета)
st.markdown("""
    <style>
    /* Убираем стандартную верхнюю панель Streamlit для чистоты */
    header {visibility: hidden;}
    /* Строгие шрифты */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    /* Стилизация кнопок */
    .stButton>button {
        background-color: #0A2540;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #113A64;
        color: white;
    }
    /* Кастомные плашки (вместо смайлов) */
    .info-box {
        background-color: #E8F0FE;
        border-left: 4px solid #1A73E8;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0 4px 4px 0;
        color: #202124;
    }
    .success-box {
        background-color: #E6F4EA;
        border-left: 4px solid #1E8E3E;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0 4px 4px 0;
        color: #202124;
    }
    .warning-box {
        background-color: #FEF7E0;
        border-left: 4px solid #F9AB00;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0 4px 4px 0;
        color: #202124;
    }
    h1, h2, h3 { color: #202124; }
    </style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown("<h1>Система проектирования исследований биоэквивалентности</h1>", unsafe_allow_html=True)
st.markdown("<div class='info-box'>Введите параметры исследуемого препарата для автоматического расчета дизайна, выборки и генерации синопсиса протокола (согласно Решению ЕЭК №85).</div>", unsafe_allow_html=True)

# Создаем колонки для ввода данных
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Входные параметры препарата")
    test_drug_name = st.text_input("Название препарата (Дженерик)", "Препарат Тест")
    ref_drug_name = st.text_input("Препарат сравнения (Оригинал)", "Препарат Референс")
    is_toxic = st.checkbox("Препарат имеет высокую токсичность (напр., цитостатик)")
    food_effect = st.selectbox("Режим приема", ["натощак", "после еды"])

with col2:
    st.markdown("### Фармакокинетические данные (PK)")
    cv_intra = st.number_input("Внутрисубъектная вариабельность (CVintra, %)", min_value=1.0, max_value=100.0, value=25.0, step=0.1)
    t_half = st.number_input("Период полувыведения (T1/2, часы)", min_value=0.1, value=12.0, step=0.5)
    dropout_rate = st.slider("Прогнозируемый % выбывания (Drop-out)", 5, 40, 20)

st.markdown("---")

# Кнопка запуска вычислений
if st.button("Рассчитать параметры и спланировать дизайн"):
    
    # Имитация загрузки для "серьезности" работы системы
    with st.spinner("Анализ данных и расчет статистической мощности..."):
        time.sleep(1) # небольшая пауза
        
    # 1. Выбираем дизайн
    design_type, design_reason = determine_study_design(cv_intra, t_half, is_toxic)
    
    # 2. Считаем выборку
    sample_data = calculate_sample_size(cv_intra, drop_out_rate=dropout_rate/100.0)
    
    # Вывод результатов в красивых плашках
    st.markdown("### Результаты проектирования")
    
    r_col1, r_col2 = st.columns(2)
    
    with r_col1:
        st.markdown(f"""
        <div class='success-box'>
            <b>Рекомендованный дизайн:</b> {design_type}<br>
            <b>Обоснование:</b> {design_reason}
        </div>
        """, unsafe_allow_html=True)
        
    with r_col2:
        st.markdown(f"""
        <div class='success-box'>
            <b>Размер выборки (N):</b> {sample_data['n_total']} добровольцев<br>
            <b>Базовая потребность (без drop-out):</b> {sample_data['n_base']} добровольцев
        </div>
        """, unsafe_allow_html=True)

    # Вывод математики (чтобы жюри видело прозрачность)
    st.markdown("#### Статистическое обоснование выборки")
    st.latex(rf"""
        N = \frac{{2({sample_data['z_alpha']} + {sample_data['z_beta']})^2 \times {sample_data['sigma_sq']}}}{{(\ln 0.8)^2}} \approx {sample_data['n_base']}
    """)
    
    # --- ТА САМАЯ ФИЧА ДЛЯ ФАРМАЦЕВТА ---
    st.markdown("---")
    st.markdown("### Модуль ослепления (Blinding Label Generator)")
    st.markdown("""
    <div class='warning-box'>
        <b>GCP Compliance:</b> Для предотвращения субъективности (Bias), препараты будут переупакованы (Over-encapsulation). 
        Клинический персонал получит зашифрованные наборы. Ниже сгенерирована матрица для фармацевта исследовательского центра.
    </div>
    """, unsafe_allow_html=True)
    
    # Генерация фейковой матрицы для демонстрации
    import pandas as pd
    matrix_df = pd.DataFrame({
        "Код на упаковке (Label)": ["TRT-A-001", "TRT-B-002", "TRT-A-003", "TRT-B-004"],
        "Содержимое (Скрыто от врача)": [test_drug_name, ref_drug_name, test_drug_name, ref_drug_name],
        "Инструкция фармацевту": ["Выдать в Период 1", "Выдать в Период 1", "Выдать в Период 2", "Выдать в Период 2"]
    })
    st.dataframe(matrix_df, hide_index=True, use_container_width=True)
    
    # Подготовка к шагу LLM (сохраняем данные в session_state)
    st.session_state['ready_for_llm'] = True
    st.session_state['json_data'] = {
        "test_drug": {"name": test_drug_name, "substance": "МНН"},
        "reference_drug": {"name": ref_drug_name},
        "design": {"type": design_type, "food": food_effect},
        "pk_data": {"cv_intra_percent": cv_intra, "t_half_hours": t_half},
        "sample_size": {"n_enrolled": sample_data['n_total'], "dropout_percent": f"{dropout_rate}%"}
    }

# Если расчеты выполнены, показываем кнопку генерации документа
if st.session_state.get('ready_for_llm', False):
    st.markdown("---")
    if st.button("Сгенерировать синопсис (AI Engine)"):
        st.info("Здесь будет интеграция с LLM и подстановка в твой шаблон. Мы сделаем это на следующем шаге!")
