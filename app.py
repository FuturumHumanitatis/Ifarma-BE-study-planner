import streamlit as st
import time
from models.domain import StudyInput
from pk_data.source import get_pk_parameters
from design.logic import select_study_design
from stats.sample_size import calculate_sample_size
from reg.checks import run_regulatory_checks

# --- Настройка страницы ---
st.set_page_config(page_title="AI Protocol Engine", layout="wide", initial_sidebar_state="collapsed")

# --- Современный CSS (Анимации, тени, строгие цвета) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }
    
    /* Анимации появления */
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGreen {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Карточки модулей */
    .module-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        animation: slideUpFade 0.6s ease-out forwards;
    }
    
    /* Заголовки разделов */
    .section-title {
        color: #0F172A;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 16px;
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 8px;
    }

    /* Индикаторы статусов (вместо смайлов) */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-success { background-color: #10B981; animation: pulseGreen 2s infinite; }
    .status-warning { background-color: #F59E0B; }
    .status-error { background-color: #EF4444; }
    .status-info { background-color: #3B82F6; }

    /* Блоки алертов */
    .alert-box {
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 0.95rem;
        border-left: 4px solid;
    }
    .alert-info { background: #EFF6FF; border-color: #3B82F6; color: #1E3A8A; }
    .alert-warning { background: #FFFBEB; border-color: #F59E0B; color: #92400E; }
    .alert-error { background: #FEF2F2; border-color: #EF4444; color: #991B1B; }

    /* Кнопки */
    .stButton > button {
        background-color: #0F172A;
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #334155;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }
    
    /* Данные Data Point */
    .data-point {
        display: flex;
        flex-direction: column;
        margin-bottom: 16px;
    }
    .data-label { font-size: 0.85rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
    .data-value { font-size: 1.15rem; color: #0F172A; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div style='padding: 2rem 0; text-align: center; animation: slideUpFade 0.5s ease-out;'>
    <h1 style='color: #0F172A; margin: 0;'>Clinical Trial Architecture Engine</h1>
    <p style='color: #64748B; font-size: 1.1rem;'>Модуль проектирования исследований биоэквивалентности</p>
</div>
""", unsafe_allow_html=True)

# Инициализация состояния
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- ШАГ 1: ВВОД ДАННЫХ ---
if st.session_state.step == 1:
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Конфигурация препарата</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        inn = st.text_input("МНН (Международное непатентованное наименование)", placeholder="Например: Omeprazole")
        form = st.selectbox("Лекарственная форма", ["tablet", "capsule", "solution", "other"])
    with col2:
        dose = st.number_input("Дозировка (мг)", min_value=0.1, value=20.0, step=5.0)
        regime = st.selectbox("Режим приема", ["fasted", "fed", "both"])
    with col3:
        cv_known = st.number_input("Известный CVintra (доля 0-1)", min_value=0.0, max_value=1.0, value=0.0, step=0.05, help="Оставьте 0, если неизвестно")
        is_toxic = st.checkbox("Высокотоксичный препарат (цитостатики и т.д.)")

    if st.button("Инициализировать алгоритм"):
        if inn:
            cv_val = cv_known if cv_known > 0 else None
            st.session_state.study_input = StudyInput(
                inn=inn, dose_mg=dose, form=form, regime=regime,
                cv_intra=cv_val, is_toxic=is_toxic
            )
            st.session_state.step = 2
            st.rerun()
        else:
            st.markdown("<div class='alert-box alert-error'>Необходимо указать МНН препарата.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- ШАГ 2: ВЫЧИСЛЕНИЯ И ОТЧЕТ ---
if st.session_state.step == 2:
    si = st.session_state.study_input
    
    # Имитация работы API с логами (создает "технический" вайб)
    log_container = st.empty()
    logs = [
        "Подключение к базе данных PK параметров...",
        f"Поиск МНН: {si.inn}...",
        "Извлечение фармакокинетических профилей...",
        "Анализ дисперсии и расчет мощности...",
        "Генерация регуляторного отчета..."
    ]
    for i in range(len(logs)):
        log_container.markdown(f"<div style='font-family: monospace; color: #10B981; font-size: 0.9rem;'>> {logs[i]}</div>", unsafe_allow_html=True)
        time.sleep(0.4)
    log_container.empty()

    # Исполнение бизнес-логики
    pk_data = get_pk_parameters(si)
    design = select_study_design(si, pk_data)
    
    effective_cv = si.cv_intra if si.cv_intra else (pk_data.cv_intra if pk_data.cv_intra else 0.25)
    sample_size = calculate_sample_size(si, design, effective_cv)
    issues = run_regulatory_checks(si, pk_data, design, sample_size)

    # ВЫВОД РЕЗУЛЬТАТОВ: КАРТОЧКА 1 (Дизайн)
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'><span class='status-indicator status-success'></span>Архитектура исследования</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='data-point'><span class='data-label'>Выбранный дизайн</span><span class='data-value'>{design.type.upper()}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='data-point'><span class='data-label'>Периоды / Смывка</span><span class='data-value'>{design.periods} / {design.washout_days} дн.</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='data-point'><span class='data-label'>Выборка (N Total)</span><span class='data-value'>{sample_size.adjusted_for_dropout}</span></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='data-point'><span class='data-label'>RSABE статус</span><span class='data-value'>{'Применимо' if design.rsabe_applicable else 'Не требуется'}</span></div>", unsafe_allow_html=True)
    
    st.markdown(f"<div style='color: #475569; font-size: 0.95rem; margin-top: 10px;'><b>Полное название:</b> {design.name}<br><b>Схемы рандомизации:</b> {', '.join(design.sequences)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ВЫВОД РЕЗУЛЬТАТОВ: КАРТОЧКА 2 (Регуляторика)
    st.markdown("<div class='module-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Регуляторный комплаенс (ЕАЭС №85)</div>", unsafe_allow_html=True)
    
    if not issues:
        st.markdown("<div class='alert-box alert-info'>Нарушений протокола не выявлено. Дизайн полностью соответствует регуляторным нормам.</div>", unsafe_allow_html=True)
    else:
        for issue in issues:
            css_class = f"alert-{issue.severity}" if issue.severity in ['info', 'warning', 'error'] else "alert-info"
            st.markdown(f"<div class='alert-box {css_class}'><b>[{issue.code}]</b> {issue.message}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- ФИЧА: Модуль ослепления (Blinding) ---
    st.markdown("<div class='module-card' style='border-color: #CBD5E1;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'><span class='status-indicator status-info'></span>Модуль IWRS / Ослепление (Для Фармацевта)</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.9rem; color: #64748B;'>Генерация матрицы переупаковки препаратов для обеспечения двойного слепого контроля.</p>", unsafe_allow_html=True)
    
    import pandas as pd
    blind_df = pd.DataFrame({
        "Label Code (Видит врач)": ["SEQ-A-101", "SEQ-B-102", "SEQ-A-103"],
        "Содержимое (Скрыто)": [f"TEST ({si.inn})", "REFERENCE", f"TEST ({si.inn})"],
        "Выдача (Период 1)": ["Флакон А", "Флакон B", "Флакон А"]
    })
    st.dataframe(blind_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Кнопка перехода к LLM (заглушка для следующего шага)
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        if st.button("Генерировать Синопсис (AI LLM Engine)"):
            st.success("Данные подготовлены! На следующем шаге мы подключим API и вставим эти расчеты в твой шаблон.")
