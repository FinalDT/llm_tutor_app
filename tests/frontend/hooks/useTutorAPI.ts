/**
 * Custom Hooks for LLM Tutor API
 * React Hook으로 API 상태 관리 및 비즈니스 로직 캡슐화
 */

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { api, isAPISuccess } from '../utils/apiClient';
import {
  TutorState,
  TutorActions,
  ConversationMessage,
  GeneratedQuestion,
  APIResponse,
  TutorAPIResponse
} from '../types/api.types';

// 메인 튜터 API 훅
export function useTutorAPI(learnerID: string, sessionID: string): TutorState & TutorActions {
  const [state, setState] = useState<TutorState>({
    messages: [],
    isLoading: false,
    error: null,
    currentQuestion: undefined
  });

  const [currentStep, setCurrentStep] = useState<'summary' | 'feedback' | 'hint'>('summary');
  const isInitialized = useRef(false);

  // 에러 핸들링 유틸리티
  const handleError = useCallback((error: string) => {
    setState(prev => ({
      ...prev,
      error,
      isLoading: false
    }));
  }, []);

  // API 응답 처리 유틸리티
  const handleAPIResponse = useCallback((response: APIResponse<TutorAPIResponse>) => {
    if (isAPISuccess(response)) {
      setState(prev => ({
        ...prev,
        messages: response.data.conversation_history,
        currentQuestion: response.data.generated_question_data || prev.currentQuestion,
        isLoading: false,
        error: null
      }));
      return true;
    } else {
      handleError(response.error?.error || 'API 요청 실패');
      return false;
    }
  }, [handleError]);

  // 세션 시작 (진단테스트 요약)
  const startSession = useCallback(async (customLearnerID?: string, customSessionID?: string) => {
    const lid = customLearnerID || learnerID;
    const sid = customSessionID || sessionID;

    if (!lid || !sid) {
      handleError('학습자 ID와 세션 ID가 필요합니다.');
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await api.getSessionSummary(lid, sid);
      if (handleAPIResponse(response)) {
        setCurrentStep('feedback');
      }
    } catch (error) {
      handleError('네트워크 연결 오류');
    }
  }, [learnerID, sessionID, handleError, handleAPIResponse]);

  // 메시지 전송
  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim() || state.isLoading) return;

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      let response: APIResponse<TutorAPIResponse>;

      if (currentStep === 'feedback') {
        // 유사문항 생성 요청
        response = await api.requestSimilarItem(
          learnerID,
          sessionID,
          message,
          state.messages
        );

        if (handleAPIResponse(response) && isAPISuccess(response)) {
          if (response.data.generated_question_data) {
            setCurrentStep('hint');
          }
        }
      } else if (currentStep === 'hint' && state.currentQuestion) {
        // 힌트 요청
        response = await api.requestHint(
          state.currentQuestion,
          message,
          state.messages,
          learnerID
        );

        handleAPIResponse(response);
      } else {
        handleError('현재 단계에서는 메시지를 보낼 수 없습니다.');
      }
    } catch (error) {
      handleError('네트워크 연결 오류');
    }
  }, [currentStep, learnerID, sessionID, state.messages, state.currentQuestion, state.isLoading, handleError, handleAPIResponse]);

  // 유사문항 요청
  const requestSimilarItem = useCallback(async (questionNumber: string) => {
    const message = `${questionNumber}번문제 유사 문항 주세요`;
    await sendMessage(message);
  }, [sendMessage]);

  // 에러 클리어
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // 상태 리셋
  const reset = useCallback(() => {
    setState({
      messages: [],
      isLoading: false,
      error: null,
      currentQuestion: undefined
    });
    setCurrentStep('summary');
    isInitialized.current = false;
  }, []);

  // 초기화
  useEffect(() => {
    if (learnerID && sessionID && !isInitialized.current) {
      isInitialized.current = true;
      startSession();
    }
  }, [learnerID, sessionID, startSession]);

  return {
    ...state,
    sendMessage,
    startSession,
    requestSimilarItem,
    clearError,
    reset
  };
}

// 연결 상태 확인 훅
export function useConnectionStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkConnection = useCallback(async () => {
    setIsChecking(true);
    try {
      const response = await api.healthCheck();
      setIsConnected(isAPISuccess(response));
    } catch (error) {
      setIsConnected(false);
    } finally {
      setIsChecking(false);
    }
  }, []);

  useEffect(() => {
    checkConnection();

    // 30초마다 연결 상태 확인
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  return { isConnected, isChecking, checkConnection };
}

// 자동 저장 훅
export function useAutoSave(
  messages: ConversationMessage[],
  delay: number = 2000
) {
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const saveToLocalStorage = useCallback(() => {
    try {
      localStorage.setItem('tutor_conversation', JSON.stringify({
        messages,
        timestamp: new Date().toISOString()
      }));
      setLastSaved(new Date());
    } catch (error) {
      console.warn('Failed to save conversation to localStorage:', error);
    }
  }, [messages]);

  const loadFromLocalStorage = useCallback((): ConversationMessage[] => {
    try {
      const saved = localStorage.getItem('tutor_conversation');
      if (saved) {
        const data = JSON.parse(saved);
        return data.messages || [];
      }
    } catch (error) {
      console.warn('Failed to load conversation from localStorage:', error);
    }
    return [];
  }, []);

  const clearSaved = useCallback(() => {
    try {
      localStorage.removeItem('tutor_conversation');
      setLastSaved(null);
    } catch (error) {
      console.warn('Failed to clear saved conversation:', error);
    }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(saveToLocalStorage, delay);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [messages, delay, saveToLocalStorage]);

  return { lastSaved, loadFromLocalStorage, clearSaved };
}

// 타이핑 효과 훅
export function useTypingEffect(text: string, speed: number = 50) {
  const [displayText, setDisplayText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!text) {
      setDisplayText('');
      return;
    }

    setIsTyping(true);
    setDisplayText('');

    let index = 0;
    const timer = setInterval(() => {
      setDisplayText(text.slice(0, index + 1));
      index++;

      if (index >= text.length) {
        clearInterval(timer);
        setIsTyping(false);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return { displayText, isTyping };
}

// 키보드 단축키 훅
export function useKeyboardShortcuts(callbacks: {
  onSend?: () => void;
  onClear?: () => void;
  onReset?: () => void;
}) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + Enter: 메시지 전송
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        callbacks.onSend?.();
      }

      // Ctrl/Cmd + K: 대화 내용 클리어
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        callbacks.onClear?.();
      }

      // Ctrl/Cmd + R: 리셋 (기본 새로고침 방지)
      if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
        event.preventDefault();
        callbacks.onReset?.();
      }

      // ESC: 에러 클리어
      if (event.key === 'Escape') {
        callbacks.onClear?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [callbacks]);
}

// 반응형 디자인 훅
export function useResponsive() {
  const [screenSize, setScreenSize] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');

  useEffect(() => {
    const checkScreenSize = () => {
      const width = window.innerWidth;
      if (width < 768) {
        setScreenSize('mobile');
      } else if (width < 1024) {
        setScreenSize('tablet');
      } else {
        setScreenSize('desktop');
      }
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  return screenSize;
}

// 대화 통계 훅
export function useConversationStats(messages: ConversationMessage[]) {
  const stats = {
    totalMessages: messages.length,
    userMessages: messages.filter(m => m.role === 'user').length,
    aiMessages: messages.filter(m => m.role === 'assistant').length,
    averageMessageLength: messages.length > 0
      ? Math.round(messages.reduce((sum, m) => sum + m.content.length, 0) / messages.length)
      : 0,
    conversationDuration: messages.length > 1 ? '진행 중' : '시작 전'
  };

  return stats;
}