from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.generators.base import BaseQuestionGenerator


class ScenarioQuestionGenerator(BaseQuestionGenerator):
    @property
    def question_type(self) -> QuestionType:
        return QuestionType.SCENARIO

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        questions = []
        techs = jd.技术栈.must[:3]

        scenarios = [
            ("性能优化", "当系统性能出现瓶颈时"),
            ("高并发", "在高并发场景下"),
            ("数据处理", "面对海量数据时"),
            ("系统集成", "需要集成多个系统时"),
            ("故障排查", "生产环境出现故障时"),
        ]

        question_templates = {
            QuestionDifficulty.EASY: [
                "{scenario}，您会怎么做？",
                "{scenario}，如何快速定位问题？",
            ],
            QuestionDifficulty.MEDIUM: [
                "{scenario}，请设计一个解决方案？",
                "{scenario}，您的思考过程是怎样的？",
                "{scenario}，如何平衡各方需求？",
            ],
            QuestionDifficulty.HARD: [
                "{scenario}，请详细设计解决方案，并说明理由？",
                "{scenario}，如何评估方案的可行性？",
                "{scenario}，有哪些潜在风险？如何规避？",
            ],
            QuestionDifficulty.EXPERT: [
                "{scenario}，请从架构层面给出完整的解决方案？",
                "{scenario}，如何衡量方案的效果？",
                "{scenario}，长期演进路径是什么？",
            ],
        }

        templates = question_templates.get(difficulty, question_templates[QuestionDifficulty.MEDIUM])

        for i in range(count):
            scenario, prefix = scenarios[i % len(scenarios)]
            template = templates[i % len(templates)]
            content = template.format(scenario=prefix + "，" + scenario)

            question = Question(
                id=self._generate_id(i),
                type=self.question_type,
                difficulty=difficulty,
                content=content,
                expected_skills=techs,
                scoring_guide=[
                    "分析问题全面",
                    "方案切实可行",
                    "考虑周全",
                ],
                follow_up_hints=[
                    "方案的优缺点是什么？",
                    "有什么优化空间？",
                ],
                tags=["场景", scenario],
            )
            questions.append(self._adjust_difficulty(question, difficulty))

        return questions
