from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.generators.base import BaseQuestionGenerator


class DeepDiveQuestionGenerator(BaseQuestionGenerator):
    @property
    def question_type(self) -> QuestionType:
        return QuestionType.DEEP_DIVE

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        questions = []
        techs = jd.技术栈.must[:3] + [s.名称 for s in resume.技能[:3]]
        techs = list(set(techs))[:5]

        question_templates = {
            QuestionDifficulty.EASY: [
                "请解释 {tech} 的核心概念是什么？",
                "{tech} 的工作原理是怎样的？",
                "如何理解 {tech} 的基本概念？",
            ],
            QuestionDifficulty.MEDIUM: [
                "{tech} 的内部机制是如何实现的？",
                "请深入分析 {tech} 的核心算法？",
                "{tech} 的设计模式是怎样的？",
            ],
            QuestionDifficulty.HARD: [
                "{tech} 的底层实现细节是什么？",
                "如何优化 {tech} 的核心性能？",
                "{tech} 的源码中有哪些关键设计决策？",
            ],
            QuestionDifficulty.EXPERT: [
                "{tech} 的架构演进过程是怎样的？",
                "如何解决 {tech} 的深层次技术问题？",
                "{tech} 在大规模应用中的挑战是什么？",
            ],
        }

        templates = question_templates.get(difficulty, question_templates[QuestionDifficulty.MEDIUM])

        for i in range(count):
            tech = techs[i % len(techs)] if techs else "技术"
            template = templates[i % len(templates)]
            content = template.format(tech=tech)

            question = Question(
                id=self._generate_id(i),
                type=self.question_type,
                difficulty=difficulty,
                content=content,
                expected_skills=[tech],
                scoring_guide=[
                    "技术深度足够",
                    "原理阐述清晰",
                    "能够结合实践",
                ],
                follow_up_hints=[
                    f"{tech} 的优缺点是什么？",
                    f"在什么场景下适合使用 {tech}？",
                ],
                tags=["深挖", tech],
            )
            questions.append(self._adjust_difficulty(question, difficulty))

        return questions
