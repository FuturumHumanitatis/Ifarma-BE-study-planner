
import math
from scipy.stats import norm
from models.domain import StudyInput, StudyDesign, SampleSizeResult
from config import DEFAULT_ALPHA, DEFAULT_POWER, DESIGN_PENALTY_MULTIPLIER

def estimate_log_variance_from_cv(cv_intra: float) -> float:
    # cv_intra ожидается в долях (например, 0.25)
    return math.log(1 + cv_intra**2)

def calculate_sample_size(
    study_input: StudyInput,
    design: StudyDesign,
    cv_effective: float,
    dropout_rate: float = 0.15,
    screen_fail_rate: float = 0.20
) -> SampleSizeResult:
    
    sigma_sq = estimate_log_variance_from_cv(cv_effective)
    z_alpha = norm.ppf(1 - DEFAULT_ALPHA)
    z_beta = norm.ppf(DEFAULT_POWER)
    
    # Классический расчет для 2x2 Crossover (TOST)
    numerator = 2 * (z_alpha + z_beta)**2 * sigma_sq
    denominator = (math.log(0.80))**2 # Граница эквивалентности
    
    base_n = math.ceil(numerator / denominator)
    
    # Применение эвристического коэффициента для других дизайнов (для прототипа)
    base_n = math.ceil(base_n * DESIGN_PENALTY_MULTIPLIER.get(design.type, 1.0))
    
    # Округление до четного числа для баланса последовательностей
    if base_n % 2 != 0: base_n += 1
        
    # Учет потерь
    adjusted_n = math.ceil(base_n / ((1 - dropout_rate) * (1 - screen_fail_rate)))
    if adjusted_n % 2 != 0: adjusted_n += 1
        
    return SampleSizeResult(
        base_n=base_n,
        adjusted_for_dropout=adjusted_n,
        dropout_rate=dropout_rate,
        screen_fail_rate=screen_fail_rate
    )
