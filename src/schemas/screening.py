from pydantic import BaseModel, Field


class ScreeningResult(BaseModel):
    passed: bool
    reasons: list[str] = Field(default_factory=list)
    failed_rules: list[str] = Field(default_factory=list)
    matched_rules: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RuleMatch(BaseModel):
    rule_id: str
    rule_name: str
    passed: bool
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str | None = None


class DimensionScore(BaseModel):
    name: str
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    weight: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str | None = None
    details: dict | None = None


class ScoringResult(BaseModel):
    total: float = Field(default=0.0, ge=0.0, le=100.0)
    dimensions: list[DimensionScore] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    summary: str | None = None
    recommendation: str | None = None


class ScreeningConfig(BaseModel):
    min_work_years: int = 0
    required_education: list[str] = Field(default_factory=list)
    required_tech_stack: list[str] = Field(default_factory=list)
    preferred_tech_stack: list[str] = Field(default_factory=list)
    city_requirement: list[str] = Field(default_factory=list)
    salary_range: tuple[int, int] | None = None
