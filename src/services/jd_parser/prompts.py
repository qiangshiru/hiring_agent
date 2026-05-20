from src.schemas.jd import JDParseResult

JD_PARSER_SYSTEM_PROMPT = """你是企业招聘系统中的 JD 解析专家。
请从招聘 JD 中抽取学历、工作年限、技术栈、行业经验、城市要求和薪资范围。
必须只输出符合 JSON Schema 的 JSON，不要输出解释文字。
"""

JD_PARSER_USER_PROMPT_TEMPLATE = """请解析以下 JD：

{jd_text}
"""


def build_jd_parser_prompt(jd_text: str) -> str:
    return JD_PARSER_SYSTEM_PROMPT + "\n" + JD_PARSER_USER_PROMPT_TEMPLATE.format(jd_text=jd_text)


def jd_parser_json_schema() -> dict[str, object]:
    return JDParseResult.model_json_schema(by_alias=True)
