
import json
from openai import OpenAI
from models.domain import StudyInput, PKParameters, StudyDesign, SampleSizeResult

def generate_synopsis_llm(
    api_key: str,
    study_input: StudyInput,
    pk_data: PKParameters,
    design: StudyDesign,
    sample_size: SampleSizeResult,
    template_text: str
) -> str:
    """
    Отправляет собранные данные и промпт в LLM для генерации синопсиса.
    """
    client = OpenAI(api_key=api_key)
    
    context_data = {
        "protocol_name": f"Клиническое исследование биоэквивалентности препарата {study_input.inn.capitalize()}",
        "sponsor": "[НАИМЕНОВАНИЕ СПОНСОРА]",
        "site": "[КЛИНИЧЕСКИЙ ЦЕНТР]",
        "lab": "[БИОАНАЛИТИЧЕСКАЯ ЛАБОРАТОРИЯ]",
        "test_drug": {
            "name": f"{study_input.inn.capitalize()} Тест",
            "substance": study_input.inn.capitalize()
        },
        "reference_drug": {
            "name": f"{study_input.inn.capitalize()} Референс",
            "reg_number": "ЛП-XXXXXX"
        },
        "design": {
            "type": design.type,
            "food": "натощак" if study_input.regime == "fasted" else "после приема высококалорийной пищи",
            "washout_days": design.washout_days
        },
        "pk_data": {
            "cv_intra_percent": (study_input.cv_intra or pk_data.cv_intra or 0.25) * 100,
            "cv_intra_param": "Cmax и AUC0-t",
            "t_half_hours": pk_data.t_half or 12.0,
            "tmax_value": pk_data.tmax_value if hasattr(pk_data, 'tmax_value') else 2.0
        },
        "sample_size": {
            "n_enrolled": sample_size.adjusted_for_dropout,
            "n_screened": int(sample_size.adjusted_for_dropout / (1 - sample_size.screen_fail_rate)),
            "dropout_percent": f"{int(sample_size.dropout_rate * 100)}%",
            "screen_fail_percent": f"{int(sample_size.screen_fail_rate * 100)}%",
            "n_per_group": sample_size.adjusted_for_dropout // 2
        },
        "study_periods": {
            "screening_max_days": 14,
            "pk_period_days": 2,
            "follow_up_days": 7,
            "total_duration_days": 14 + 2 + design.washout_days + 2 + 7
        },
        "blood_sampling": {
            "samples_per_period": 16,
            "volume_per_sample_ml": 5,
            "sampling_schedule": "до приема и через 0.33, 0.67, 1, 1.5, 2, 2.5, 3, 4, 6, 8, 12, 16, 24, 36, 48 часов",
            "total_blood_fk_ml": 16 * 5 * 2,
            "total_blood_clinical_ml": 40
        },
        "safety": {"ecg_parameter": "интервала QTc"},
        "bioequivalence_criteria": {
            "ci_level": 90,
            "lower_bound": "80,00%",
            "upper_bound": "125,00%",
            "alpha": 0.05
        },
        "statistics": {"anova_factors": "Препарат, Период, Последовательность, Субъект(Последовательность)"},
        "ethical": {"insurance_company": "[СТРАХОВАЯ КОМПАНИЯ]"}
    }

    # Системный промпт (строгое поведение)
    system_prompt = (
        "Ты — высококвалифицированный клинический фармаколог и медицинский писатель (Medical Writer). "
        "Твоя задача — строго следовать инструкции пользователя и заполнить шаблон синопсиса."
        "Ты не имеешь права выдумывать данные, которых нет во входном JSON."
    )

    user_prompt = f"""
ВХОДНЫЕ ДАННЫЕ (JSON):
{json.dumps(context_data, indent=2, ensure_ascii=False)}

ПРОМПТ-ИНСТРУКЦИЯ И ШАБЛОН:
{template_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o", # или gpt-4-turbo
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1, # Низкая температура для максимальной строгости и отсутствия галлюцинаций
        max_tokens=4000
    )
    
    return response.choices[0].message.content
