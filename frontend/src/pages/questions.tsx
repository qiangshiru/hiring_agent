import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { questionsApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { QuestionGenerationResult, Question } from '@/types';

export const QuestionsPage: React.FC = () => {
  const { jd, resume, setQuestions } = useAppStore();
  const [selectedType, setSelectedType] = useState<string>('all');

  const { mutate, isPending: isLoading, data, error } = useMutation({
    mutationFn: () => questionsApi.generate(jd!, resume!),
    onSuccess: (result: QuestionGenerationResult) => {
      setQuestions(result);
    },
  });

  const handleGenerate = () => {
    if (jd && resume) {
      mutate();
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      foundation: '基础题',
      project: '项目题',
      deep_dive: '深挖题',
      scenario: '场景题',
      tradeoff: '架构题',
      failure: '故障题',
      system_design: '系统设计题',
    };
    return labels[type] || type;
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      easy: 'bg-green-100 text-green-700',
      medium: 'bg-yellow-100 text-yellow-700',
      hard: 'bg-orange-100 text-orange-700',
      expert: 'bg-red-100 text-red-700',
    };
    return colors[difficulty] || 'bg-gray-100 text-gray-700';
  };

  const getDifficultyLabel = (difficulty: string) => {
    const labels: Record<string, string> = {
      easy: '简单',
      medium: '中等',
      hard: '困难',
      expert: '专家',
    };
    return labels[difficulty] || difficulty;
  };

  const filteredQuestions = data?.questions.filter((q) =>
    selectedType === 'all' ? true : q.type === selectedType
  ) || [];

  const types = ['all', 'foundation', 'project', 'deep_dive', 'scenario', 'tradeoff', 'failure', 'system_design'];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">面试题生成</h1>

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
          onClick={handleGenerate}
          disabled={isLoading || !jd || !resume}
          className="btn-primary"
        >
          {isLoading ? '生成中...' : '生成面试题'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">生成失败: {error.message}</p>
        </div>
      )}

      {data && (
        <div>
          <div className="card mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">难度分布</h2>
            <div className="flex flex-wrap gap-4">
              {Object.entries(data.difficulty_distribution).map(([difficulty, count]) => (
                <div key={difficulty} className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-sm ${getDifficultyColor(difficulty)}`}>
                    {getDifficultyLabel(difficulty)}
                  </span>
                  <span className="text-gray-600">{count} 题</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="flex flex-wrap gap-2 mb-4">
              {types.map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${
                    selectedType === type
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {type === 'all' ? '全部' : getTypeLabel(type)}
                </button>
              ))}
            </div>

            <div className="space-y-4">
              {filteredQuestions.map((question: Question, index) => (
                <div key={question.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <span className="font-medium text-gray-900">
                      {index + 1}. {question.content}
                    </span>
                    <div className="flex gap-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                        {getTypeLabel(question.type)}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs ${getDifficultyColor(question.difficulty)}`}>
                        {getDifficultyLabel(question.difficulty)}
                      </span>
                    </div>
                  </div>
                  {question.scoring_guide && question.scoring_guide.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-500 mb-1">评分要点:</p>
                      <ul className="flex flex-wrap gap-2">
                        {question.scoring_guide.map((point, idx) => (
                          <li key={idx} className="px-2 py-1 bg-gray-200 rounded text-xs text-gray-700">
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionsPage;
