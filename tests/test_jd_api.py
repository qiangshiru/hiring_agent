from fastapi.testclient import TestClient


def test_parse_jd_api(client: TestClient) -> None:
    response = client.post(
        "/api/v1/jd/parse",
        json={
            "text": "招聘 Python AI 工程师：985优先，3年以上经验，熟悉 RAG，熟悉 Agent，熟悉 LangChain",
            "use_cache": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["技术栈"]["must"] == ["Python", "RAG", "LangChain"]
    assert body["data"]["工作经验"]["min_years"] == 3
