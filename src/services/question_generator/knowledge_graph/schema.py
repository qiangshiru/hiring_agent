from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TechCategory(Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    AI_ML = "ai_ml"
    DEVOPS = "devops"
    CLOUD = "cloud"


@dataclass
class TechNode:
    id: str
    name: str
    category: TechCategory
    description: str = ""
    related_techs: list[str] = None
    parent_tech: Optional[str] = None
    complexity: int = 1

    def __post_init__(self):
        if self.related_techs is None:
            self.related_techs = []


@dataclass
class TechRelation:
    source: str
    target: str
    relation_type: str
    description: str = ""


class KnowledgeGraph:
    def __init__(self):
        self._nodes: dict[str, TechNode] = {}
        self._relations: list[TechRelation] = []
        self._build_graph()

    def _build_graph(self):
        python_node = TechNode(
            id="python",
            name="Python",
            category=TechCategory.LANGUAGE,
            description="高级编程语言",
            complexity=2,
        )
        self._nodes["python"] = python_node

        java_node = TechNode(
            id="java",
            name="Java",
            category=TechCategory.LANGUAGE,
            description="企业级编程语言",
            complexity=3,
        )
        self._nodes["java"] = java_node

        langchain_node = TechNode(
            id="langchain",
            name="LangChain",
            category=TechCategory.FRAMEWORK,
            description="LLM应用框架",
            related_techs=["python"],
            parent_tech="python",
            complexity=3,
        )
        self._nodes["langchain"] = langchain_node

        rag_node = TechNode(
            id="rag",
            name="RAG",
            category=TechCategory.AI_ML,
            description="检索增强生成",
            related_techs=["langchain", "elasticsearch", "vector_db"],
            complexity=4,
        )
        self._nodes["rag"] = rag_node

        vector_db_node = TechNode(
            id="vector_db",
            name="向量数据库",
            category=TechCategory.DATABASE,
            description="存储和检索向量数据",
            related_techs=["rag"],
            complexity=3,
        )
        self._nodes["vector_db"] = vector_db_node

        redis_node = TechNode(
            id="redis",
            name="Redis",
            category=TechCategory.DATABASE,
            description="内存数据库",
            complexity=2,
        )
        self._nodes["redis"] = redis_node

        elasticsearch_node = TechNode(
            id="elasticsearch",
            name="Elasticsearch",
            category=TechCategory.DATABASE,
            description="全文搜索引擎",
            related_techs=["vector_db"],
            complexity=3,
        )
        self._nodes["elasticsearch"] = elasticsearch_node

        docker_node = TechNode(
            id="docker",
            name="Docker",
            category=TechCategory.DEVOPS,
            description="容器化平台",
            complexity=2,
        )
        self._nodes["docker"] = docker_node

        k8s_node = TechNode(
            id="kubernetes",
            name="Kubernetes",
            category=TechCategory.INFRASTRUCTURE,
            description="容器编排",
            related_techs=["docker"],
            complexity=4,
        )
        self._nodes["kubernetes"] = k8s_node

        self._relations = [
            TechRelation("python", "langchain", "uses"),
            TechRelation("langchain", "rag", "implements"),
            TechRelation("rag", "vector_db", "requires"),
            TechRelation("rag", "elasticsearch", "uses"),
            TechRelation("docker", "kubernetes", "orchestrates"),
        ]

    def get_node(self, tech_id: str) -> Optional[TechNode]:
        return self._nodes.get(tech_id.lower())

    def get_related_techs(self, tech_id: str) -> list[TechNode]:
        node = self.get_node(tech_id)
        if not node:
            return []
        return [self._nodes.get(t) for t in node.related_techs if self._nodes.get(t)]

    def get_by_category(self, category: TechCategory) -> list[TechNode]:
        return [node for node in self._nodes.values() if node.category == category]

    def get_complexity(self, tech_id: str) -> int:
        node = self.get_node(tech_id)
        return node.complexity if node else 1

    def query_tech_depth(self, tech_id: str) -> int:
        node = self.get_node(tech_id)
        if not node:
            return 0

        depth = node.complexity
        for related_id in node.related_techs:
            depth += self.query_tech_depth(related_id) // 2

        return min(depth, 10)

    def suggest_deep_dive_topics(self, tech_ids: list[str]) -> list[str]:
        topics = []
        for tech_id in tech_ids:
            node = self.get_node(tech_id)
            if node:
                if node.complexity >= 3:
                    topics.append(f"{node.name} 原理与实现")
                if node.related_techs:
                    for related_id in node.related_techs[:2]:
                        related_node = self.get_node(related_id)
                        if related_node:
                            topics.append(f"{node.name} 与 {related_node.name} 集成")
        return topics[:10]
