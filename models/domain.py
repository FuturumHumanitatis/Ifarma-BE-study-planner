
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class StudyInput(BaseModel):
    inn: str = Field(..., description="МНН препарата")
    dose_mg: float = Field(..., description="Дозировка в мг")
    form: Literal["tablet", "capsule", "solution", "other"]
    cv_intra: Optional[float] = Field(None, description="Внутрисубъектная вариабельность в долях (0-1)")
    cv_category: Optional[Literal["low", "high"]] = None
    need_rsabe: Optional[bool] = False
    regime: Literal["fasted", "fed", "both"]
    preferred_design: Optional[str] = None
    is_toxic: bool = False

class PKParameters(BaseModel):
    cmax: Optional[float] = None
    auc: Optional[float] = None
    tmax: Optional[float] = None
    t_half: Optional[float] = None
    cv_intra: Optional[float] = None

class StudyDesign(BaseModel):
    name: str
    type: Literal["2x2", "2x3x3", "2x4", "parallel", "other"]
    periods: int
    sequences: List[str]
    washout_days: int
    rsabe_applicable: bool

class SampleSizeResult(BaseModel):
    base_n: int
    adjusted_for_dropout: int
    dropout_rate: float
    screen_fail_rate: float

class RegulatoryIssue(BaseModel):
    code: str
    severity: Literal["info", "warning", "error"]
    message: str
