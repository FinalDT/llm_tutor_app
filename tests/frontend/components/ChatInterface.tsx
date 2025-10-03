/**
 * LLM Tutor Chat Interface Component
 * Next.js 13+ App Router 최적화된 채팅 인터페이스
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { api, isAPISuccess } from '../utils/apiClient';
import {
  TutorState,
  ConversationMessage,
  GeneratedQuestion,
  ChatInterfaceProps
} from '../types/api.types';
import LoadingSpinner from './LoadingSpinner';

export default function ChatInterface({
  learnerID,
  sessionID,
  onStateChange
}: ChatInterfaceProps) {
  // 상태 관리
  const [state, setState] = useState<TutorState>({
    messages: [],
    isLoading: false,
    error: null,
    currentQuestion: undefined
  });

  const [inputMessage, setInputMessage] = useState('');
  const [currentStep, setCurrentStep] = useState<'summary' | 'feedback' | 'hint'>('summary');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 자동 스크롤 (개선된 버전)
  const scrollToBottom = () => {
    // 즉시 스크롤과 지연 스크롤 모두 적용
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

    // DOM 업데이트 후 다시 한번 스크롤 (안전장치)
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  // 메시지가 변경될 때마다 스크롤
  useEffect(() => {
    scrollToBottom();
  }, [state.messages]);

  // 로딩 상태가 변경될 때도 스크롤 (AI 응답 후)
  useEffect(() => {
    if (!state.isLoading && state.messages.length > 0) {
      scrollToBottom();
    }
  }, [state.isLoading]);

  // 상태 변경 콜백
  useEffect(() => {
    onStateChange?.(state);
  }, [state, onStateChange]);

  // 초기 세션 요약 요청
  useEffect(() => {
    const initSession = async () => {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await api.getSessionSummary(learnerID, sessionID);

        if (isAPISuccess(response)) {
          setState(prev => ({
            ...prev,
            messages: response.data.conversation_history,
            isLoading: false
          }));
          setCurrentStep('feedback');
        } else {
          setState(prev => ({
            ...prev,
            error: response.error?.error || '세션 로드 실패',
            isLoading: false
          }));
        }
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: '네트워크 연결 오류',
          isLoading: false
        }));
      }
    };

    if (learnerID && sessionID) {
      initSession();
    }
  }, [learnerID, sessionID]);

  // 메시지 전송 핸들러
  const sendMessage = async () => {
    if (!inputMessage.trim() || state.isLoading) return;

    const userMessage = inputMessage;
    setInputMessage('');

    // 사용자 메시지를 즉시 화면에 추가
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, { role: 'user', content: userMessage }],
      isLoading: true,
      error: null
    }));

    // 스크롤을 즉시 하단으로 이동
    setTimeout(() => scrollToBottom(), 50);

    try {
      let response;

      if (currentStep === 'feedback') {
        // 2단계: 유사문항 생성 요청
        response = await api.requestSimilarItem(
          learnerID,
          sessionID,
          userMessage,
          state.messages
        );

        if (isAPISuccess(response)) {
          setState(prev => ({
            ...prev,
            messages: response.data.conversation_history,
            currentQuestion: response.data.generated_question_data,
            isLoading: false
          }));

          if (response.data.generated_question_data) {
            setCurrentStep('hint');
          }

          // AI 응답 후 스크롤
          setTimeout(() => scrollToBottom(), 100);
        }
      } else if (currentStep === 'hint' && state.currentQuestion) {
        // 3단계: 힌트 요청
        response = await api.requestHint(
          state.currentQuestion,
          userMessage,
          state.messages,
          learnerID
        );

        if (isAPISuccess(response)) {
          setState(prev => ({
            ...prev,
            messages: response.data.conversation_history,
            isLoading: false
          }));

          // AI 응답 후 스크롤
          setTimeout(() => scrollToBottom(), 100);
        }
      }

      if (response && !isAPISuccess(response)) {
        setState(prev => ({
          ...prev,
          error: response.error?.error || '메시지 전송 실패',
          isLoading: false
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: '네트워크 연결 오류',
        isLoading: false
      }));
    }
  };

  // Enter 키 처리
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 에러 클리어
  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  // 세션 리셋
  const resetSession = () => {
    setState({
      messages: [],
      isLoading: false,
      error: null,
      currentQuestion: undefined
    });
    setCurrentStep('summary');
    setInputMessage('');
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-white border border-gray-200 rounded-lg shadow-lg">
      {/* 헤더 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-blue-50">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">AI 수학 튜터</h2>
          <p className="text-sm text-gray-600">
            학습자: {learnerID} | 세션: {sessionID}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 text-xs rounded-full ${
            currentStep === 'summary' ? 'bg-yellow-100 text-yellow-800' :
            currentStep === 'feedback' ? 'bg-blue-100 text-blue-800' :
            'bg-green-100 text-green-800'
          }`}>
            {currentStep === 'summary' ? '진단 분석' :
             currentStep === 'feedback' ? '문항 생성' : '힌트 제공'}
          </span>
          <button
            onClick={resetSession}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
          >
            리셋
          </button>
        </div>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50" style={{ scrollBehavior: 'smooth' }}>
        {state.messages.length === 0 && !state.isLoading && (
          <div className="text-center text-gray-500 py-8">
            <p>안녕하세요! AI 수학 튜터입니다.</p>
            <p>진단테스트 결과를 분석 중입니다...</p>
          </div>
        )}

        {state.messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}

        {/* 현재 문제 표시 */}
        {state.currentQuestion && currentStep === 'hint' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-800 mb-2">📝 연습 문제</h3>
            <p className="text-gray-800 mb-3">{state.currentQuestion.new_question_text}</p>
            <div className="text-xs text-gray-600">
              <p><strong>정답:</strong> {state.currentQuestion.correct_answer}</p>
              <p><strong>해설:</strong> {state.currentQuestion.explanation}</p>
            </div>
          </div>
        )}

        {state.isLoading && (
          <div className="flex justify-center">
            <LoadingSpinner message="AI가 답변을 생각하고 있어요..." />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 에러 표시 */}
      {state.error && (
        <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex justify-between items-center">
            <span className="text-red-700 text-sm">❌ {state.error}</span>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700 transition-colors"
              aria-label="에러 메시지 닫기"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* 입력 영역 */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              currentStep === 'summary' ? '진단 분석 중...' :
              currentStep === 'feedback' ? '어떤 문제의 유사 문항이 필요한가요? (예: 1번문제 유사 문항 주세요)' :
              '질문이나 답안을 입력하세요... (Shift + Enter로 줄바꿈)'
            }
            disabled={state.isLoading || currentStep === 'summary'}
            className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            rows={3}
          />
          <button
            onClick={sendMessage}
            disabled={state.isLoading || !inputMessage.trim() || currentStep === 'summary'}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {state.isLoading ? '전송 중...' : '전송'}
          </button>
        </div>

        {/* 도움말 */}
        <div className="mt-2 text-xs text-gray-500">
          {currentStep === 'feedback' && '💡 "1번문제 유사 문항 주세요" 와 같이 구체적으로 요청해보세요'}
          {currentStep === 'hint' && '💡 "힌트 주세요", "모르겠어요", "어떻게 풀어요?" 등으로 도움을 요청하세요'}
        </div>
      </div>
    </div>
  );
}

// 메시지 버블 컴포넌트
interface MessageBubbleProps {
  message: ConversationMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div className="text-center text-sm text-gray-500 italic">
        {message.content}
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-3xl px-4 py-3 rounded-lg ${
        isUser
          ? 'bg-blue-600 text-white'
          : 'bg-white border border-gray-200 text-gray-800'
      }`}>
        <div className="flex items-start space-x-2">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
            isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'
          }`}>
            {isUser ? '👤' : '🤖'}
          </div>
          <div className="flex-1">
            <div className={`text-xs font-medium mb-1 ${
              isUser ? 'text-blue-100' : 'text-gray-500'
            }`}>
              {isUser ? '학생' : 'AI 튜터'}
            </div>
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}