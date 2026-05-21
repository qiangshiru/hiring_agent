from typing import Optional

from src.services.risk_detection.detectors.base import BaseRiskDetector
from src.schemas.evaluation import (
    RiskItem,
    EvidenceItem,
    RiskType,
    RiskLevel,
    InterviewRecord,
)
from src.schemas.resume import ResumeParseResult


class ProjectFraudDetector(BaseRiskDetector):
    @property
    def risk_type(self) -> RiskType:
        return RiskType.项目造假

    def detect(
        self,
        interview_record: InterviewRecord,
        resume: Optional[ResumeParseResult] = None,
    ) -> Optional[RiskItem]:
        evidence_list = []
        project_question_count = 0
        poor_answer_count = 0

        # 检查项目相关问题的回答
        for turn in interview_record.turns:
            if turn.question_type == "project":
                project_question_count += 1
                if turn.answer_quality in ["poor", "no_answer"]:
                    poor_answer_count += 1
                    evidence_list.append(
                        EvidenceItem(
                            source=f"面试-{turn.turn_id}",
                            content=f"项目问题回答较差: {turn.question[:50]}...",
                        )
                    )

        # 如果简历中有项目但回答都很差，可能有问题
        has_resume_projects = resume and len(resume.项目) > 0 if resume else False

        if project_question_count >= 2 and poor_answer_count / project_question_count >= 0.7:
            if has_resume_projects:
                confidence = 0.8
                level = RiskLevel.高
                desc = "简历中提到项目，但面试中相关问题回答都不理想"
            else:
                confidence = 0.5
                level = RiskLevel.中
                desc = "项目相关问题回答质量不高"
            return self._create_risk(level, desc, evidence_list, confidence)

        return None
