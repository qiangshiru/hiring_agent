import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { evaluationApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { EvaluationResult, RiskDetectionResult, ResumeParseResult } from '@/types';

const buildInterviewRecord = () => ({
  session_id: `session-${Date.now()}`,
  jd_id: `jd-${Date.now()}`,
  resume_id: `resume-${Date.now()}`,
  turns: [
    {
      turn_id: 'turn-1',
      question: 'Python的GIL是什么？它在多线程场景下有什么影响？',
      question_type: 'foundation',
      answer: 'GIL是全局解释器锁，限制了Python多线程的并行执行能力。在CPU密集型任务中，多线程无法利用多核优势，但在IO密集型任务中影响较小。可以通过多进程或使用C扩展来绕过GIL限制。',
      answer_quality: 'good',
      confidence: 0.8,
      follow_up_questions: [] as string[],
    },
    {
      turn_id: 'turn-2',
      question: '请描述你设计RAG系统时的架构决策和遇到的挑战？',
      question_type: 'system_design',
      answer: '我们采用了混合检索策略，结合了向量检索和关键词检索。向量检索使用Milvus，关键词检索使用Elasticsearch。主要挑战是检索结果的重排序和上下文窗口的管理。我们实现了两阶段重排序：粗排用BM25，精排用cross-encoder。',
      answer_quality: 'excellent',
      confidence: 0.9,
      follow_up_questions: [] as string[],
    },
  ],
  start_time: new Date().toISOString(),
  end_time: new Date().toISOString(),
});

export const EvaluationPage: React.FC = () => {
  const { resume, setEvaluation, setRisks } = useAppStore();
  const [customQuestion, setCustomQuestion] = useState('');
  const [customAnswer, setCustomAnswer] = useState('');

  const {
    mutate: evaluateMutate,
    isPending: evaluateLoading,
    data: evaluation,
    error: evaluateError,
  } = useMutation({
    mutationFn: evaluationApi.evaluate,
    onSuccess: (result: EvaluationResult) => {
      setEvaluation(result);
    },
  });

  const {
    mutate: risksMutate,
    isPending: risksLoading,
    data: risks,
    error: risksError,
  } = useMutation({
    mutationFn: (record: Record<string, unknown>) =>
      evaluationApi.detectRisks(record, resume as ResumeParseResult),
    onSuccess: (result: RiskDetectionResult) => {
      setRisks(result);
    },
  });

  const handleEvaluate = () => {
    const record = buildInterviewRecord();
    if (customQuestion && customAnswer) {
      record.turns.push({
        turn_id: 'turn-custom',
        question: customQuestion,
        question_type: 'scenario',
        answer: customAnswer,
        answer_quality: 'fair',
        confidence: 0.7,
        follow_up_questions: [],
      });
    }
    evaluateMutate(record);
  };

  const handleDetectRisks = () => {
    const record = buildInterviewRecord();
    if (customQuestion && customAnswer) {
      record.turns.push({
        turn_id: 'turn-custom',
        question: customQuestion,
        question_type: 'scenario',
        answer: customAnswer,
        answer_quality: 'fair',
        confidence: 0.7,
        follow_up_questions: [],
      });
    }
    risksMutate(record);
  };

  const getLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      '强': 'text-green-600',
      '中': 'text-yellow-600',
      '弱': 'text-red-600',
    };
    return colors[level] || 'text-gray-600';
  };

  const getRiskLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      '高': 'bg-red-100 text-red-700',
      '中': 'bg-yellow-100 text-yellow-700',
      '低': 'bg-orange-100 text-orange-700',
      '无': 'bg-green-100 text-green-700',
    };
    return colors[level] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">评价分析</h1>

      <div className="card mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">面试数据</h2>
        <p className="text-sm text-gray-500 mb-4">
          系统已预设示例面试问答数据。你也可以添加自定义问答来进行评价分析。
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">面试问题</label>
            <textarea
              className="input-field h-24"
              value={customQuestion}
              onChange={(e) => setCustomQuestion(e.target.value)}
              placeholder="可选：输入自定义面试问题"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">候选人回答</label>
            <textarea
              className="input-field h-24"
              value={customAnswer}
              onChange={(e) => setCustomAnswer(e.target.value)}
              placeholder="可选：输入候选人回答"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">综合评价</h2>
          <button
            onClick={handleEvaluate}
            disabled={evaluateLoading}
            className="btn-primary mb-4"
          >
            {evaluateLoading ? '评价中...' : '执行评价'}
          </button>

          {evaluateError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-red-700 text-sm">评价失败: {evaluateError.message}</p>
            </div>
          )}

          {evaluation && (
            <div>
              <div className="flex items-center justify-between mb-4 p-4 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">综合评分</span>
                <span className="text-3xl font-bold">{evaluation.综合评分.toFixed(1)}</span>
              </div>

              <div className="space-y-3">
                {(['技术深度', '沟通表达', '真实性', '系统设计', '工程能力'] as const).map((dim) => (
                  <div key={dim} className="flex items-center justify-between">
                    <span className="text-gray-600">{dim}</span>
                    <span className={`font-medium ${getLevelColor(evaluation[dim].level)}`}>
                      {evaluation[dim].level} ({evaluation[dim].score.toFixed(1)})
                    </span>
                  </div>
                ))}
              </div>

              {evaluation.优势 && evaluation.优势.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-medium text-gray-700 mb-2">优势</h3>
                  <ul className="space-y-1">
                    {evaluation.优势.map((item, index) => (
                      <li key={index} className="text-green-600 text-sm">✓ {item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {evaluation.不足 && evaluation.不足.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-medium text-gray-700 mb-2">不足</h3>
                  <ul className="space-y-1">
                    {evaluation.不足.map((item, index) => (
                      <li key={index} className="text-red-600 text-sm">✗ {item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">风险检测</h2>
          <button
            onClick={handleDetectRisks}
            disabled={risksLoading}
            className="btn-primary mb-4"
          >
            {risksLoading ? '检测中...' : '检测风险'}
          </button>

          {risksError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-red-700 text-sm">检测失败: {risksError.message}</p>
            </div>
          )}

          {risks && (
            <div>
              <div className="flex items-center justify-between mb-4 p-4 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">总体风险等级</span>
                <span className={`px-3 py-1 rounded-full text-sm ${getRiskLevelColor(risks.overall_risk_level)}`}>
                  {risks.overall_risk_level}
                </span>
              </div>

              {risks.risks && risks.risks.length > 0 ? (
                <div className="space-y-3">
                  {risks.risks.map((risk, index) => (
                    <div key={index} className="p-3 bg-red-50 rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-gray-900">{risk.risk_type}</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${getRiskLevelColor(risk.risk_level)}`}>
                          {risk.risk_level}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{risk.description}</p>
                      <p className="text-xs text-gray-500 mt-1">置信度: {(risk.confidence * 100).toFixed(0)}%</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-green-600 text-center py-4">✓ 未检测到明显风险</p>
              )}

              {risks.risk_summary && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700">{risks.risk_summary}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EvaluationPage;
