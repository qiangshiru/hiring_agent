import React from 'react';
import Link from 'next/link';

export const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-gray-900">AI 招聘 Agent</h1>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            <Link href="/" className="text-gray-600 hover:text-primary-600 transition-colors">
              首页
            </Link>
            <Link href="/jd" className="text-gray-600 hover:text-primary-600 transition-colors">
              JD 解析
            </Link>
            <Link href="/resume" className="text-gray-600 hover:text-primary-600 transition-colors">
              简历解析
            </Link>
            <Link href="/screening" className="text-gray-600 hover:text-primary-600 transition-colors">
              筛选评分
            </Link>
            <Link href="/questions" className="text-gray-600 hover:text-primary-600 transition-colors">
              面试题生成
            </Link>
            <Link href="/evaluation" className="text-gray-600 hover:text-primary-600 transition-colors">
              评价分析
            </Link>
            <Link href="/multi-agent" className="text-gray-600 hover:text-primary-600 transition-colors">
              综合评估
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};
