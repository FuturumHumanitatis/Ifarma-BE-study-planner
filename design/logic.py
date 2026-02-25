
from models.domain import StudyInput, PKParameters, StudyDesign
import math

def select_study_design(study_input: StudyInput, pk: PKParameters) -> StudyDesign:
    # 1. Определение эффективного CV
    effective_cv = 0.25 # По умолчанию
    if study_input.cv_intra is not None:
        effective_cv = study_input.cv_intra
    elif pk.cv_intra is not None:
        effective_cv = pk.cv_intra
    elif study_input.cv_category == "low":
        effective_cv = 0.20
    elif study_input.cv_category == "high":
        effective_cv = 0.45

    # 2. Определение возможности RSABE
    rsabe_applicable = effective_cv > 0.30 or study_input.need_rsabe

    # 3. Расчет отмывочного периода (минимум 7 дней или 5 периодов полувыведения)
    washout = 7
    if pk.t_half is not None:
        washout = max(7, math.ceil((5 * pk.t_half) / 24))

    # 4. Выбор дизайна
    if study_input.is_toxic or (pk.t_half and pk.t_half > 168):
        return StudyDesign(
            name="Параллельный дизайн (Parallel group)",
            type="parallel", periods=1, sequences=["T", "R"],
            washout_days=0, rsabe_applicable=rsabe_applicable
        )
        
    if effective_cv <= 0.30:
        return StudyDesign(
            name="Стандартный 2×2 перекрестный (Standard 2x2 Crossover)",
            type="2x2", periods=2, sequences=["TR", "RT"],
            washout_days=washout, rsabe_applicable=False
        )
        
    if 0.30 < effective_cv <= 0.50:
        return StudyDesign(
            name="Трехпериодный частично репликативный (3-way Replicate)",
            type="2x3x3", periods=3, sequences=["TRR", "RRT", "RTR"],
            washout_days=washout, rsabe_applicable=True
        )
        
    return StudyDesign(
        name="Четырехпериодный полный репликативный (4-way Replicate)",
        type="2x4", periods=4, sequences=["TRTR", "RTRT"],
        washout_days=washout, rsabe_applicable=True
    )
