from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.generators.base import BaseQuestionGenerator


class FoundationQuestionGenerator(BaseQuestionGenerator):
    @property
    def question_type(self) -> QuestionType:
        return QuestionType.FOUNDATION

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        questions = []
        techs = jd.技术栈.must[:5]

        question_templates = {
            QuestionDifficulty.EASY: [
                "请解释什么是 {tech}？",
                "{tech} 的主要特点是什么？",
                "如何安装和配置 {tech}？",
                "{tech} 的基本使用方法是什么？",
            ],
            QuestionDifficulty.MEDIUM: [
                "{tech} 的核心原理是什么？",
                "请比较 {tech} 与同类技术的差异",
                "{tech} 的最佳实践有哪些？",
                "如何在项目中引入 {tech}？",
            ],
            QuestionDifficulty.HARD: [
                "{tech} 的底层实现机制是怎样的？",
                "如何优化 {tech} 的性能？",
                "{tech} 的架构设计是怎样的？",
                "{tech} 的扩展性如何保证？",
            ],
            QuestionDifficulty.EXPERT: [
                "{tech} 的设计模式和架构原则是什么？",
                "如何解决 {tech} 的性能瓶颈？",
                "{tech} 在大规模场景下的挑战是什么？",
                "{tech} 的未来发展方向是什么？",
            ],
        }

        templates = question_templates.get(difficulty, question_templates[QuestionDifficulty.MEDIUM])

        for i in range(count):
            tech = techs[i % len(techs)] if techs else "编程"
            template = templates[i % len(templates)]
            content = template.format(tech=tech)

            question = Question(
                id=self._generate_id(i),
                type=self.question_type,
                difficulty=difficulty,
                content=content,
                expected_skills=[tech],
                scoring_guide=[
                    "回答准确、完整",
                    "能够举例说明",
                    "逻辑清晰",
                ],
                follow_up_hints=[
                    f"能否详细说明 {tech} 的应用场景？",
                    f"{tech} 的优缺点是什么？",
                ],
                tags=["基础", tech],
            )
            questions.append(self._adjust_difficulty(question, difficulty))

        return questions
