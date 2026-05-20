from pydantic import BaseModel, ConfigDict, Field


class EducationRequirement(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    must: list[str] = Field(default_factory=list, alias="必须")
    bonus: list[str] = Field(default_factory=list, alias="加分")


class WorkExperienceRequirement(BaseModel):
    min_years: int | None = Field(default=None, ge=0)
    max_years: int | None = Field(default=None, ge=0)


class TechStackRequirement(BaseModel):
    must: list[str] = Field(default_factory=list)
    bonus: list[str] = Field(default_factory=list)


class SalaryRange(BaseModel):
    min_monthly: int | None = Field(default=None, ge=0)
    max_monthly: int | None = Field(default=None, ge=0)
    currency: str = "CNY"
    raw: str | None = None


class JDParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    use_cache: bool = True


class JDParseResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    学历: EducationRequirement = Field(default_factory=EducationRequirement)
    工作经验: WorkExperienceRequirement = Field(default_factory=WorkExperienceRequirement)
    技术栈: TechStackRequirement = Field(default_factory=TechStackRequirement)
    行业经验: list[str] = Field(default_factory=list)
    城市要求: list[str] = Field(default_factory=list)
    薪资范围: SalaryRange | None = None


class JDParseResponse(BaseModel):
    data: JDParseResult
    cached: bool = False
