import sys
import os
from datetime import datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.schemas.jd import JDParseResult, WorkExperienceRequirement, EducationRequirement, TechStackRequirement
from src.schemas.resume import ResumeParseResult, Education, WorkExperience, Project


@pytest.fixture
def sample_jd():
    return JDParseResult(
        工作经验=WorkExperienceRequirement(min_years=3),
        学历=EducationRequirement(
            必须=["本科"],
            加分=["硕士", "博士"]
        ),
        技术栈=TechStackRequirement(
            必须=["Python", "LangChain", "LLM"],
            加分=["RAG", "向量数据库"]
        ),
    )


@pytest.fixture
def sample_resume():
    return ResumeParseResult(
        姓名="张三",
        教育=[
            Education(学校="清华大学", 学历="硕士", 专业="计算机科学")
        ],
        工作经验=[
            WorkExperience(
                公司="字节跳动",
                职位="高级工程师",
                描述="负责 AI 平台开发",
                技能=["Python", "Go", "Kubernetes"]
            )
        ],
        项目=[
            Project(
                项目名称="智能推荐系统",
                角色="技术负责人",
                描述="基于 LangChain 和 RAG 的智能推荐系统",
                技术栈=["Python", "LangChain", "RAG", "Milvus"]
            )
        ],
        技能=["Python", "Go", "LangChain", "RAG", "Kubernetes"],
    )


@pytest.fixture
def mock_interview_record():
    from src.schemas.evaluation import InterviewRecord, InterviewTurnRecord
    
    return InterviewRecord(
        session_id="test-session-001",
        jd_id="jd-001",
        resume_id="resume-001",
        turns=[
            InterviewTurnRecord(
                turn_id="t1",
                question="请解释一下什么是 RAG？",
                question_type="deep_dive",
                answer="RAG 是检索增强生成，通过检索外部知识来增强 LLM 的回答...",
                answer_quality="good",
                confidence=0.85,
            ),
            InterviewTurnRecord(
                turn_id="t2",
                question="请介绍一下你的项目经验",
                question_type="project",
                answer="我负责了一个基于 LangChain 的 RAG 系统，主要解决了...",
                answer_quality="good",
                confidence=0.8,
            ),
        ],
        start_time=datetime.now(),
    )
