from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.generators.base import BaseQuestionGenerator


class TradeoffQuestionGenerator(BaseQuestionGenerator):
    @property
    def question_type(self) -> QuestionType:
        return QuestionType.TRADEOFF

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        questions = []

        tradeoffs = [
            ("CAP定理", "一致性、可用性、分区容错"),
            ("性能与可扩展性", "系统性能与扩展性"),
            ("一致性与可用性", "数据一致性与系统可用性"),
            ("同步与异步", "同步调用与异步调用"),
            ("缓存与数据库", "缓存策略与数据库设计"),
            ("单体与微服务", "单体架构与微服务"),
        ]

        question_templates = {
            QuestionDifficulty.EASY: [
                "请解释 {tradeoff} 的关系？",
                "{tradeoff} 的基本概念是什么？",
            ],
            QuestionDifficulty.MEDIUM: [
                "如何在 {tradeoff} 之间做出权衡？",
                "{tradeoff} 的适用场景分别是什么？",
                "在实际项目中如何处理 {tradeoff}？",
            ],
            QuestionDifficulty.HARD: [
                "请深入分析 {tradeoff} 的权衡因素？",
                "{tradeoff} 的技术方案有哪些？如何选择？",
                "如何量化 {tradeoff} 的影响？",
            ],
            QuestionDifficulty.EXPERT: [
                "{tradeoff} 的理论基础和实际应用是怎样的？",
                "在大规模系统中如何平衡 {tradeoff}？",
                "{tradeoff} 的演进方向是什么？",
            ],
        }

        templates = question_templates.get(difficulty, question_templates[QuestionDifficulty.MEDIUM])

        for i in range(count):
            tradeoff, desc = tradeoffs[i % len(tradeoffs)]
            template = templates[i % len(templates)]
            content = template.format(tradeoff=tradeoff)

            question = Question(
                id=self._generate_id(i),
                type=self.question_type,
                difficulty=difficulty,
                content=content,
                expected_skills=["架构设计", "系统设计"],
                scoring_guide=[
                    "理解深刻",
                    "权衡分析全面",
                    "结合实践",
                ],
                follow_up_hints=[
                    "有什么最佳实践？",
                    "实际案例是什么？",
                ],
                tags=["架构权衡", tradeoff],
            )
            questions.append(self._adjust_difficulty(question, difficulty))

        return questions
