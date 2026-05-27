#!/bin/bash
# Comprehensive API test script for Hiring Agent
set -e

BASE="http://localhost:8000/api/v1"
PASS=0
FAIL=0

# ==========================================
# 1. Health Check
# ==========================================
echo "============================================"
echo "TEST 1: Health Check"
echo "============================================"
response=$(curl -s http://localhost:8000/api/v1/health)
echo "Response: $response"
if echo "$response" | grep -q '"ok"'; then
  echo "PASS"
  PASS=$((PASS + 1))
else
  echo "FAIL"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# 2. JD Parse
# ==========================================
echo "============================================"
echo "TEST 2: JD Parse"
echo "============================================"
JD_RESPONSE=$(curl -s -X POST "$BASE/jd/parse" \
  -H "Content-Type: application/json" \
  -d '{"text":"招聘 Python AI 工程师：985优先，3年以上经验，熟悉 RAG，熟悉 Agent，熟悉 LangChain"}')

echo "$JD_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$JD_RESPONSE"

if echo "$JD_RESPONSE" | grep -q '"data"'; then
  echo "PASS"
  PASS=$((PASS + 1))
else
  echo "FAIL"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# 3. Resume Parse (text)
# ==========================================
echo "============================================"
echo "TEST 3: Resume Parse (text)"
echo "============================================"
RESUME_RESPONSE=$(curl -s -X POST "$BASE/resume/parse" \
  -H "Content-Type: application/json" \
  -d '{"text":"张三，男，28岁，13800138000，zhangsan@email.com。北京大学计算机科学硕士。2019-2022在字节跳动担任高级Python工程师，负责RAG系统开发。2022-至今在腾讯担任AI架构师，负责Agent框架设计。精通Python、FastAPI、LangChain、Docker、Kubernetes。熟悉RAG、Agent系统设计。"}')

echo "$RESUME_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$RESUME_RESPONSE"

if echo "$RESUME_RESPONSE" | grep -q '"data"'; then
  echo "PASS"
  PASS=$((PASS + 1))
else
  echo "FAIL"
  FAIL=$((FAIL + 1))
fi
echo ""

# Extract JD and Resume data for subsequent tests
JD_DATA=$(echo "$JD_RESPONSE" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['data']))" 2>/dev/null)
RESUME_DATA=$(echo "$RESUME_RESPONSE" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)['data']))" 2>/dev/null)

# ==========================================
# 4. Questions Generate
# ==========================================
echo "============================================"
echo "TEST 4: Questions Generate"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  Q_RESPONSE=$(curl -s -X POST "$BASE/questions/generate" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  echo "$Q_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Generated {len(d.get(\"questions\",[]))} questions')" 2>/dev/null

  if echo "$Q_RESPONSE" | grep -q '"questions"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $(echo $Q_RESPONSE | head -c 200)"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP: Missing JD/Resume data"
fi
echo ""

# ==========================================
# 5. Screening
# ==========================================
echo "============================================"
echo "TEST 5: Screening"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  SCREEN_RESPONSE=$(curl -s -X POST "$BASE/screening/screen" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  echo "$SCREEN_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$SCREEN_RESPONSE"

  if echo "$SCREEN_RESPONSE" | grep -q '"passed"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP: Missing JD/Resume data"
fi
echo ""

# ==========================================
# 6. Scoring
# ==========================================
echo "============================================"
echo "TEST 6: Scoring"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  SCORE_RESPONSE=$(curl -s -X POST "$BASE/scoring/score" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  echo "$SCORE_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Total: {d.get(\"total\")}, Recommendation: {d.get(\"recommendation\")}')" 2>/dev/null

  if echo "$SCORE_RESPONSE" | grep -q '"total"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP: Missing JD/Resume data"
fi
echo ""

# ==========================================
# 7. Scoring with Custom Weights
# ==========================================
echo "============================================"
echo "TEST 7: Scoring with Custom Weights"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  SW_RESPONSE=$(curl -s -X POST "$BASE/scoring/score/weights" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA, \"weights\": {\"tech_match\": 0.4, \"ai_depth\": 0.3, \"engineering\": 0.15, \"education\": 0.1, \"stability\": 0.05}}")

  echo "$SW_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Total: {d.get(\"total\")}, Recommendation: {d.get(\"recommendation\")}')" 2>/dev/null

  if echo "$SW_RESPONSE" | grep -q '"total"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP: Missing JD/Resume data"
fi
echo ""

# ==========================================
# 8. Screening Batch
# ==========================================
echo "============================================"
echo "TEST 8: Screening Batch"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  BATCH_RESPONSE=$(curl -s -X POST "$BASE/screening/screen/batch" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resumes\": [$RESUME_DATA, $RESUME_DATA]}")

  echo "$BATCH_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Results: {len(d)} candidates')" 2>/dev/null

  if echo "$BATCH_RESPONSE" | grep -q '"passed"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP: Missing JD/Resume data"
fi
echo ""

# ==========================================
# 9. Scoring Batch
# ==========================================
echo "============================================"
echo "TEST 9: Scoring Batch"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  SB_RESPONSE=$(curl -s -X POST "$BASE/scoring/score/batch" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resumes\": [$RESUME_DATA, $RESUME_DATA]}")

  echo "$SB_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Results: {len(d)} candidates')" 2>/dev/null

  if echo "$SB_RESPONSE" | grep -q '"total"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP: Missing JD/Resume data"
fi
echo ""

# ==========================================
# 10. Interview Session Create
# ==========================================
echo "============================================"
echo "TEST 10: Interview Session Create"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  SESSION_RESPONSE=$(curl -s -X POST "$BASE/interview/session" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  echo "$SESSION_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$SESSION_RESPONSE"

  if echo "$SESSION_RESPONSE" | grep -q '"session_id"'; then
    echo "PASS"
    PASS=$((PASS + 1))
    SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null)
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
    SESSION_ID=""
  fi
else
  echo "SKIP: Missing JD/Resume data"
  SESSION_ID=""
fi
echo ""

# ==========================================
# 11. Get Session Info
# ==========================================
echo "============================================"
echo "TEST 11: Get Session Info"
echo "============================================"
if [ -n "$SESSION_ID" ]; then
  SINFO_RESPONSE=$(curl -s "$BASE/interview/session/$SESSION_ID")
  echo "$SINFO_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$SINFO_RESPONSE"
  if echo "$SINFO_RESPONSE" | grep -q '"session_id"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP: No session ID"
fi
echo ""

# ==========================================
# 12. Next Question
# ==========================================
echo "============================================"
echo "TEST 12: Next Question"
echo "============================================"
if [ -n "$SESSION_ID" ]; then
  NEXTQ_RESPONSE=$(curl -s -X POST "$BASE/interview/session/$SESSION_ID/next-question")
  echo "$NEXTQ_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Question: {d.get(\"content\",\"\")[:50]}...')" 2>/dev/null
  if echo "$NEXTQ_RESPONSE" | grep -q '"question_id"'; then
    echo "PASS"
    PASS=$((PASS + 1))
    QUESTION_ID=$(echo "$NEXTQ_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['question_id'])" 2>/dev/null)
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
    QUESTION_ID=""
  fi
else
  echo "SKIP"
  QUESTION_ID=""
fi
echo ""

# ==========================================
# 13. Submit Answer
# ==========================================
echo "============================================"
echo "TEST 13: Submit Answer"
echo "============================================"
if [ -n "$SESSION_ID" ] && [ -n "$QUESTION_ID" ]; then
  ANSWER_RESPONSE=$(curl -s -X POST "$BASE/interview/session/$SESSION_ID/answer" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\", \"question_id\": \"$QUESTION_ID\", \"answer\": \"RAG是检索增强生成技术，通过从外部知识库检索相关信息来增强大语言模型的生成能力。\"}")
  echo "$ANSWER_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$ANSWER_RESPONSE"
  if echo "$ANSWER_RESPONSE" | grep -q '"turn_id"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP"
fi
echo ""

# ==========================================
# 14. Follow-up
# ==========================================
echo "============================================"
echo "TEST 14: Follow-up"
echo "============================================"
if [ -n "$SESSION_ID" ] && [ -n "$QUESTION_ID" ]; then
  FOLLOWUP_RESPONSE=$(curl -s -X POST "$BASE/interview/session/$SESSION_ID/follow-up" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\", \"question_id\": \"$QUESTION_ID\", \"answer\": \"RAG是检索增强生成\"}")
  echo "$FOLLOWUP_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$FOLLOWUP_RESPONSE"
  if echo "$FOLLOWUP_RESPONSE" | grep -q '"question_id"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP"
fi
echo ""

# ==========================================
# 15. Complete Session
# ==========================================
echo "============================================"
echo "TEST 15: Complete Session"
echo "============================================"
if [ -n "$SESSION_ID" ]; then
  COMPLETE_RESPONSE=$(curl -s -X POST "$BASE/interview/session/$SESSION_ID/complete")
  echo "$COMPLETE_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))" 2>/dev/null || echo "$COMPLETE_RESPONSE"
  if echo "$COMPLETE_RESPONSE" | grep -q '"session_id"'; then
    echo "PASS"
    PASS=$((PASS + 1))
  else
    echo "FAIL"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP"
fi
echo ""

# ==========================================
# 16. Multi-Agent Status
# ==========================================
echo "============================================"
echo "TEST 16: Multi-Agent Status"
echo "============================================"
MA_STATUS=$(curl -s "$BASE/multi-agent/status")
echo "Response: $MA_STATUS"
# Actual response has agent_status, workflow_status, errors keys
if echo "$MA_STATUS" | grep -q '"agent_status"'; then
  echo "PASS"
  PASS=$((PASS + 1))
else
  echo "FAIL"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# 17. Multi-Agent Evaluate
# ==========================================
echo "============================================"
echo "TEST 17: Multi-Agent Evaluate"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  MA_EVAL=$(curl -s -X POST "$BASE/multi-agent/evaluate" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  echo "$MA_EVAL" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Keys: {list(d.keys())}')" 2>/dev/null
  http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/multi-agent/evaluate" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  if [ "$http_code" = "200" ]; then
    echo "PASS (HTTP $http_code)"
    PASS=$((PASS + 1))
  else
    echo "FAIL (HTTP $http_code)"
    echo "Response: $(echo $MA_EVAL | head -c 300)"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP"
fi
echo ""

# ==========================================
# 18. Multi-Agent Full Interview
# ==========================================
echo "============================================"
echo "TEST 18: Multi-Agent Full Interview"
echo "============================================"
if [ -n "$JD_DATA" ] && [ -n "$RESUME_DATA" ]; then
  MA_FULL=$(curl -s -X POST "$BASE/multi-agent/full-interview" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/multi-agent/full-interview" \
    -H "Content-Type: application/json" \
    -d "{\"jd\": $JD_DATA, \"resume\": $RESUME_DATA}")

  if [ "$http_code" = "200" ]; then
    echo "PASS (HTTP $http_code)"
    PASS=$((PASS + 1))
  else
    echo "FAIL (HTTP $http_code)"
    echo "Response: $(echo $MA_FULL | head -c 300)"
    FAIL=$((FAIL + 1))
  fi
else
  echo "SKIP"
fi
echo ""

# ==========================================
# 19. Evaluation - Evaluate Interview
# ==========================================
echo "============================================"
echo "TEST 19: Evaluation - Evaluate Interview"
echo "============================================"
EVAL_PAYLOAD=$(cat <<EOF
{
  "session_id": "test-session-001",
  "jd_id": "jd-test",
  "resume_id": "resume-test",
  "turns": [
    {
      "turn_id": "turn-1",
      "question": "Python的GIL是什么？",
      "question_type": "foundation",
      "answer": "GIL是全局解释器锁，限制了Python多线程的并行执行。",
      "answer_quality": "good",
      "confidence": 0.8,
      "follow_up_questions": []
    }
  ],
  "start_time": "2026-05-27T12:00:00",
  "end_time": "2026-05-27T12:30:00"
}
EOF
)

EVAL_RESPONSE=$(curl -s -X POST "$BASE/evaluation/evaluate" \
  -H "Content-Type: application/json" \
  -d "$EVAL_PAYLOAD")

echo "$EVAL_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Keys: {list(d.keys())}')" 2>/dev/null
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/evaluation/evaluate" \
  -H "Content-Type: application/json" \
  -d "$EVAL_PAYLOAD")

if [ "$http_code" = "200" ]; then
  echo "PASS (HTTP $http_code)"
  PASS=$((PASS + 1))
else
  echo "FAIL (HTTP $http_code)"
  echo "Response: $(echo $EVAL_RESPONSE | head -c 300)"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# 20. Evaluation - Detect Risks
# ==========================================
echo "============================================"
echo "TEST 20: Evaluation - Detect Risks"
echo "============================================"
# This endpoint has two body params: interview_record + resume, so wrap in interview_record key
RISK_RESPONSE=$(curl -s -X POST "$BASE/evaluation/detect-risks" \
  -H "Content-Type: application/json" \
  -d "{\"interview_record\": $EVAL_PAYLOAD}")

echo "$RISK_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Keys: {list(d.keys())}')" 2>/dev/null
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/evaluation/detect-risks" \
  -H "Content-Type: application/json" \
  -d "{\"interview_record\": $EVAL_PAYLOAD}")

if [ "$http_code" = "200" ]; then
  echo "PASS (HTTP $http_code)"
  PASS=$((PASS + 1))
else
  echo "FAIL (HTTP $http_code)"
  echo "Response: $(echo $RISK_RESPONSE | head -c 300)"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# 21. Evaluation - Generate Report
# ==========================================
echo "============================================"
echo "TEST 21: Evaluation - Generate Report"
echo "============================================"
REPORT_PAYLOAD=$(cat <<EOF
{
  "interview_record": $EVAL_PAYLOAD,
  "resume": $RESUME_DATA,
  "candidate_name": "张三"
}
EOF
)

REPORT_RESPONSE=$(curl -s -X POST "$BASE/evaluation/generate-report" \
  -H "Content-Type: application/json" \
  -d "$REPORT_PAYLOAD")

echo "$REPORT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Keys: {list(d.keys())}')" 2>/dev/null
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/evaluation/generate-report" \
  -H "Content-Type: application/json" \
  -d "$REPORT_PAYLOAD")

if [ "$http_code" = "200" ]; then
  echo "PASS (HTTP $http_code)"
  PASS=$((PASS + 1))
else
  echo "FAIL (HTTP $http_code)"
  echo "Response: $(echo $REPORT_RESPONSE | head -c 300)"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# 22. API Docs
# ==========================================
echo "============================================"
echo "TEST 22: API Docs"
echo "============================================"
DOCS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$DOCS_CODE" = "200" ]; then
  echo "PASS (HTTP 200)"
  PASS=$((PASS + 1))
else
  echo "FAIL (HTTP $DOCS_CODE)"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# 23. OpenAPI Schema
# ==========================================
echo "============================================"
echo "TEST 23: OpenAPI Schema"
echo "============================================"
SCHEMA_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/openapi.json)
if [ "$SCHEMA_CODE" = "200" ]; then
  echo "PASS (HTTP 200)"
  PASS=$((PASS + 1))
else
  echo "FAIL (HTTP $SCHEMA_CODE)"
  FAIL=$((FAIL + 1))
fi
echo ""

# ==========================================
# SUMMARY
# ==========================================
echo ""
echo "============================================"
echo "           TEST SUMMARY"
echo "============================================"
echo "  Passed : $PASS"
echo "  Failed : $FAIL"
echo "  Total  : $((PASS + FAIL))"
echo "============================================"

if [ "$FAIL" -gt 0 ]; then
  echo "SOME TESTS FAILED"
  exit 1
else
  echo "ALL TESTS PASSED"
  exit 0
fi
