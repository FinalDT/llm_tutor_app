# Frontend Testing Guide

Next.js + TypeScript 프로젝트에서 LLM Tutor API를 사용하기 위한 완벽한 가이드입니다.

## 📋 목차

- [빠른 시작](#빠른-시작)
- [API 클라이언트 사용법](#api-클라이언트-사용법)
- [TypeScript 타입 활용](#typescript-타입-활용)
- [컴포넌트 예제](#컴포넌트-예제)
- [에러 처리](#에러-처리)
- [환경 설정](#환경-설정)
- [트러블슈팅](#트러블슈팅)

## 🚀 빠른 시작

### 1. 파일 복사
다음 파일들을 Next.js 프로젝트에 복사하세요:

```bash
# 타입 정의 파일
cp tests/frontend/types/api.types.ts ./src/types/
cp tests/frontend/utils/apiClient.ts ./src/utils/
```

### 2. 환경변수 설정
`.env.local` 파일에 다음을 추가:

```env
NEXT_PUBLIC_API_URL=http://localhost:7071/api
NEXT_PUBLIC_TIMEOUT=30000
NEXT_PUBLIC_RETRY_ATTEMPTS=3
```

### 3. 기본 사용법

```typescript
import { api, isAPISuccess } from '@/utils/apiClient';

// 진단테스트 요약 요청
const response = await api.getSessionSummary(
  'A070001768',
  'rt-20250918:first6:A070001768:0'
);

if (isAPISuccess(response)) {
  console.log('피드백:', response.data.feedback);
} else {
  console.error('에러:', response.error?.error);
}
```

## 🔌 API 클라이언트 사용법

### 진단테스트 요약 (1단계)

```typescript
import { api, ConversationMessage } from '@/utils/apiClient';

const getSummary = async () => {
  const response = await api.getSessionSummary(
    'A070001768',                           // 학습자 ID
    'rt-20250918:first6:A070001768:0',     // 세션 ID
    []                                      // 대화 기록 (선택적)
  );

  if (response.data) {
    setFeedback(response.data.feedback);
    setConversationHistory(response.data.conversation_history);
  } else {
    setError(response.error?.error || '요청 실패');
  }
};
```

### 유사문항 생성 (2단계)

```typescript
const requestSimilarItem = async () => {
  const response = await api.requestSimilarItem(
    'A070001768',                           // 학습자 ID
    'rt-20250918:first6:A070001768:0',     // 세션 ID
    '1번문제 유사 문항 주세요',              // 요청 메시지
    conversationHistory                     // 이전 대화 기록
  );

  if (response.data) {
    setFeedback(response.data.feedback);
    setGeneratedQuestion(response.data.generated_question_data);
    setConversationHistory(response.data.conversation_history);
  }
};
```

### 힌트 요청 (3단계)

```typescript
const requestHint = async () => {
  const questionData = {
    new_question_text: "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요...",
    correct_answer: "72 cm²",
    explanation: "각기둥의 겉넓이는..."
  };

  const response = await api.requestHint(
    questionData,                           // 문제 데이터
    '모르겠어요',                           // 학생 메시지
    conversationHistory,                    // 대화 기록
    'A070001768',                          // 학습자 ID (선택적)
    '각기둥의 겉넓이'                       // 개념명 (선택적)
  );

  if (response.data) {
    setHint(response.data.feedback);
    setConversationHistory(response.data.conversation_history);
  }
};
```

## 📝 TypeScript 타입 활용

### 기본 타입 import

```typescript
import {
  TutorAPIRequest,
  TutorAPIResponse,
  ConversationMessage,
  GeneratedQuestion,
  TutorState,
  TutorActions,
  APIResponse
} from '@/types/api.types';
```

### 컴포넌트 상태 관리

```typescript
const [tutorState, setTutorState] = useState<TutorState>({
  messages: [],
  isLoading: false,
  error: null,
  currentQuestion: undefined
});
```

### 타입 가드 사용

```typescript
import { isAPISuccess } from '@/utils/apiClient';

const handleAPICall = async () => {
  const response = await api.getSessionSummary('학습자ID', '세션ID');

  if (isAPISuccess(response)) {
    // response.data가 TutorAPIResponse 타입으로 보장됨
    console.log(response.data.feedback);
  } else {
    // response.error가 TutorAPIError 타입으로 보장됨
    console.error(response.error?.error);
  }
};
```

## 🧩 컴포넌트 예제

### 기본 채팅 인터페이스

```typescript
'use client';

import { useState, useEffect } from 'react';
import { api, isAPISuccess } from '@/utils/apiClient';
import { TutorState, ConversationMessage } from '@/types/api.types';

interface ChatInterfaceProps {
  learnerID: string;
  sessionID: string;
}

export default function ChatInterface({ learnerID, sessionID }: ChatInterfaceProps) {
  const [state, setState] = useState<TutorState>({
    messages: [],
    isLoading: false,
    error: null
  });

  const [inputMessage, setInputMessage] = useState('');

  // 초기 세션 요약 요청
  useEffect(() => {
    const initSession = async () => {
      setState(prev => ({ ...prev, isLoading: true }));

      const response = await api.getSessionSummary(learnerID, sessionID);

      if (isAPISuccess(response)) {
        setState(prev => ({
          ...prev,
          messages: response.data.conversation_history,
          isLoading: false
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: response.error?.error || '세션 로드 실패',
          isLoading: false
        }));
      }
    };

    initSession();
  }, [learnerID, sessionID]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    setState(prev => ({ ...prev, isLoading: true }));

    const response = await api.requestSimilarItem(
      learnerID,
      sessionID,
      inputMessage,
      state.messages
    );

    if (isAPISuccess(response)) {
      setState(prev => ({
        ...prev,
        messages: response.data.conversation_history,
        currentQuestion: response.data.generated_question_data,
        isLoading: false
      }));
    } else {
      setState(prev => ({
        ...prev,
        error: response.error?.error || '메시지 전송 실패',
        isLoading: false
      }));
    }

    setInputMessage('');
  };

  return (
    <div className="chat-interface">
      <div className="messages">
        {state.messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <strong>{message.role}:</strong> {message.content}
          </div>
        ))}
      </div>

      {state.error && (
        <div className="error">에러: {state.error}</div>
      )}

      <div className="input-area">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          disabled={state.isLoading}
          placeholder="메시지를 입력하세요..."
        />
        <button onClick={sendMessage} disabled={state.isLoading}>
          {state.isLoading ? '전송 중...' : '전송'}
        </button>
      </div>
    </div>
  );
}
```

### 로딩 스피너 컴포넌트

```typescript
import { LoadingSpinnerProps } from '@/types/api.types';

export default function LoadingSpinner({
  message = "AI가 답변을 생각하고 있어요...",
  size = 'medium'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`animate-spin rounded-full border-2 border-blue-300 border-t-blue-600 ${sizeClasses[size]}`} />
      {message && <span className="text-gray-600">{message}</span>}
    </div>
  );
}
```

## ⚠️ 에러 처리

### 네트워크 오류 처리

```typescript
import { handleAPIError } from '@/utils/apiClient';

const handleNetworkError = (response: APIResponse<any>) => {
  if (response.status === 408) {
    alert('요청 시간이 초과되었습니다. 다시 시도해주세요.');
  } else if (response.status >= 500) {
    alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
  } else {
    alert(handleAPIError(response.error));
  }
};
```

### React Error Boundary

```typescript
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class TutorErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>튜터 시스템에 오류가 발생했습니다</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            페이지 새로고침
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## 🔧 환경 설정

### Next.js 환경변수

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:7071/api
NEXT_PUBLIC_TIMEOUT=30000
NEXT_PUBLIC_RETRY_ATTEMPTS=3

# 개발 환경
NEXT_PUBLIC_DEBUG=true

# 운영 환경
NEXT_PUBLIC_API_URL=https://your-azure-function.azurewebsites.net/api
NEXT_PUBLIC_DEBUG=false
```

### API 클라이언트 설정 커스터마이징

```typescript
import { TutorAPIClient } from '@/utils/apiClient';

// 커스텀 설정으로 클라이언트 생성
const customClient = new TutorAPIClient({
  baseURL: 'https://custom-api.com/api',
  timeout: 60000,
  retryAttempts: 5,
  retryDelay: 2000
});

// 기존 클라이언트 설정 업데이트
tutorAPI.updateConfig({
  timeout: 45000,
  retryAttempts: 2
});
```

## 🔍 트러블슈팅

### 자주 발생하는 문제들

#### 1. CORS 오류
```
Access to fetch at 'http://localhost:7071/api/tutor_api' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**해결방법**: Azure Functions의 CORS 설정에 Next.js 개발 서버 URL 추가

#### 2. 타입 오류
```
Property 'conversation_history' does not exist on type 'TutorAPIResponse'
```

**해결방법**: API 응답 타입 확인 및 타입 가드 사용
```typescript
if (isAPISuccess(response) && response.data.conversation_history) {
  // 안전한 접근
}
```

#### 3. 환경변수 인식 안됨
```
NEXT_PUBLIC_API_URL is undefined
```

**해결방법**:
- `.env.local` 파일 위치 확인 (프로젝트 루트)
- Next.js 서버 재시작
- 환경변수명에 `NEXT_PUBLIC_` 접두사 확인

### 디버깅 도구

```typescript
// 개발 모드에서 API 호출 로깅
if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
  console.log('API Request:', request);
  console.log('API Response:', response);
}

// 서버 연결 상태 확인
const checkConnection = async () => {
  const health = await api.healthCheck();
  console.log('Server health:', health);
};
```

## 📚 추가 리소스

- [Next.js App Router 문서](https://nextjs.org/docs/app)
- [TypeScript 핸드북](https://www.typescriptlang.org/docs/)
- [Azure Functions 문서](https://docs.microsoft.com/azure/azure-functions/)

## 🆘 도움이 필요하다면

1. API 서버가 실행 중인지 확인: `http://localhost:7071`
2. 백엔드 테스트 스크립트 실행: `python test_api.py`
3. 브라우저 개발자 도구에서 네트워크 탭 확인
4. 트러블슈팅로그.md 파일 참조