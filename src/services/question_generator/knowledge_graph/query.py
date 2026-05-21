from typing import Optional

from src.services.question_generator.knowledge_graph.schema import (
    KnowledgeGraph,
    TechCategory,
    TechNode,
)


class KnowledgeGraphQuery:
    def __init__(self, graph: KnowledgeGraph = None):
        self._graph = graph or KnowledgeGraph()

    def get_tech_details(self, tech_name: str) -> Optional[TechNode]:
        return self._graph.get_node(tech_name)

    def find_related_technologies(self, tech_name: str) -> list[str]:
        related = self._graph.get_related_techs(tech_name)
        return [node.name for node in related]

    def get_complexity_level(self, tech_name: str) -> str:
        complexity = self._graph.get_complexity(tech_name)
        if complexity <= 1:
            return "入门"
        elif complexity == 2:
            return "基础"
        elif complexity == 3:
            return "中级"
        elif complexity == 4:
            return "高级"
        else:
            return "专家"

    def suggest_questions_by_tech(self, tech_name: str) -> list[str]:
        node = self._graph.get_node(tech_name)
        if not node:
            return []

        questions = []

        if node.category == TechCategory.LANGUAGE:
            questions = [
                f"请解释 {node.name} 中的内存管理机制",
                f"{node.name} 的垃圾回收机制是怎样的？",
                f"请比较 {node.name} 与其他编程语言的优劣",
                f"{node.name} 的并发编程模型是什么？",
            ]
        elif node.category == TechCategory.FRAMEWORK:
            questions = [
                f"{node.name} 的核心设计理念是什么？",
                f"如何在 {node.name} 中实现高性能？",
                f"{node.name} 的最佳实践有哪些？",
                f"{node.name} 的架构设计是怎样的？",
            ]
        elif node.category == TechCategory.DATABASE:
            questions = [
                f"{node.name} 的数据存储结构是怎样的？",
                f"{node.name} 的索引机制是如何工作的？",
                f"如何优化 {node.name} 的查询性能？",
                f"{node.name} 的事务处理机制是什么？",
            ]
        elif node.category == TechCategory.AI_ML:
            questions = [
                f"{node.name} 的核心原理是什么？",
                f"如何在实际项目中应用 {node.name}？",
                f"{node.name} 有哪些常见的优化策略？",
                f"{node.name} 与其他技术的结合应用场景？",
            ]
        elif node.category == TechCategory.INFRASTRUCTURE:
            questions = [
                f"{node.name} 的架构设计是怎样的？",
                f"{node.name} 的高可用方案是什么？",
                f"如何在 {node.name} 中实现弹性伸缩？",
                f"{node.name} 的监控和告警方案？",
            ]

        return questions

    def generate_deep_dive_topics(self, tech_stack: list[str]) -> list[str]:
        topics = []
        for tech in tech_stack:
            depth = self._graph.query_tech_depth(tech)
            if depth >= 5:
                topics.extend(self.suggest_questions_by_tech(tech))

        topics.extend(self._graph.suggest_deep_dive_topics(tech_stack))
        return list(set(topics))[:15]

    def validate_tech_stack(self, tech_stack: list[str]) -> dict:
        result = {"valid": [], "unknown": [], "complexity": {}}
        for tech in tech_stack:
            node = self._graph.get_node(tech)
            if node:
                result["valid"].append(tech)
                result["complexity"][tech] = self.get_complexity_level(tech)
            else:
                result["unknown"].append(tech)
        return result
