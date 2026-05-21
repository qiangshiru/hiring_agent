from typing import Dict, Any, Optional
from datetime import datetime

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.orchestrator import MultiAgentOrchestrator
from src.services.question_generator import QuestionGeneratorService
from src.services.evaluation import EvaluationService
from src.services.interview import InterviewSession


class FullInterviewWorkflow:
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.question_generator = QuestionGeneratorService()
        self.evaluation_service = EvaluationService()

    def run(self, jd: JDParseResult, resume: ResumeParseResult) -> Dict[str, Any]:
        print("=== Step 1: 多 Agent 评估 ===")
        multi_agent_result = self.orchestrator.run_full_interview(jd, resume)

        print("\n=== Step 2: 生成面试问题 ===")
        questions_result = self.question_generator.generate(jd, resume)

        print("\n=== Step 3: 创建面试会话 ===")
        interview_session = InterviewSession(jd, resume)

        return {
            "stage": "initial",
            "multi_agent_result": multi_agent_result,
            "questions": [
                {"id": q.id, "type": q.type, "content": q.content, "difficulty": q.difficulty}
                for q in questions_result.questions
            ],
            "session_id": interview_session.session_id,
            "created_at": datetime.now().isoformat(),
        }

    def run_with_interview(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        answers: Dict[str, str],
    ) -> Dict[str, Any]:
        result = self.run(jd, resume)
        session = InterviewSession(jd, resume, session_id=result["session_id"])

        print("\n=== Step 4: 模拟面试流程 ===")
        turn_records = []

        for question_id, answer in answers.items():
            turn = session.submit_answer(question_id, answer)
            turn_records.append({
                "question_id": question_id,
                "answer": answer,
                "quality": turn.answer_quality.value,
            })

            follow_up = session.follow_up(answer)
            if follow_up:
                follow_up_answer = answers.get(follow_up.question_id, "")
                if follow_up_answer:
                    session.submit_answer(follow_up.question_id, follow_up_answer)
                    turn_records.append({
                        "question_id": follow_up.question_id,
                        "answer": follow_up_answer,
                        "type": "follow_up",
                    })

        session_info = session.complete()

        return {
            **result,
            "stage": "completed",
            "interview_records": turn_records,
            "session_info": {
                "total_turns": session_info.total_turns,
                "current_difficulty": session_info.current_difficulty.value,
                "overall_score": session_info.overall_score,
            },
        }
