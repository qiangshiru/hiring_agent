import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { screeningApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { ScreeningResult } from '@/types';

export const ScreeningPage: React.FC = () => {
  const { jd, resume, setScreeningResult } = useAppStore();

  const { mutate, isPending: isLoading, data, error } = useMutation({
    mutationFn: () => screeningApi.screen(jd!, resume!),
    onSuccess: (result: ScreeningResult) => {
      setScreeningResult(result);
    },
  });

  const handleScreen = () => {
    if (jd && resume) {
      mutate();
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-200';
    if (score >= 0.6) return 'bg-yellow-200';
    return 'bg-red-200';
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
          disabled={isLoading || !jd || !resume}
          className="btn-primary"
        >
          {isLoading ? '评分中...' : '开始评分'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">评分失败: {error.message}</p>
        </div>
      )}

      {data && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">评分结果</h2>
          
          <div className="flex items-center justify-between mb-6 p-4 bg-gray-50 rounded-lg">
            <span className="font-medium text-gray-700">综合评分</span>
            <span className={`text-3xl font-bold ${getScoreColor(data.综合评分)}`}>
              {(data.综合评分 * 100).toFixed(1)}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">技术匹配度</p>
              <p className={`text-xl font-bold ${getScoreColor(data.技术匹配度)}`}>
                {(data.技术匹配度 * 100).toFixed(1)}
              </p>
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBgColor(data.技术匹配度)}`}
                  style={{ width: `${data.技术匹配度 * 100}%` }}
                />
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">AI能力深度</p>
              <p className={`text-xl font-bold ${getScoreColor(data.AI能力深度)}`}>
                {(data.AI能力深度 * 100).toFixed(1)}
              </p>
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBgColor(data.AI能力深度)}`}
                  style={{ width: `${data.AI能力深度 * 100}%` }}
                />
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">工程能力</p>
              <p className={`text-xl font-bold ${getScoreColor(data.工程能力)}`}>
                {(data.工程能力 * 100).toFixed(1)}
              </p>
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBgColor(data.工程能力)}`}
                  style={{ width: `${data.工程能力 * 100}%` }}
                />
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">教育背景</p>
              <p className={`text-xl font-bold ${getScoreColor(data.教育背景)}`}>
                {(data.教育背景 * 100).toFixed(1)}
              </p>
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBgColor(data.教育背景)}`}
                  style={{ width: `${data.教育背景 * 100}%` }}
                />
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">稳定性</p>
              <p className={`text-xl font-bold ${getScoreColor(data.稳定性)}`}>
                {(data.稳定性 * 100).toFixed(1)}
              </p>
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBgColor(data.稳定性)}`}
                  style={{ width: `${data.稳定性 * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mb-4">
            <h3 className="font-medium text-gray-700 mb-2">筛选结果</h3>
            <span className={`px-3 py-1 rounded-full text-sm ${data.筛选结果 === '通过' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {data.筛选结果}
            </span>
          </div>

          {data.理由 && data.理由.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-700 mb-2">评分理由</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {data.理由.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ScreeningPage;
