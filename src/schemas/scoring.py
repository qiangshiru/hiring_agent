from pydantic import BaseModel, Field


class ScoringDimension(BaseModel):
    name: str
    description: str
    weight: float = Field(default=0.0, ge=0.0, le=1.0)
    enabled: bool = True


class DimensionWeights(BaseModel):
    tech_match: float = Field(default=0.25, ge=0.0, le=1.0)
    ai_depth: float = Field(default=0.25, ge=0.0, le=1.0)
    engineering: float = Field(default=0.2, ge=0.0, le=1.0)
    education: float = Field(default=0.15, ge=0.0, le=1.0)
    stability: float = Field(default=0.15, ge=0.0, le=1.0)

    def normalize(self) -> "DimensionWeights":
        total = (
            self.tech_match
            + self.ai_depth
            + self.engineering
            + self.education
            + self.stability
        )
        if total <= 0:
            return DimensionWeights()
        return DimensionWeights(
            tech_match=round(self.tech_match / total, 4),
            ai_depth=round(self.ai_depth / total, 4),
            engineering=round(self.engineering / total, 4),
            education=round(self.education / total, 4),
            stability=round(self.stability / total, 4),
        )

    def get_dimensions(self) -> list[ScoringDimension]:
        return [
            ScoringDimension(name="tech_match", description="技术栈匹配度", weight=self.tech_match),
            ScoringDimension(name="ai_depth", description="AI深度", weight=self.ai_depth),
            ScoringDimension(name="engineering", description="工程能力", weight=self.engineering),
            ScoringDimension(name="education", description="教育背景", weight=self.education),
            ScoringDimension(name="stability", description="稳定性", weight=self.stability),
        ]
