/**
 * LLM Tutor API TypeScript Interface Definitions
 * Next.js + TypeScript 프로젝트용 타입 정의
 */

// 기본 메시지 구조
export interface ConversationMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

// 생성된 문항 데이터 구조
export interface GeneratedQuestion {
  new_question_text: string;
  correct_answer: string;
  explanation: string;
}

// API 요청 타입들
export type RequestType = 'session_summary' | 'item_feedback' | 'generated_item';

// 1단계: 진단테스트 요약 요청
export interface SessionSummaryRequest {
  request_type: 'session_summary';
  learnerID: string;
  session_id: string;
  conversation_history?: ConversationMessage[];
}

// 2단계: 유사문항 생성 요청
export interface ItemFeedbackRequest {
  request_type: 'item_feedback';
  learnerID: string;
  session_id: string;
  message: string;
  conversation_history: ConversationMessage[];
}

// 3단계: 힌트 제공 요청
export interface GeneratedItemRequest {
  request_type: 'generated_item';
  generated_question_data: GeneratedQuestion;
  message: string;
  conversation_history: ConversationMessage[];
  learnerID?: string; // 선택적 개인화 정보
  original_concept?: string; // 선택적 원본 개념
}

// 통합 API 요청 타입
export type TutorAPIRequest = SessionSummaryRequest | ItemFeedbackRequest | GeneratedItemRequest;

// API 응답 구조
export interface TutorAPIResponse {
  feedback: string;
  conversation_history: ConversationMessage[];
  generated_question_data?: GeneratedQuestion; // 유사문항 생성 시에만 포함
}

// 에러 응답 구조
export interface TutorAPIError {
  error: string;
}

// API 클라이언트 설정
export interface APIClientConfig {
  baseURL?: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
}

// 개인화 데이터 (내부 처리용)
export interface PersonalizationData {
  learner_id?: string;
  original_concept?: string;
  personal_accuracy?: number;
  hint_level?: 'beginner' | 'intermediate' | 'advanced';
}

// 답안 분석 결과 (내부 처리용)
export interface AnswerAnalysis {
  confidence: number;
  is_partial_correct: boolean;
  has_good_approach: boolean;
}

// React Hook용 상태 타입들
export interface TutorState {
  messages: ConversationMessage[];
  isLoading: boolean;
  error: string | null;
  currentQuestion?: GeneratedQuestion;
}

export interface TutorActions {
  sendMessage: (message: string) => Promise<void>;
  startSession: (learnerID: string, sessionID: string) => Promise<void>;
  requestSimilarItem: (questionNumber: string) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

// 컴포넌트 Props 타입들
export interface ChatInterfaceProps {
  learnerID: string;
  sessionID: string;
  onStateChange?: (state: TutorState) => void;
}

export interface MessageBubbleProps {
  message: ConversationMessage;
  isLoading?: boolean;
}

export interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
}

// 유틸리티 타입들
export type APIStatus = 'idle' | 'loading' | 'success' | 'error';

export interface APIResult<T> {
  data?: T;
  error?: string;
  status: APIStatus;
}

// 환경변수 타입
export interface EnvConfig {
  NEXT_PUBLIC_API_URL: string;
  NEXT_PUBLIC_TIMEOUT?: string;
  NEXT_PUBLIC_RETRY_ATTEMPTS?: string;
}

// HTTP 상태 코드 타입
export type HTTPStatusCode = 200 | 400 | 401 | 403 | 404 | 500 | 502 | 503 | 504;

// API 응답 래퍼
export interface APIResponse<T> {
  data?: T;
  error?: TutorAPIError;
  status: HTTPStatusCode;
  headers?: Record<string, string>;
}