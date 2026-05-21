import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { evaluationApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { EvaluationResult, RiskDetectionResult, ResumeParseResult } from '@/types';

export const EvaluationPage: React.FC = () => {
  const { resume, setEvaluation, setRisks } = useAppStore();

  const { mutate: evaluateMutate, isLoading: evaluateLoading, data: evaluation, error: evaluateError } = useMutation({
    mutationFn: evaluationApi.evaluate,
    onSuccess: (result: EvaluationResult) => {
      setEvaluation(result);
    },
  });

  const { mutate: risksMutate, isLoading: risksLoading, data: risks, error: risksError } = useMutation({
    mutationFn: () => evaluationApi.detectRisks({}, resume as ResumeParseResult),
    onSuccess: (result: RiskDetectionResult) => {
      setRisks(result);
    },
  });

  const handleEvaluate = () => {
    evaluateMutate({});
  };

  const handleDetectRisks = () => {
    risksMutate();
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
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">技术深度</span>
                  <span className={`font-medium ${getLevelColor(evaluation.技术深度.level)}`}>
                    {evaluation.技术深度.level} ({evaluation.技术深度.score.toFixed(1)})
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">沟通表达</span>
                  <span className={`font-medium ${getLevelColor(evaluation.沟通表达.level)}`}>
                    {evaluation.沟通表达.level} ({evaluation.沟通表达.score.toFixed(1)})
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">真实性</span>
                  <span className={`font-medium ${getLevelColor(evaluation.真实性.level)}`}>
                    {evaluation.真实性.level} ({evaluation.真实性.score.toFixed(1)})
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">系统设计</span>
                  <span className={`font-medium ${getLevelColor(evaluation.系统设计.level)}`}>
                    {evaluation.系统设计.level} ({evaluation.系统设计.score.toFixed(1)})
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">工程能力</span>
                  <span className={`font-medium ${getLevelColor(evaluation.工程能力.level)}`}>
                    {evaluation.工程能力.level} ({evaluation.工程能力.score.toFixed(1)})
                  </span>
                </div>
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
