class HiringAgentError(Exception):
    """招聘 Agent 基异常类。"""
    pass


class EmptyInputError(HiringAgentError):
    """输入为空异常。"""
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"{field} 不能为空")


class JDParserError(HiringAgentError):
    """JD 解析异常基类。"""
    pass


class FieldExtractionError(JDParserError):
    """字段提取失败异常。"""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"提取字段 {field} 失败: {reason}")


class JDParseFailure(JDParserError):
    """JD 解析失败异常。"""
    def __init__(self, text: str, error: Exception):
        self.text = text
        self.error = error
        super().__init__(f"JD 解析失败: {str(error)}")


class ResumeParserError(HiringAgentError):
    """简历解析异常基类。"""
    pass


class ResumeFormatError(ResumeParserError):
    """简历格式错误异常。"""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"简历格式错误: {reason}")


class ScreeningError(HiringAgentError):
    """筛选服务异常基类。"""
    pass


class MissingDataError(ScreeningError):
    """缺少必要数据异常。"""
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(f"缺少必要数据: {', '.join(missing_fields)}")


class QuestionGeneratorError(HiringAgentError):
    """问题生成异常基类。"""
    pass


class GenerationFailure(QuestionGeneratorError):
    """问题生成失败异常。"""
    def __init__(self, question_type: str, error: Exception):
        self.question_type = question_type
        self.error = error
        super().__init__(f"生成 {question_type} 问题失败: {str(error)}")


class InterviewSessionError(HiringAgentError):
    """面试会话异常基类。"""
    pass


class SessionNotFoundError(InterviewSessionError):
    """会话不存在异常。"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"会话不存在: {session_id}")


class EvaluationError(HiringAgentError):
    """评价服务异常基类。"""
    pass


class RiskDetectionError(HiringAgentError):
    """风险检测异常基类。"""
    pass


class LLMServiceError(HiringAgentError):
    """LLM 服务异常。"""
    def __init__(self, service: str, error: Exception):
        self.service = service
        self.error = error
        super().__init__(f"LLM 服务 {service} 调用失败: {str(error)}")


class APIError(HiringAgentError):
    """API 调用异常。"""
    def __init__(self, endpoint: str, status_code: int, message: str = ""):
        self.endpoint = endpoint
        self.status_code = status_code
        self.message = message
        super().__init__(f"API 调用失败 {endpoint} [{status_code}]: {message}")
