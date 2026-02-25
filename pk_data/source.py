from models.domain import StudyInput, PKParameters

# Хардкодная мини-БД для демо
HARDCODED_PK_DB = {
    "omeprazole": PKParameters(cmax=450.0, auc=1200.0, tmax=2.0, t_half=1.0, cv_intra=0.35), # Высоковариабельный
    "metoprolol": PKParameters(cmax=130.0, auc=850.0, tmax=1.5, t_half=3.5, cv_intra=0.18),  # Стандартный
    "amiodarone": PKParameters(cmax=2.5, auc=50.0, tmax=5.0, t_half=1200.0, cv_intra=0.25),  # Ооочень длинный T1/2
}

def get_pk_parameters(study_input: StudyInput) -> PKParameters:
    """
    Поиск препарата в локальной базе. В будущем здесь будет API запрос к PubMed/DrugBank.
    """
    inn_normalized = study_input.inn.strip().lower()
    return HARDCODED_PK_DB.get(inn_normalized, PKParameters())
