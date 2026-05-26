import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { resumeApi } from '@/services/api';
import { useAppStore } from '@/store/appStore';
import { ResumeParseResult } from '@/types';

export const ResumePage: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const { setResume } = useAppStore();

  const { mutate, isPending: isLoading, data, error } = useMutation({
    mutationFn: resumeApi.parse,
    onSuccess: (result: ResumeParseResult) => {
      setResume(result);
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
      <h1 className="text-2xl font-bold text-gray-900 mb-6">简历解析</h1>

      <div className="card mb-6">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              简历文本
            </label>
            <textarea
              className="input-field h-48"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="请粘贴简历文本..."
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
          
          {data.姓名 && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">姓名</h3>
              <p className="text-gray-600">{data.姓名}</p>
            </div>
          )}

          {data.教育 && data.教育.length > 0 && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">教育背景</h3>
              {data.教育.map((edu, index) => (
                <div key={index} className="mb-2 p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">{edu.学校}</p>
                  <p className="text-gray-600">{edu.学历} · {edu.专业}</p>
                </div>
              ))}
            </div>
          )}

          {data.工作经验 && data.工作经验.length > 0 && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">工作经验</h3>
              {data.工作经验.map((exp, index) => (
                <div key={index} className="mb-2 p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">{exp.公司} · {exp.职位}</p>
                  {exp.技能 && exp.技能.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-1">
                      {exp.技能.map((skill) => (
                        <span
                          key={skill}
                          className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded text-xs"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {data.项目 && data.项目.length > 0 && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">项目经验</h3>
              {data.项目.map((project, index) => (
                <div key={index} className="mb-2 p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium">{project.项目名称}</p>
                  <p className="text-gray-600 text-sm">{project.描述}</p>
                  {project.技术栈 && project.技术栈.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-1">
                      {project.技术栈.map((tech) => (
                        <span
                          key={tech}
                          className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {data.技能 && data.技能.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-700 mb-2">技能标签</h3>
              <div className="flex flex-wrap gap-2">
                {data.技能.map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResumePage;
