from typing import TypedDict

from src.schemas.jd import JDParseResult
from src.services.jd_parser.service import JDParserService


class JDParserAgentState(TypedDict, total=False):
    jd_text: str
    result: JDParseResult


def build_jd_parser_agent(service: JDParserService | None = None) -> object:
    from langgraph.graph import END, StateGraph

    parser_service = service or JDParserService()

    async def parse_node(state: JDParserAgentState) -> JDParserAgentState:
        result = await parser_service.parse_async(state["jd_text"])
        return {"jd_text": state["jd_text"], "result": result}

    graph = StateGraph(JDParserAgentState)
    graph.add_node("parse_jd", parse_node)
    graph.set_entry_point("parse_jd")
    graph.add_edge("parse_jd", END)
    return graph.compile()
