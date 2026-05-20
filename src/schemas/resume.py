from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class Education(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    学校: str | None = None
    学历: str | None = None
    专业: str | None = None
    开始时间: datetime | None = None
    结束时间: datetime | None = None
    描述: str | None = None
    置信度: float = Field(default=0.0, ge=0.0, le=1.0)


class WorkExperience(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    公司: str | None = None
    职位: str | None = None
    开始时间: datetime | None = None
    结束时间: datetime | None = None
    描述: str | None = None
    技能: list[str] = Field(default_factory=list)
    置信度: float = Field(default=0.0, ge=0.0, le=1.0)


class Project(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    项目名称: str | None = None
    角色: str | None = None
    开始时间: datetime | None = None
    结束时间: datetime | None = None
    描述: str | None = None
    技术栈: list[str] = Field(default_factory=list)
    置信度: float = Field(default=0.0, ge=0.0, le=1.0)


class Skill(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    名称: str
    类别: str | None = None
    熟练度: str | None = None
    置信度: float = Field(default=0.0, ge=0.0, le=1.0)


class ResumeParseResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    姓名: str | None = None
    性别: str | None = None
    年龄: int | None = None
    电话: str | None = None
    邮箱: str | None = None
    城市: str | None = None
    教育: list[Education] = Field(default_factory=list)
    工作经验: list[WorkExperience] = Field(default_factory=list)
    项目: list[Project] = Field(default_factory=list)
    技能: list[Skill] = Field(default_factory=list)
    自我评价: str | None = None
    原始文本: str | None = None
    解析耗时_ms: int = 0


class ResumeParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    use_cache: bool = True


class ResumeParseResponse(BaseModel):
    data: ResumeParseResult
    cached: bool = False
