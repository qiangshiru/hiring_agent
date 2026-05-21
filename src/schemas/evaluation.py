from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class EvaluationLevel(str, Enum):
    强 = "强"
    中 = "中"
    弱 = "弱"


class RiskLevel(str, Enum):
    高 = "高"
    中 = "中"
    低 = "低"
    无 = "无"


class RiskType(str, Enum):
    项目造假 = "项目造假"
    过度包装 = "过度包装"
    死记硬背 = "死记硬背"
    不稳定 = "不稳定性"


class EvidenceItem(BaseModel):
    source: str  # 来源，如"简历-项目1"、"面试-问题3"
    content: str  # 证据内容
    timestamp: datetime = Field(default_factory=datetime.now)


class DimensionEvaluation(BaseModel):
    dimension: str  # 评价维度，如"技术深度"
    level: EvaluationLevel
    score: float = Field(ge=0.0, le=10.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    comment: str = ""


class EvaluationResult(BaseModel):
    技术深度: DimensionEvaluation
    沟通表达: DimensionEvaluation
    真实性: DimensionEvaluation
    系统设计: DimensionEvaluation
    工程能力: DimensionEvaluation
    综合评分: float = Field(ge=0.0, le=100.0)
    优势: List[str] = Field(default_factory=list)
    不足: List[str] = Field(default_factory=list)


class RiskItem(BaseModel):
    risk_type: RiskType
    risk_level: RiskLevel
    description: str
    evidence: List[EvidenceItem]
    confidence: float = Field(ge=0.0, le=1.0)


class RiskDetectionResult(BaseModel):
    risks: List[RiskItem] = Field(default_factory=list)
    overall_risk_level: RiskLevel = RiskLevel.无
    risk_summary: str = ""


class InterviewTurnRecord(BaseModel):
    turn_id: str
    question: str
    question_type: str
    answer: str
    answer_quality: str
    confidence: float
    follow_up_questions: List[str] = Field(default_factory=list)


class InterviewRecord(BaseModel):
    session_id: str
    jd_id: str
    resume_id: str
    turns: List[InterviewTurnRecord] = Field(default_factory=list)
    start_time: datetime
    end_time: Optional[datetime] = None


class EvaluationReport(BaseModel):
    candidate_name: str
    evaluation_result: EvaluationResult
    risk_result: RiskDetectionResult
    hiring_recommendation: str  # "强烈推荐"、"推荐"、"谨慎推荐"、"不推荐"
    key_insights: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
