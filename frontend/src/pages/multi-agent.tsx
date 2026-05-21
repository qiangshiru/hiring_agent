import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { multiAgentApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { MultiAgentResult } from '@/types';

export const MultiAgentPage: React.FC = () => {
  const { jd, resume, setMultiAgentResult } = useAppStore();

  const { mutate, isLoading, data, error } = useMutation({
    mutationFn: () => multiAgentApi.evaluate(jd!, resume!),
    onSuccess: (result: MultiAgentResult) => {
      setMultiAgentResult(result);
    },
  });

  const handleEvaluate = () => {
    if (jd && resume) {
      mutate();
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    const colors: Record<string, string> = {
      '强烈推荐': 'bg-green-100 text-green-700',
      '推荐': 'bg-blue-100 text-blue-700',
      '待定': 'bg-yellow-100 text-yellow-700',
      '不推荐': 'bg-red-100 text-red-700',
    };
    return colors[recommendation] || 'bg-gray-100 text-gray-700';
  };

  const getAgentIcon = (agentName: string) => {
    const icons: Record<string, string> = {
      hr_agent: '👔',
      tech_agent: '💻',
      architect_agent: '🏗️',
      risk_agent: '🛡️',
    };
    return icons[agentName] || '🤖';
  };

  const getAgentLabel = (agentName: string) => {
    const labels: Record<string, string> = {
      hr_agent: 'HR Agent',
      tech_agent: '技术 Agent',
      architect_agent: '架构师 Agent',
      risk_agent: '风险 Agent',
    };
    return labels[agentName] || agentName;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">综合评估</h1>

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
          onClick={handleEvaluate}
          disabled={isLoading || !jd || !resume}
          className="btn-primary"
        >
          {isLoading ? '评估中...' : '启动多 Agent 评估'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">评估失败: {error.message}</p>
        </div>
      )}

      {data && (
        <div>
          <div className="card mb-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">最终决策</h2>
              <span className={`px-4 py-2 rounded-full font-medium ${getRecommendationColor(data.final_recommendation)}`}>
                {data.final_recommendation}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.hr_agent_output && (
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">{getAgentIcon('hr_agent')}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{getAgentLabel('hr_agent')}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs ${getRecommendationColor(data.agent_recommendations['hr_agent'])}`}>
                      {data.agent_recommendations['hr_agent']}
                    </span>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  {typeof data.hr_agent_output === 'object' && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-500">学历匹配</span>
                        <span className="text-gray-700">{((data.hr_agent_output as Record<string, number>).education_match || 0) * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">经验匹配</span>
                        <span className="text-gray-700">{((data.hr_agent_output as Record<string, number>).experience_match || 0) * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">综合评分</span>
                        <span className="text-gray-700">{((data.hr_agent_output as Record<string, number>).overall_score || 0) * 100}%</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {data.tech_agent_output && (
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">{getAgentIcon('tech_agent')}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{getAgentLabel('tech_agent')}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs ${getRecommendationColor(data.agent_recommendations['tech_agent'])}`}>
                      {data.agent_recommendations['tech_agent']}
                    </span>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  {typeof data.tech_agent_output === 'object' && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-500">技术匹配</span>
                        <span className="text-gray-700">{((data.tech_agent_output as Record<string, number>).tech_match || 0) * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">AI深度</span>
                        <span className="text-gray-700">{((data.tech_agent_output as Record<string, number>).ai_depth || 0) * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">综合评分</span>
                        <span className="text-gray-700">{((data.tech_agent_output as Record<string, number>).overall_score || 0) * 100}%</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {data.architect_agent_output && (
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">{getAgentIcon('architect_agent')}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{getAgentLabel('architect_agent')}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs ${getRecommendationColor(data.agent_recommendations['architect_agent'])}`}>
                      {data.agent_recommendations['architect_agent']}
                    </span>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  {typeof data.architect_agent_output === 'object' && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-500">项目复杂度</span>
                        <span className="text-gray-700">{((data.architect_agent_output as Record<string, number>).project_complexity || 0) * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">架构经验</span>
                        <span className="text-gray-700">{((data.architect_agent_output as Record<string, number>).architecture_experience || 0) * 100}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">综合评分</span>
                        <span className="text-gray-700">{((data.architect_agent_output as Record<string, number>).overall_score || 0) * 100}%</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {data.risk_agent_output && (
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">{getAgentIcon('risk_agent')}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{getAgentLabel('risk_agent')}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs ${getRecommendationColor(data.agent_recommendations['risk_agent'])}`}>
                      {data.agent_recommendations['risk_agent']}
                    </span>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  {typeof data.risk_agent_output === 'object' && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-500">风险数量</span>
                        <span className="text-gray-700">{(data.risk_agent_output as Record<string, number>).risk_count || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">风险等级</span>
                        <span className="text-gray-700">{(data.risk_agent_output as Record<string, string>).overall_risk_level || '无'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">风险评分</span>
                        <span className="text-gray-700">{((data.risk_agent_output as Record<string, number>).risk_score || 0) * 100}%</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>

          {data.errors && data.errors.length > 0 && (
            <div className="mt-6 card bg-red-50">
              <h3 className="font-medium text-red-700 mb-2">错误信息</h3>
              <ul className="space-y-1">
                {data.errors.map((error, index) => (
                  <li key={index} className="text-red-600 text-sm">{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
