import math
import numpy as np
from scipy.stats import norm

def calculate_sample_size(cv_intra_percent, power=0.80, alpha=0.05, theta1=0.8, drop_out_rate=0.20):
    """
    Расчет размера выборки для 2x2 Crossover дизайна (формула со слайда 13).
    """
    # Переводим CV из процентов в доли
    cv = cv_intra_percent / 100.0
    
    # Внутрисубъектная дисперсия (sigma^2 = ln(CV^2 + 1))
    # В презентации упрощенно используется sigma^2 = (ln(CV))^2, но академически верно так:
    sigma_sq = math.log(cv**2 + 1)
    
    # Критические значения Z
    z_alpha = norm.ppf(1 - alpha)
    z_beta = norm.ppf(power)
    
    # Базовая формула
    numerator = 2 * (z_alpha + z_beta)**2 * sigma_sq
    denominator = (math.log(theta1))**2
    
    n_base = numerator / denominator
    n_rounded = math.ceil(n_base)
    
    # Корректировка на drop-out
    n_total = math.ceil(n_rounded / (1 - drop_out_rate))
    
    # Для перекрестного дизайна выборка должна быть кратна 2
    if n_total % 2 != 0:
        n_total += 1
        
    return {
        "n_base": n_rounded,
        "n_total": n_total,
        "sigma_sq": round(sigma_sq, 4),
        "z_alpha": round(z_alpha, 3),
        "z_beta": round(z_beta, 3)
    }

def determine_study_design(cv_intra, t_half_hours, is_toxic=False):
    """
    Алгоритм выбора дизайна на основе твоего промпта.
    """
    if is_toxic:
        return "parallel", "Параллельный дизайн (препарат токсичен)"
    if t_half_hours > 168:
        return "parallel", "Параллельный дизайн (T1/2 > 168 часов)"
    if cv_intra > 30:
        return "replicate 2x2x4", "Полный репликативный дизайн (CV > 30%, высоко вариабельный)"
    
    return "2×2 crossover", "Классический перекрестный дизайн 2x2"
