/**
 * 라이브 데모 페이지
 * 실제 사용 환경을 시뮬레이션하는 완전한 데모
 */

'use client';

import { useState } from 'react';
import { TutorErrorBoundary } from '../frontend/components/ErrorBoundary';
import ChatInterface from '../frontend/components/ChatInterface';
import BasicUsageExample from '../frontend/examples/BasicUsage';
import AdvancedUsageExample from '../frontend/examples/AdvancedUsage';

type DemoMode = 'chat' | 'basic' | 'advanced' | 'showcase';

export default function DemoPage() {
  const [currentDemo, setCurrentDemo] = useState<DemoMode>('showcase');
  const [isDarkMode, setIsDarkMode] = useState(false);

  const demos = [
    {
      id: 'showcase' as DemoMode,
      title: '🎯 데모 소개',
      description: '각 데모의 특징과 사용법을 확인하세요'
    },
    {
      id: 'chat' as DemoMode,
      title: '💬 완전한 채팅 인터페이스',
      description: '실제 서비스와 동일한 3단계 튜터링 시스템'
    },
    {
      id: 'basic' as DemoMode,
      title: '🚀 기본 사용법',
      description: '최소한의 설정으로 시작하는 방법'
    },
    {
      id: 'advanced' as DemoMode,
      title: '⚙️ 고급 기능',
      description: '모든 기능을 활용한 완전한 구현'
    }
  ];

  const showcaseContent = (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">🎓 LLM Tutor API 라이브 데모</h1>
        <p className="text-xl text-gray-600 mb-6">
          실제 동작하는 AI 수학 튜터 시스템을 체험해보세요
        </p>
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-blue-800">
            💡 <strong>사전 준비:</strong> 백엔드 서버가 실행 중인지 확인하세요 (<code>func start</code>)
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {demos.slice(1).map((demo) => (
          <div
            key={demo.id}
            className="bg-white border rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => setCurrentDemo(demo.id)}
          >
            <h3 className="text-xl font-semibold mb-2">{demo.title}</h3>
            <p className="text-gray-600 mb-4">{demo.description}</p>
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
              체험해보기
            </button>
          </div>
        ))}
      </div>

      <div className="bg-gray-50 p-6 rounded-lg mb-8">
        <h2 className="text-2xl font-semibold mb-4">🔧 기술 스택</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h4 className="font-semibold text-blue-600 mb-2">프론트엔드</h4>
            <ul className="text-sm space-y-1">
              <li>• Next.js 13+ App Router</li>
              <li>• TypeScript</li>
              <li>• Tailwind CSS</li>
              <li>• React Hooks</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-green-600 mb-2">백엔드</h4>
            <ul className="text-sm space-y-1">
              <li>• Azure Functions</li>
              <li>• Python 3.9+</li>
              <li>• OpenAI GPT-4o-mini</li>
              <li>• SQL Server</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-purple-600 mb-2">AI 기능</h4>
            <ul className="text-sm space-y-1">
              <li>• 파인튜닝된 모델</li>
              <li>• 소크라틱 방식 튜터링</li>
              <li>• 개인화 학습 데이터</li>
              <li>• 실시간 힌트 제공</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg border">
        <h2 className="text-2xl font-semibold mb-4">📊 3단계 학습 플로우</h2>
        <div className="space-y-4">
          <div className="flex items-center space-x-4 p-4 bg-yellow-50 rounded-lg">
            <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center text-white font-bold">1</div>
            <div>
              <h4 className="font-semibold">진단테스트 분석</h4>
              <p className="text-sm text-gray-600">학습자의 테스트 결과를 분석하여 약한 개념을 파악합니다.</p>
            </div>
          </div>
          <div className="flex items-center space-x-4 p-4 bg-blue-50 rounded-lg">
            <div className="w-8 h-8 bg-blue-400 rounded-full flex items-center justify-center text-white font-bold">2</div>
            <div>
              <h4 className="font-semibold">유사문항 생성</h4>
              <p className="text-sm text-gray-600">틀린 문제와 유사한 새로운 연습 문제를 AI가 생성합니다.</p>
            </div>
          </div>
          <div className="flex items-center space-x-4 p-4 bg-green-50 rounded-lg">
            <div className="w-8 h-8 bg-green-400 rounded-full flex items-center justify-center text-white font-bold">3</div>
            <div>
              <h4 className="font-semibold">소크라틱 힌트</h4>
              <p className="text-sm text-gray-600">정답을 직접 알려주지 않고 질문을 통해 스스로 깨닫도록 안내합니다.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurrentDemo = () => {
    switch (currentDemo) {
      case 'showcase':
        return showcaseContent;
      case 'chat':
        return (
          <div className="max-w-6xl mx-auto p-6">
            <div className="mb-6 text-center">
              <h2 className="text-2xl font-bold mb-2">💬 완전한 채팅 인터페이스</h2>
              <p className="text-gray-600">실제 서비스와 동일한 사용자 경험을 제공합니다</p>
            </div>
            <ChatInterface
              learnerID="A070001768"
              sessionID="rt-20250918:first6:A070001768:0"
            />
          </div>
        );
      case 'basic':
        return <BasicUsageExample />;
      case 'advanced':
        return <AdvancedUsageExample />;
      default:
        return showcaseContent;
    }
  };

  return (
    <TutorErrorBoundary>
      <div className={`min-h-screen transition-colors ${
        isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'
      }`}>
        {/* 상단 네비게이션 */}
        <nav className={`sticky top-0 z-50 border-b ${
          isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        }`}>
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-8">
                <h1 className="text-xl font-bold">🎓 LLM Tutor Demo</h1>
                <div className="hidden md:flex space-x-4">
                  {demos.map((demo) => (
                    <button
                      key={demo.id}
                      onClick={() => setCurrentDemo(demo.id)}
                      className={`px-3 py-2 rounded-md text-sm transition-colors ${
                        currentDemo === demo.id
                          ? 'bg-blue-600 text-white'
                          : isDarkMode
                          ? 'text-gray-300 hover:text-white hover:bg-gray-700'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      {demo.title}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setIsDarkMode(!isDarkMode)}
                  className={`p-2 rounded-md transition-colors ${
                    isDarkMode
                      ? 'text-gray-300 hover:text-white hover:bg-gray-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  {isDarkMode ? '☀️' : '🌙'}
                </button>

                <a
                  href="https://github.com/your-repo/llm-tutor"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`px-3 py-2 rounded-md text-sm transition-colors ${
                    isDarkMode
                      ? 'bg-gray-700 text-white hover:bg-gray-600'
                      : 'bg-gray-900 text-white hover:bg-gray-800'
                  }`}
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </nav>

        {/* 모바일 메뉴 */}
        <div className="md:hidden border-b border-gray-200">
          <div className="px-4 py-2">
            <select
              value={currentDemo}
              onChange={(e) => setCurrentDemo(e.target.value as DemoMode)}
              className="w-full p-2 border rounded"
            >
              {demos.map((demo) => (
                <option key={demo.id} value={demo.id}>
                  {demo.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 메인 콘텐츠 */}
        <main className="pb-8">
          {renderCurrentDemo()}
        </main>

        {/* 푸터 */}
        <footer className={`border-t mt-8 ${
          isDarkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'
        }`}>
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="text-center text-sm">
              <p className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>
                LLM Tutor API Demo •
                <a href="/tests/README.md" className="ml-1 text-blue-600 hover:text-blue-800">
                  개발 가이드
                </a> •
                <a href="/tests/swagger" className="ml-1 text-blue-600 hover:text-blue-800">
                  API 문서
                </a>
              </p>
            </div>
          </div>
        </footer>
      </div>
    </TutorErrorBoundary>
  );
}