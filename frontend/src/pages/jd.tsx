import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { jdApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { JDParseResult } from '@/types';

export const JDPage: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const { setJD } = useAppStore();

  const { mutate, isPending: isLoading, data, error } = useMutation({
    mutationFn: jdApi.parse,
    onSuccess: (result: JDParseResult) => {
      setJD(result);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      mutate(inputText);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">JD 解析</h1>

      <div className="card mb-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              招聘 JD 文本
            </label>
            <textarea
              className="input-field h-48"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="请粘贴招聘 JD 文本..."
            />
          </div>
          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading ? '解析中...' : '开始解析'}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">解析失败: {error.message}</p>
        </div>
      )}

      {data && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">解析结果</h2>
          
          {data.工作经验 && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">工作经验要求</h3>
              <p className="text-gray-600">
                最少 {data.工作经验.min_years || 0} 年经验
              </p>
            </div>
          )}

          {data.学历 && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">学历要求</h3>
              {data.学历.必须 && data.学历.必须.length > 0 && (
                <div className="mb-1">
                  <span className="text-sm text-gray-500">必须:</span>
                  <span className="ml-2 text-gray-700">{data.学历.必须.join(', ')}</span>
                </div>
              )}
              {data.学历.加分 && data.学历.加分.length > 0 && (
                <div>
                  <span className="text-sm text-gray-500">加分:</span>
                  <span className="ml-2 text-gray-700">{data.学历.加分.join(', ')}</span>
                </div>
              )}
            </div>
          )}

          {data.技术栈 && (
            <div>
              <h3 className="font-medium text-gray-700 mb-2">技术栈要求</h3>
              {data.技术栈.must && data.技术栈.must.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {data.技术栈.must.map((tech) => (
                    <span
                      key={tech}
                      className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              )}
              {data.技术栈.bonus && data.技术栈.bonus.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {data.技术栈.bonus.map((tech) => (
                    <span
                      key={tech}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JDPage;
