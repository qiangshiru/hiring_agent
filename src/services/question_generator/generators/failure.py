from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.generators.base import BaseQuestionGenerator


class FailureQuestionGenerator(BaseQuestionGenerator):
    @property
    def question_type(self) -> QuestionType:
        return QuestionType.FAILURE

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        questions = []

        failures = [
            "线上服务突然宕机",
            "数据库连接池耗尽",
            "缓存击穿",
            "消息队列堆积",
            "网络分区",
            "数据不一致",
            "性能急剧下降",
            "安全漏洞",
        ]

        question_templates = {
            QuestionDifficulty.EASY: [
                "如果遇到 {failure}，您会怎么做？",
                "{failure} 的常见原因是什么？",
            ],
            QuestionDifficulty.MEDIUM: [
                "{failure} 的排查思路是什么？",
                "如何预防 {failure} 的发生？",
                "{failure} 的应急响应流程是什么？",
            ],
            QuestionDifficulty.HARD: [
                "请详细描述 {failure} 的排查过程？",
                "{failure} 的根因分析方法是什么？",
                "如何建立 {failure} 的预防机制？",
            ],
            QuestionDifficulty.EXPERT: [
                "{failure} 的系统性解决方案是什么？",
                "如何量化 {failure} 的影响？",
                "{failure} 的复盘方法论是什么？",
            ],
        }

        templates = question_templates.get(difficulty, question_templates[QuestionDifficulty.MEDIUM])

        for i in range(count):
            failure = failures[i % len(failures)]
            template = templates[i % len(templates)]
            content = template.format(failure=failure)

            question = Question(
                id=self._generate_id(i),
                type=self.question_type,
                difficulty=difficulty,
                content=content,
                expected_skills=["故障排查", "运维"],
                scoring_guide=[
                    "排查思路清晰",
                    "解决方案有效",
                    "预防措施到位",
                ],
                follow_up_hints=[
                    "如何避免再次发生？",
                    "有什么监控方案？",
                ],
                tags=["故障", failure],
            )
            questions.append(self._adjust_difficulty(question, difficulty))

        return questions
