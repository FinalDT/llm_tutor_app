/**
 * 기본 사용법 예제
 * 최소한의 설정으로 튜터 기능 구현하는 방법
 */

'use client';

import { useState } from 'react';
import { api, isAPISuccess } from '../utils/apiClient';
import { ConversationMessage } from '../types/api.types';

export default function BasicUsageExample() {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputMessage, setInputMessage] = useState('');

  // 기본적인 메시지 전송 함수
  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    setIsLoading(true);

    try {
      // 진단테스트 요약 요청 (첫 번째 메시지인 경우)
      if (messages.length === 0) {
        const response = await api.getSessionSummary(
          'A070001768',
          'rt-20250918:first6:A070001768:0'
        );

        if (isAPISuccess(response)) {
          setMessages(response.data.conversation_history);
        } else {
          console.error('API 오류:', response.error?.error);
        }
      } else {
        // 유사문항 요청
        const response = await api.requestSimilarItem(
          'A070001768',
          'rt-20250918:first6:A070001768:0',
          inputMessage,
          messages
        );

        if (isAPISuccess(response)) {
          setMessages(response.data.conversation_history);
        } else {
          console.error('API 오류:', response.error?.error);
        }
      }
    } catch (error) {
      console.error('네트워크 오류:', error);
    } finally {
      setIsLoading(false);
      setInputMessage('');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">🎯 기본 사용법 예제</h1>

      {/* 메시지 목록 */}
      <div className="border rounded-lg p-4 h-96 overflow-y-auto mb-4 bg-gray-50">
        {messages.length === 0 ? (
          <p className="text-gray-500 text-center">
            "테스트 시작" 버튼을 눌러 시작하세요
          </p>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`mb-2 p-2 rounded ${
              message.role === 'user' ? 'bg-blue-100 ml-8' : 'bg-white mr-8'
            }`}>
              <strong>{message.role === 'user' ? '학생' : 'AI'}:</strong>
              <p className="mt-1">{message.content}</p>
            </div>
          ))
        )}

        {isLoading && (
          <div className="text-center text-gray-500">
            AI가 응답을 준비하고 있습니다...
          </div>
        )}
      </div>

      {/* 입력 영역 */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder={
            messages.length === 0
              ? "먼저 '테스트 시작'을 눌러주세요"
              : "메시지를 입력하세요..."
          }
          disabled={isLoading || messages.length === 0}
          className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        {messages.length === 0 ? (
          <button
            onClick={() => {
              setInputMessage('테스트 시작');
              setTimeout(sendMessage, 100);
            }}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            테스트 시작
          </button>
        ) : (
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            전송
          </button>
        )}
      </div>

      {/* 사용법 안내 */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">💡 사용법</h3>
        <ol className="text-sm text-blue-700 space-y-1">
          <li>1. "테스트 시작" 버튼으로 진단테스트 결과 확인</li>
          <li>2. "1번문제 유사 문항 주세요" 같은 메시지로 문항 요청</li>
          <li>3. 생성된 문제에 대해 "힌트 주세요"로 도움 요청</li>
        </ol>
      </div>
    </div>
  );
}