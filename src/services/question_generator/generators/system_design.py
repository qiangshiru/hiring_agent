from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.generators.base import BaseQuestionGenerator


class SystemDesignQuestionGenerator(BaseQuestionGenerator):
    @property
    def question_type(self) -> QuestionType:
        return QuestionType.SYSTEM_DESIGN

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        questions = []

        systems = [
            "设计一个高可用的秒杀系统",
            "设计一个分布式缓存系统",
            "设计一个消息队列系统",
            "设计一个实时数据分析系统",
            "设计一个分布式锁服务",
            "设计一个全球CDN系统",
            "设计一个推荐系统架构",
            "设计一个日志收集系统",
        ]

        question_templates = {
            QuestionDifficulty.EASY: [
                "{system}，请描述整体架构？",
                "{system} 的核心组件有哪些？",
            ],
            QuestionDifficulty.MEDIUM: [
                "{system}，请设计核心模块？",
                "{system} 的数据流是怎样的？",
                "{system} 的关键技术选型是什么？",
            ],
            QuestionDifficulty.HARD: [
                "{system}，请详细设计架构，并说明理由？",
                "{system} 的扩展性设计是怎样的？",
                "{system} 的性能优化策略是什么？",
            ],
            QuestionDifficulty.EXPERT: [
                "{system}，请从0到1设计完整方案？",
                "{system} 的演进路线图是什么？",
                "{system} 在大规模场景下的挑战和解决方案？",
            ],
        }

        templates = question_templates.get(difficulty, question_templates[QuestionDifficulty.HARD])

        for i in range(count):
            system = systems[i % len(systems)]
            template = templates[i % len(templates)]
            content = template.format(system=system)

            question = Question(
                id=self._generate_id(i),
                type=self.question_type,
                difficulty=difficulty,
                content=content,
                expected_skills=["系统设计", "架构"],
                scoring_guide=[
                    "架构设计合理",
                    "技术选型恰当",
                    "考虑周全",
                ],
                follow_up_hints=[
                    "如何评估方案？",
                    "有什么改进空间？",
                ],
                tags=["系统设计", "架构"],
            )
            questions.append(self._adjust_difficulty(question, difficulty))

        return questions
