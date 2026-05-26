import React, { useState } from 'react';
import { useAppStore } from '@/store/appStore';
import { Question } from '@/types';

const InterviewPage: React.FC = () => {
  const { questions } = useAppStore();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [followUpAnswer, setFollowUpAnswer] = useState('');
  const [showFollowUp, setShowFollowUp] = useState(false);
  const [currentFollowUp, setCurrentFollowUp] = useState<string>('');

  const currentQuestion = questions?.questions[currentIndex];

  const handleAnswer = () => {
    if (currentQuestion && answers[currentQuestion.id]) {
      setShowFollowUp(true);
      setCurrentFollowUp(`针对你的回答，能否详细说明一下？`);
    }
  };

  const handleNext = () => {
    if (questions && currentIndex < questions.questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowFollowUp(false);
      setFollowUpAnswer('');
      setCurrentFollowUp('');
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowFollowUp(false);
      setFollowUpAnswer('');
      setCurrentFollowUp('');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">面试模拟</h1>

      {!questions || questions.questions.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600 mb-4">请先生成面试题</p>
          <a href="/questions" className="btn-primary inline-block">
            去生成面试题
          </a>
        </div>
      ) : (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <span className="text-sm text-gray-500">
              问题 {currentIndex + 1} / {questions.questions.length}
            </span>
            <div className="flex gap-2">
              <button
                onClick={handlePrevious}
                disabled={currentIndex === 0}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一题
              </button>
              <button
                onClick={handleNext}
                disabled={currentIndex === questions.questions.length - 1}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一题
              </button>
            </div>
          </div>

          {currentQuestion && (
            <div>
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                    {currentQuestion.type}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    currentQuestion.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                    currentQuestion.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    currentQuestion.difficulty === 'hard' ? 'bg-orange-100 text-orange-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {currentQuestion.difficulty}
                  </span>
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {currentQuestion.content}
                </h2>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  你的回答
                </label>
                <textarea
                  className="input-field h-32"
                  value={answers[currentQuestion.id] || ''}
                  onChange={(e) => setAnswers({ ...answers, [currentQuestion.id]: e.target.value })}
                  placeholder="请输入你的回答..."
                />
              </div>

              <button onClick={handleAnswer} className="btn-primary mb-4">
                提交回答并追问
              </button>

              {showFollowUp && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-3">追问问题</h3>
                  <p className="text-gray-700 mb-3">{currentFollowUp}</p>
                  <textarea
                    className="input-field h-24"
                    value={followUpAnswer}
                    onChange={(e) => setFollowUpAnswer(e.target.value)}
                    placeholder="请回答追问..."
                  />
                  <button onClick={handleNext} className="btn-primary mt-3">
                    完成本题
                  </button>
                </div>
              )}

              {currentQuestion.scoring_points && currentQuestion.scoring_points.length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-medium text-blue-900 mb-2">评分要点</h3>
                  <ul className="flex flex-wrap gap-2">
                    {currentQuestion.scoring_points.map((point, idx) => (
                      <li key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InterviewPage;
