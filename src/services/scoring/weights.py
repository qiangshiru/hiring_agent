from pydantic import BaseModel, Field

from src.schemas.scoring import DimensionWeights


class DefaultWeights:
    @staticmethod
    def standard() -> DimensionWeights:
        return DimensionWeights(
            tech_match=0.25,
            ai_depth=0.25,
            engineering=0.20,
            education=0.15,
            stability=0.15,
        )

    @staticmethod
    def ai_focus() -> DimensionWeights:
        return DimensionWeights(
            tech_match=0.20,
            ai_depth=0.35,
            engineering=0.20,
            education=0.10,
            stability=0.15,
        )

    @staticmethod
    def engineering_focus() -> DimensionWeights:
        return DimensionWeights(
            tech_match=0.25,
            ai_depth=0.15,
            engineering=0.35,
            education=0.10,
            stability=0.15,
        )

    @staticmethod
    def senior() -> DimensionWeights:
        return DimensionWeights(
            tech_match=0.20,
            ai_depth=0.20,
            engineering=0.25,
            education=0.20,
            stability=0.15,
        )

    @staticmethod
    def fresh_graduate() -> DimensionWeights:
        return DimensionWeights(
            tech_match=0.25,
            ai_depth=0.20,
            engineering=0.15,
            education=0.30,
            stability=0.10,
        )


class WeightsConfig(BaseModel):
    name: str = "default"
    weights: DimensionWeights = Field(default_factory=DefaultWeights.standard)
    description: str | None = None

    def normalize(self) -> "WeightsConfig":
        normalized_weights = self.weights.normalize()
        return WeightsConfig(
            name=self.name,
            weights=normalized_weights,
            description=self.description,
        )


PRESET_CONFIGS = {
    "standard": DefaultWeights.standard(),
    "ai_focus": DefaultWeights.ai_focus(),
    "engineering_focus": DefaultWeights.engineering_focus(),
    "senior": DefaultWeights.senior(),
    "fresh_graduate": DefaultWeights.fresh_graduate(),
}


def get_preset(name: str) -> DimensionWeights:
    return PRESET_CONFIGS.get(name, DefaultWeights.standard())


def create_custom_weights(
    tech_match: float = 0.25,
    ai_depth: float = 0.25,
    engineering: float = 0.20,
    education: float = 0.15,
    stability: float = 0.15,
) -> DimensionWeights:
    weights = DimensionWeights(
        tech_match=tech_match,
        ai_depth=ai_depth,
        engineering=engineering,
        education=education,
        stability=stability,
    )
    return weights.normalize()
