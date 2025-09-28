/**
 * 고급 사용법 예제
 * 커스텀 훅과 고급 기능을 활용한 완전한 튜터 시스템
 */

'use client';

import { useState } from 'react';
import { useTutorAPI, useConnectionStatus, useAutoSave } from '../hooks/useTutorAPI';
import { TutorErrorBoundary } from '../components/ErrorBoundary';
import LoadingSpinner from '../components/LoadingSpinner';

export default function AdvancedUsageExample() {
  const [learnerID, setLearnerID] = useState('A070001768');
  const [sessionID, setSessionID] = useState('rt-20250918:first6:A070001768:0');
  const [inputMessage, setInputMessage] = useState('');

  // 고급 훅 사용
  const tutorState = useTutorAPI(learnerID, sessionID);
  const { isConnected, checkConnection } = useConnectionStatus();
  const { lastSaved, clearSaved } = useAutoSave(tutorState.messages);

  // 빠른 응답 버튼들
  const quickResponses = [
    '1번문제 유사 문항 주세요',
    '2번문제 유사 문항 주세요',
    '힌트 주세요',
    '모르겠어요',
    '어떻게 풀어요?'
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    await tutorState.sendMessage(inputMessage);
    setInputMessage('');
  };

  const handleQuickResponse = async (message: string) => {
    await tutorState.sendMessage(message);
  };

  return (
    <TutorErrorBoundary>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">🚀 고급 사용법 예제</h1>

        {/* 연결 상태 및 설정 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* 연결 상태 */}
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-semibold mb-2">🔗 연결 상태</h3>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                isConnected === null ? 'bg-yellow-400' :
                isConnected ? 'bg-green-400' : 'bg-red-400'
              }`} />
              <span className="text-sm">
                {isConnected === null ? '확인 중...' :
                 isConnected ? '서버 연결됨' : '서버 연결 실패'}
              </span>
              <button
                onClick={checkConnection}
                className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
              >
                재확인
              </button>
            </div>
          </div>

          {/* 자동 저장 상태 */}
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-semibold mb-2">💾 자동 저장</h3>
            <div className="text-sm text-gray-600">
              {lastSaved ? (
                <div>
                  <p>마지막 저장: {lastSaved.toLocaleTimeString()}</p>
                  <button
                    onClick={clearSaved}
                    className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 mt-1"
                  >
                    저장된 데이터 삭제
                  </button>
                </div>
              ) : (
                <p>저장된 대화 없음</p>
              )}
            </div>
          </div>
        </div>

        {/* 학습자 설정 */}
        <div className="bg-blue-50 p-4 rounded-lg mb-6">
          <h3 className="font-semibold mb-3">⚙️ 학습자 설정</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">학습자 ID</label>
              <input
                type="text"
                value={learnerID}
                onChange={(e) => setLearnerID(e.target.value)}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="A070001768"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">세션 ID</label>
              <input
                type="text"
                value={sessionID}
                onChange={(e) => setSessionID(e.target.value)}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="rt-20250918:first6:A070001768:0"
              />
            </div>
          </div>
          <button
            onClick={() => tutorState.startSession(learnerID, sessionID)}
            disabled={tutorState.isLoading}
            className="mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            새 세션 시작
          </button>
        </div>

        {/* 메인 채팅 영역 */}
        <div className="bg-white rounded-lg border shadow-sm">
          {/* 채팅 헤더 */}
          <div className="p-4 border-b bg-gray-50 rounded-t-lg">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">💬 대화</h3>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">
                  메시지: {tutorState.messages.length}개
                </span>
                <button
                  onClick={tutorState.reset}
                  className="text-xs px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                >
                  리셋
                </button>
              </div>
            </div>
          </div>

          {/* 메시지 목록 */}
          <div className="h-96 overflow-y-auto p-4">
            {tutorState.messages.length === 0 && !tutorState.isLoading ? (
              <div className="text-center text-gray-500 py-8">
                <p>새 세션을 시작하면 진단테스트 결과가 표시됩니다.</p>
              </div>
            ) : (
              tutorState.messages.map((message, index) => (
                <div key={index} className={`mb-4 flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}>
                  <div className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    <div className="text-xs font-medium mb-1">
                      {message.role === 'user' ? '학생' : 'AI 튜터'}
                    </div>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>
                </div>
              ))
            )}

            {tutorState.isLoading && (
              <div className="flex justify-center mb-4">
                <LoadingSpinner message="AI가 응답을 준비하고 있습니다..." />
              </div>
            )}
          </div>

          {/* 에러 표시 */}
          {tutorState.error && (
            <div className="mx-4 mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <div className="flex justify-between items-center">
                <span className="text-red-700 text-sm">❌ {tutorState.error}</span>
                <button
                  onClick={tutorState.clearError}
                  className="text-red-500 hover:text-red-700"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* 현재 문제 표시 */}
          {tutorState.currentQuestion && (
            <div className="mx-4 mb-4 p-4 bg-blue-50 border border-blue-200 rounded">
              <h4 className="font-semibold text-blue-800 mb-2">📝 연습 문제</h4>
              <p className="text-gray-800 mb-2">{tutorState.currentQuestion.new_question_text}</p>
              <details className="text-sm text-gray-600">
                <summary className="cursor-pointer hover:text-gray-800">정답 및 해설 보기</summary>
                <div className="mt-2 p-2 bg-white rounded">
                  <p><strong>정답:</strong> {tutorState.currentQuestion.correct_answer}</p>
                  <p><strong>해설:</strong> {tutorState.currentQuestion.explanation}</p>
                </div>
              </details>
            </div>
          )}

          {/* 빠른 응답 버튼 */}
          <div className="px-4 py-2 bg-gray-50">
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="text-sm text-gray-600 mr-2">빠른 응답:</span>
              {quickResponses.map((response, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickResponse(response)}
                  disabled={tutorState.isLoading}
                  className="text-xs px-3 py-1 bg-white border rounded-full hover:bg-gray-100 disabled:opacity-50"
                >
                  {response}
                </button>
              ))}
            </div>
          </div>

          {/* 입력 영역 */}
          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="메시지를 입력하세요... (Enter로 전송)"
                disabled={tutorState.isLoading}
                className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
              <button
                onClick={handleSendMessage}
                disabled={tutorState.isLoading || !inputMessage.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {tutorState.isLoading ? '전송 중...' : '전송'}
              </button>
            </div>
          </div>
        </div>

        {/* 개발자 도구 */}
        <div className="mt-6 bg-gray-900 text-white p-4 rounded-lg">
          <h3 className="font-semibold mb-3">🛠️ 개발자 도구</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <strong>상태:</strong>
              <ul className="mt-1 space-y-1">
                <li>로딩: {tutorState.isLoading ? '✅' : '❌'}</li>
                <li>에러: {tutorState.error ? '⚠️' : '✅'}</li>
                <li>연결: {isConnected ? '✅' : '❌'}</li>
              </ul>
            </div>
            <div>
              <strong>데이터:</strong>
              <ul className="mt-1 space-y-1">
                <li>메시지 수: {tutorState.messages.length}</li>
                <li>현재 문제: {tutorState.currentQuestion ? '있음' : '없음'}</li>
                <li>자동 저장: {lastSaved ? '완료' : '없음'}</li>
              </ul>
            </div>
            <div>
              <strong>설정:</strong>
              <ul className="mt-1 space-y-1">
                <li>학습자: {learnerID}</li>
                <li>세션: {sessionID.slice(-8)}...</li>
                <li>API: localhost:7071</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </TutorErrorBoundary>
  );
}