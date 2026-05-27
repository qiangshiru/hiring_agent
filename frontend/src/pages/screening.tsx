import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { screeningApi, scoringApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { ScreeningResult, ScoringResult } from '@/types';

export const ScreeningPage: React.FC = () => {
  const { jd, resume, setScreeningResult } = useAppStore();

  const {
    mutate: screenMutate,
    isPending: screenLoading,
    data: screenResult,
    error: screenError,
  } = useMutation({
    mutationFn: () => screeningApi.screen(jd!, resume!),
    onSuccess: (result: ScreeningResult) => {
      setScreeningResult(result);
    },
  });

  const {
    mutate: scoreMutate,
    isPending: scoreLoading,
    data: scoreResult,
    error: scoreError,
  } = useMutation({
    mutationFn: () => scoringApi.score(jd!, resume!),
  });

  const handleScreen = () => {
    if (jd && resume) {
      screenMutate();
      scoreMutate();
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-200';
    if (score >= 60) return 'bg-yellow-200';
    return 'bg-red-200';
  };

  const getDimensionLabel = (name: string) => {
    const labels: Record<string, string> = {
      tech_match: '技术匹配',
      ai_depth: 'AI 深度',
      engineering: '工程能力',
      education: '教育背景',
      stability: '稳定性',
    };
    return labels[name] || name;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">筛选评分</h1>

      <div className="card mb-6">
        <div className="mb-4">
          <h3 className="font-medium text-gray-700 mb-2">数据状态</h3>
          <div className="flex gap-4">
            <span className={`px-3 py-1 rounded-full text-sm ${jd ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
              {jd ? '✓ JD 已解析' : 'JD 未解析'}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm ${resume ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
              {resume ? '✓ 简历已解析' : '简历未解析'}
            </span>
          </div>
        </div>
        <button
          onClick={handleScreen}
          disabled={screenLoading || scoreLoading || !jd || !resume}
          className="btn-primary"
        >
          {screenLoading || scoreLoading ? '评分中...' : '开始评分'}
        </button>
      </div>

      {(screenError || scoreError) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">评分失败: {(screenError || scoreError)?.message}</p>
        </div>
      )}

      {screenResult && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">筛选结果</h2>
          <div className="flex items-center justify-between mb-4 p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">是否通过</span>
            <span className={`px-3 py-1 rounded-full text-sm ${screenResult.passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {screenResult.passed ? '通过' : '未通过'}
            </span>
          </div>

          {screenResult.matched_rules && screenResult.matched_rules.length > 0 && (
            <div className="mb-3">
              <h3 className="text-sm font-medium text-green-700 mb-1">✓ 通过项</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {screenResult.matched_rules.map((rule, idx) => (
                  <li key={idx}>{rule}</li>
                ))}
              </ul>
            </div>
          )}

          {screenResult.failed_rules && screenResult.failed_rules.length > 0 && (
            <div className="mb-3">
              <h3 className="text-sm font-medium text-red-700 mb-1">✗ 未通过项</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {screenResult.failed_rules.map((rule, idx) => (
                  <li key={idx}>{rule}</li>
                ))}
              </ul>
            </div>
          )}

          {screenResult.reasons && screenResult.reasons.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-1">原因</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {screenResult.reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {scoreResult && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">评分结果</h2>

          <div className="flex items-center justify-between mb-6 p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">综合评分</span>
            <span className={`text-3xl font-bold ${getScoreColor(scoreResult.total)}`}>
              {scoreResult.total.toFixed(1)}
            </span>
          </div>

          {scoreResult.recommendation && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">建议</h3>
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {scoreResult.recommendation}
              </span>
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            {scoreResult.dimensions.map((dim) => (
              <div key={dim.name} className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">{getDimensionLabel(dim.name)}</p>
                <p className={`text-xl font-bold ${getScoreColor(dim.score)}`}>
                  {dim.score.toFixed(1)}
                </p>
                <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getScoreBgColor(dim.score)}`}
                    style={{ width: `${Math.min(dim.score, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">权重: {(dim.weight * 100).toFixed(0)}%</p>
              </div>
            ))}
          </div>

          {scoreResult.summary && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">{scoreResult.summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ScreeningPage;
