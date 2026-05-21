from typing import Literal

from langgraph.graph import StateGraph, END

from src.agents.follow_up.state import InterviewAgentState
from src.agents.follow_up.nodes import FollowUpNodes


def create_follow_up_graph():
    graph = StateGraph(InterviewAgentState)
    nodes = FollowUpNodes()

    graph.add_node("evaluate_answer", nodes.evaluate_answer)
    graph.add_node("generate_follow_up", nodes.generate_follow_up)
    graph.add_node("adjust_difficulty", nodes.adjust_difficulty)
    graph.add_node("check_continue", nodes.check_should_continue)

    graph.set_entry_point("evaluate_answer")

    graph.add_edge("evaluate_answer", "adjust_difficulty")
    graph.add_edge("adjust_difficulty", "check_continue")

    def route_after_check(state: InterviewAgentState) -> Literal["generate_follow_up", END]:
        if state.get("should_continue", False):
            return "generate_follow_up"
        return END

    graph.add_conditional_edges(
        "check_continue",
        route_after_check,
        {"generate_follow_up": "generate_follow_up", END: END},
    )

    graph.add_edge("generate_follow_up", END)

    return graph.compile()
