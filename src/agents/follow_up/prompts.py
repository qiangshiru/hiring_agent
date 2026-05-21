from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


EVALUATE_ANSWER_PROMPT = PromptTemplate.from_template(
    """你是一个专业的技术面试官。请评估候选人对以下问题的回答质量。

问题：{question}
答案：{answer}

请从以下维度评估：
1. 准确性 - 答案是否准确
2. 完整性 - 答案是否完整
3. 深度 - 是否有深入的见解

请用以下等级之一回答：excellent, good, fair, poor, no_answer

只返回等级，不要其他内容。
"""
)


GENERATE_FOLLOW_UP_PROMPT = PromptTemplate.from_template(
    """你是一个专业的技术面试官。根据刚才的对话，生成一个追问问题。

原始问题：{question}
候选人回答：{answer}

请生成一个自然的追问问题，要求：
1. 深入挖掘候选人的实际经验
2. 探索技术细节或原理
3. 挑战候选人的思考深度

请直接输出追问问题，不要其他内容。
"""
)


ADJUST_DIFFICULTY_PROMPT = PromptTemplate.from_template(
    """根据候选人的回答质量，调整下一个问题的难度。

当前难度：{current_difficulty}
回答质量：{answer_quality}

可用难度：easy, medium, hard, expert

请直接输出下一个问题的难度，不要其他内容。
"""
)


SHOULD_CONTINUE_PROMPT = PromptTemplate.from_template(
    """根据面试进度，决定是否继续追问。

已完成轮次：{turn_count}
当前知识盲区：{knowledge_gaps}
当前优势：{strengths}

请用 yes 或 no 回答是否需要继续追问。
"""
)
