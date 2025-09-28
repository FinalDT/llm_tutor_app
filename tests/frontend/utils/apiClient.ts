/**
 * LLM Tutor API Client for Next.js + TypeScript
 * 타입 안전한 API 클라이언트 구현
 */

import {
  TutorAPIRequest,
  TutorAPIResponse,
  TutorAPIError,
  APIClientConfig,
  APIResponse,
  HTTPStatusCode,
  SessionSummaryRequest,
  ItemFeedbackRequest,
  GeneratedItemRequest,
  ConversationMessage,
  GeneratedQuestion
} from '../types/api.types';

export class TutorAPIClient {
  private baseURL: string;
  private timeout: number;
  private retryAttempts: number;
  private retryDelay: number;

  constructor(config: APIClientConfig = {}) {
    this.baseURL = config.baseURL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7071/api';
    this.timeout = config.timeout || 30000; // 30초
    this.retryAttempts = config.retryAttempts || 3;
    this.retryDelay = config.retryDelay || 1000; // 1초
  }

  /**
   * 기본 HTTP 요청 메서드
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const url = `${this.baseURL}/${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      const status = response.status as HTTPStatusCode;
      const responseData = await response.json();

      if (!response.ok) {
        return {
          error: responseData as TutorAPIError,
          status,
          headers: this.extractHeaders(response.headers),
        };
      }

      return {
        data: responseData as T,
        status,
        headers: this.extractHeaders(response.headers),
      };
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error && error.name === 'AbortError') {
        return {
          error: { error: 'Request timeout' },
          status: 408 as HTTPStatusCode,
        };
      }

      return {
        error: { error: error instanceof Error ? error.message : 'Unknown error' },
        status: 500 as HTTPStatusCode,
      };
    }
  }

  /**
   * 재시도 로직이 포함된 요청
   */
  private async requestWithRetry<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    let lastError: APIResponse<T> | null = null;

    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      const result = await this.request<T>(endpoint, options);

      if (result.data || (result.status && result.status < 500)) {
        return result;
      }

      lastError = result;

      if (attempt < this.retryAttempts) {
        await this.delay(this.retryDelay * attempt);
      }
    }

    return lastError || {
      error: { error: 'Maximum retry attempts exceeded' },
      status: 500 as HTTPStatusCode,
    };
  }

  /**
   * 응답 헤더 추출
   */
  private extractHeaders(headers: Headers): Record<string, string> {
    const result: Record<string, string> = {};
    headers.forEach((value, key) => {
      result[key] = value;
    });
    return result;
  }

  /**
   * 지연 함수
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 메인 API 호출 메서드
   */
  async sendRequest(request: TutorAPIRequest): Promise<APIResponse<TutorAPIResponse>> {
    return this.requestWithRetry<TutorAPIResponse>('tutor_api', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * 1단계: 진단테스트 요약 요청
   */
  async getSessionSummary(
    learnerID: string,
    sessionID: string,
    conversationHistory: ConversationMessage[] = []
  ): Promise<APIResponse<TutorAPIResponse>> {
    const request: SessionSummaryRequest = {
      request_type: 'session_summary',
      learnerID,
      session_id: sessionID,
      conversation_history: conversationHistory,
    };

    return this.sendRequest(request);
  }

  /**
   * 2단계: 유사문항 생성 요청
   */
  async requestSimilarItem(
    learnerID: string,
    sessionID: string,
    message: string,
    conversationHistory: ConversationMessage[]
  ): Promise<APIResponse<TutorAPIResponse>> {
    const request: ItemFeedbackRequest = {
      request_type: 'item_feedback',
      learnerID,
      session_id: sessionID,
      message,
      conversation_history: conversationHistory,
    };

    return this.sendRequest(request);
  }

  /**
   * 3단계: 힌트 제공 요청
   */
  async requestHint(
    questionData: GeneratedQuestion,
    message: string,
    conversationHistory: ConversationMessage[],
    learnerID?: string,
    originalConcept?: string
  ): Promise<APIResponse<TutorAPIResponse>> {
    const request: GeneratedItemRequest = {
      request_type: 'generated_item',
      generated_question_data: questionData,
      message,
      conversation_history: conversationHistory,
      learnerID,
      original_concept: originalConcept,
    };

    return this.sendRequest(request);
  }

  /**
   * 연결 상태 확인
   */
  async healthCheck(): Promise<APIResponse<{ status: string }>> {
    try {
      const response = await fetch(this.baseURL.replace('/api', ''), {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });

      if (response.ok) {
        return {
          data: { status: 'healthy' },
          status: 200 as HTTPStatusCode,
        };
      } else {
        return {
          error: { error: 'Server not responding' },
          status: response.status as HTTPStatusCode,
        };
      }
    } catch (error) {
      return {
        error: { error: 'Connection failed' },
        status: 503 as HTTPStatusCode,
      };
    }
  }

  /**
   * 설정 업데이트
   */
  updateConfig(config: Partial<APIClientConfig>): void {
    if (config.baseURL) this.baseURL = config.baseURL;
    if (config.timeout) this.timeout = config.timeout;
    if (config.retryAttempts) this.retryAttempts = config.retryAttempts;
    if (config.retryDelay) this.retryDelay = config.retryDelay;
  }

  /**
   * 현재 설정 조회
   */
  getConfig(): APIClientConfig {
    return {
      baseURL: this.baseURL,
      timeout: this.timeout,
      retryAttempts: this.retryAttempts,
      retryDelay: this.retryDelay,
    };
  }
}

// 기본 클라이언트 인스턴스 (싱글톤 패턴)
export const tutorAPI = new TutorAPIClient();

// Next.js에서 사용하기 쉬운 래퍼 함수들
export const api = {
  /**
   * 진단테스트 요약
   */
  getSessionSummary: (learnerID: string, sessionID: string, history?: ConversationMessage[]) =>
    tutorAPI.getSessionSummary(learnerID, sessionID, history),

  /**
   * 유사문항 요청
   */
  requestSimilarItem: (
    learnerID: string,
    sessionID: string,
    message: string,
    history: ConversationMessage[]
  ) => tutorAPI.requestSimilarItem(learnerID, sessionID, message, history),

  /**
   * 힌트 요청
   */
  requestHint: (
    question: GeneratedQuestion,
    message: string,
    history: ConversationMessage[],
    learnerID?: string,
    concept?: string
  ) => tutorAPI.requestHint(question, message, history, learnerID, concept),

  /**
   * 서버 상태 확인
   */
  healthCheck: () => tutorAPI.healthCheck(),
};

// 에러 처리 유틸리티
export const handleAPIError = (error: TutorAPIError | undefined): string => {
  if (!error) return 'Unknown error occurred';
  return error.error || 'Server error occurred';
};

// 응답 성공 여부 확인
export const isAPISuccess = <T>(response: APIResponse<T>): response is APIResponse<T> & { data: T } => {
  return !!response.data && !response.error;
};