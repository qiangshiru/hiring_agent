from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.generators.base import BaseQuestionGenerator


class ProjectQuestionGenerator(BaseQuestionGenerator):
    @property
    def question_type(self) -> QuestionType:
        return QuestionType.PROJECT

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        questions = []
        projects = resume.项目[:3]

        if not projects:
            return questions

        for i in range(count):
            project = projects[i % len(projects)]
            project_name = project.项目名称 or "您参与的项目"

            question_templates = {
                QuestionDifficulty.EASY: [
                    f"请介绍一下您在 {project_name} 项目中负责什么工作？",
                    f"{project_name} 项目的主要功能是什么？",
                    f"您在 {project_name} 项目中使用了哪些技术？",
                ],
                QuestionDifficulty.MEDIUM: [
                    f"请详细描述 {project_name} 项目的架构设计？",
                    f"{project_name} 项目中遇到了哪些技术难题？如何解决的？",
                    f"您在 {project_name} 项目中的核心贡献是什么？",
                ],
                QuestionDifficulty.HARD: [
                    f"{project_name} 项目的技术选型是如何考虑的？有哪些权衡？",
                    f"在 {project_name} 项目中，如何保证代码质量和可维护性？",
                    f"{project_name} 项目的性能优化策略是什么？",
                ],
                QuestionDifficulty.EXPERT: [
                    f"如果重新设计 {project_name}，您会做出哪些改进？为什么？",
                    f"{project_name} 项目的扩展性设计是怎样的？如何应对业务增长？",
                    f"在 {project_name} 项目中，您如何评估技术方案的优劣？",
                ],
            }

            templates = question_templates.get(difficulty, question_templates[QuestionDifficulty.MEDIUM])
            content = templates[i % len(templates)]

            tech_stack = project.技术栈[:3] if project.技术栈 else []

            question = Question(
                id=self._generate_id(i),
                type=self.question_type,
                difficulty=difficulty,
                content=content,
                expected_skills=tech_stack,
                scoring_guide=[
                    "能够清晰描述项目背景",
                    "突出个人贡献",
                    "技术细节准确",
                ],
                follow_up_hints=[
                    f"能否详细说明 {project_name} 的技术亮点？",
                    f"项目过程中最大的挑战是什么？",
                ],
                tags=["项目经验", project_name],
            )
            questions.append(self._adjust_difficulty(question, difficulty))

        return questions
