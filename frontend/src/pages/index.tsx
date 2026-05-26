import React from 'react';
import Link from 'next/link';

const HomePage: React.FC = () => {
  const features = [
    {
      title: 'JD 解析',
      description: '智能解析招聘需求，提取关键信息',
      icon: '📋',
      href: '/jd',
    },
    {
      title: '简历解析',
      description: '多格式简历解析，自动提取候选人信息',
      icon: '📄',
      href: '/resume',
    },
    {
      title: '智能筛选',
      description: '自动匹配候选人与职位要求',
      icon: '🔍',
      href: '/screening',
    },
    {
      title: '面试题生成',
      description: '个性化、分层级面试题自动生成',
      icon: '✏️',
      href: '/questions',
    },
    {
      title: '动态追问',
      description: '基于回答的智能追问系统',
      icon: '💬',
      href: '/interview',
    },
    {
      title: '综合评估',
      description: '多 Agent 协同决策，全面评估候选人',
      icon: '🤝',
      href: '/multi-agent',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI 招聘 Agent 系统
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          基于 AI 的智能化招聘解决方案，从简历筛选到面试评估一站式完成
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Link
            key={feature.title}
            href={feature.href}
            className="card hover:shadow-lg transition-shadow duration-300 group"
          >
            <div className="text-4xl mb-4">{feature.icon}</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
              {feature.title}
            </h3>
            <p className="text-gray-600">{feature.description}</p>
          </Link>
        ))}
      </div>

      <div className="mt-16 card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">系统架构</h2>
        <div className="flex flex-wrap justify-center gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">📋</span>
            </div>
            <p className="font-medium text-gray-900">JD 解析</p>
          </div>
          <div className="text-2xl text-gray-400 self-center">→</div>
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">📄</span>
            </div>
            <p className="font-medium text-gray-900">简历解析</p>
          </div>
          <div className="text-2xl text-gray-400 self-center">→</div>
          <div className="text-center">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">🔍</span>
            </div>
            <p className="font-medium text-gray-900">筛选评分</p>
          </div>
          <div className="text-2xl text-gray-400 self-center">→</div>
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">🤝</span>
            </div>
            <p className="font-medium text-gray-900">综合评估</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
