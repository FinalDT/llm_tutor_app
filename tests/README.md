# 🧪 LLM Tutor API 테스트 가이드

프론트엔드 개발자와 UI/UX 디자이너를 위한 완전한 테스트 및 개발 가이드입니다.

## 📋 목차

- [빠른 시작](#빠른-시작)
- [프론트엔드 테스트](#프론트엔드-테스트)
- [API 테스트](#api-테스트)
- [데모 및 예제](#데모-및-예제)
- [Swagger API 문서](#swagger-api-문서)
- [트러블슈팅](#트러블슈팅)

## 🚀 빠른 시작

### 전체 폴더 구조
```
tests/
├── README.md                    # 📖 이 문서
├── frontend/                    # 🎨 프론트엔드 개발자용
│   ├── README.md               # Next.js 전용 가이드
│   ├── types/api.types.ts      # TypeScript 타입 정의
│   ├── utils/apiClient.ts      # API 클라이언트
│   ├── components/             # React 컴포넌트
│   │   ├── ChatInterface.tsx   # 메인 채팅 인터페이스
│   │   ├── LoadingSpinner.tsx  # 로딩 컴포넌트들
│   │   └── ErrorBoundary.tsx   # 에러 처리 컴포넌트들
│   ├── hooks/useTutorAPI.ts    # React 커스텀 훅
│   └── examples/               # 사용 예제들
├── api/                        # 🔧 API 테스트
│   ├── examples/
│   │   ├── test_complete_flow.py    # 전체 플로우 테스트
│   │   └── test_individual_steps.py # 개별 단계 테스트
├── demos/                      # 🎮 라이브 데모
└── swagger/                    # 📋 API 문서
    └── api-spec.yaml           # OpenAPI 스펙
```

### 사전 요구사항

**백엔드 서버 실행:**
```bash
# 프로젝트 루트에서
func start
```

**서버 확인:**
- 브라우저에서 `http://localhost:7071` 접속
- "Your Functions 4.0 app is up and running" 메시지 확인

## 🎨 프론트엔드 테스트

### Next.js + TypeScript 프로젝트 설정

**1. 파일 복사**
```bash
# 프론트엔드 프로젝트 루트에서
cp tests/frontend/types/api.types.ts ./src/types/
cp tests/frontend/utils/apiClient.ts ./src/utils/
cp tests/frontend/components/* ./src/components/
cp tests/frontend/hooks/useTutorAPI.ts ./src/hooks/
```

**2. 환경변수 설정**
```bash
# .env.local 파일 생성
NEXT_PUBLIC_API_URL=http://localhost:7071/api
NEXT_PUBLIC_TIMEOUT=30000
NEXT_PUBLIC_RETRY_ATTEMPTS=3
```

**3. 기본 사용법**
```typescript
import { ChatInterface } from '@/components/ChatInterface';
import { TutorErrorBoundary } from '@/components/ErrorBoundary';

export default function TutorPage() {
  return (
    <TutorErrorBoundary>
      <ChatInterface
        learnerID="A070001768"
        sessionID="rt-20250918:first6:A070001768:0"
      />
    </TutorErrorBoundary>
  );
}
```

### 🎯 주요 컴포넌트 설명

#### ChatInterface
- **기능**: 완전한 3단계 튜터링 플로우
- **특징**: 자동 상태 관리, 반응형 디자인, 접근성 지원
- **사용법**: `<ChatInterface learnerID="..." sessionID="..." />`

#### LoadingSpinner
- **기능**: 다양한 로딩 상태 표시
- **변형**: 기본, 인라인, 풀스크린, 메시지용
- **사용법**: `<LoadingSpinner message="로딩 중..." size="medium" />`

#### ErrorBoundary
- **기능**: React 에러 경계 및 API 에러 처리
- **특징**: 개발/운영 모드별 차별화된 표시
- **사용법**: `<TutorErrorBoundary>{children}</TutorErrorBoundary>`

### 🪝 커스텀 훅 활용

```typescript
import { useTutorAPI } from '@/hooks/useTutorAPI';

function MyTutorComponent() {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearError,
    reset
  } = useTutorAPI('A070001768', 'session-id');

  return (
    <div>
      {/* 채팅 UI 구현 */}
    </div>
  );
}
```

### 📱 반응형 디자인

모든 컴포넌트는 Tailwind CSS를 사용하여 완전 반응형으로 구현:
- **Mobile**: 768px 미만
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px 이상

## 🔧 API 테스트

### 백엔드 개발자용 테스트

**전체 플로우 테스트:**
```bash
python tests/api/examples/test_complete_flow.py
```

**개별 단계 테스트:**
```bash
python tests/api/examples/test_individual_steps.py
```

### 테스트 시나리오

#### 1. 진단테스트 요약 (1단계)
```python
# 기본 요청
{
  "request_type": "session_summary",
  "learnerID": "A070001768",
  "session_id": "rt-20250918:first6:A070001768:0"
}
```

#### 2. 유사문항 생성 (2단계)
```python
# 유사문항 요청
{
  "request_type": "item_feedback",
  "learnerID": "A070001768",
  "session_id": "rt-20250918:first6:A070001768:0",
  "message": "1번문제 유사 문항 주세요",
  "conversation_history": [...]
}
```

#### 3. 힌트 제공 (3단계)
```python
# 힌트 요청
{
  "request_type": "generated_item",
  "generated_question_data": {
    "new_question_text": "문제 내용...",
    "correct_answer": "정답",
    "explanation": "해설..."
  },
  "message": "힌트 주세요",
  "conversation_history": [...]
}
```

### 성능 및 품질 검증

**자동 검증 항목:**
- ✅ 응답 시간 (< 30초)
- ✅ 소크라틱 방식 (질문 형태 응답)
- ✅ 정답 직접 노출 방지
- ✅ 대화 기록 연속성
- ✅ 에러 처리 및 재시도

## 🎮 데모 및 예제

### 라이브 데모 (준비 중)
- 실시간 채팅 인터페이스 데모
- 다양한 학습자 시나리오 시뮬레이션
- 성능 모니터링 대시보드

### 사용 사례별 예제

**1. 기본 통합**
```typescript
// 최소한의 설정으로 튜터 기능 추가
import { api } from '@/utils/apiClient';

const response = await api.getSessionSummary('learnerID', 'sessionID');
if (response.data) {
  console.log(response.data.feedback);
}
```

**2. 고급 커스터마이징**
```typescript
// 커스텀 UI와 비즈니스 로직 통합
const tutorLogic = useTutorAPI('learnerID', 'sessionID');
// + 추가 상태 관리 및 UI 로직
```

## 📋 Swagger API 문서

### OpenAPI 스펙 활용

**Swagger UI 로컬 실행:**
```bash
# swagger-ui-serve 설치 (글로벌)
npm install -g swagger-ui-serve

# API 문서 서빙
swagger-ui-serve tests/swagger/api-spec.yaml
```

**TypeScript 타입 자동 생성:**
```bash
# swagger-codegen 사용
npx @openapitools/openapi-generator-cli generate \
  -i tests/swagger/api-spec.yaml \
  -g typescript-fetch \
  -o ./src/generated
```

### API 문서 주요 내용

- **엔드포인트**: `POST /api/tutor_api`
- **인증**: Function Level (자동 처리)
- **요청/응답 스키마**: 완전한 TypeScript 타입 정의
- **에러 코드**: 400 (Bad Request), 500 (Internal Server Error)

## 🔍 트러블슈팅

### 자주 발생하는 문제들

#### 1. 서버 연결 오류
```
❌ 서버 연결 실패 - func start로 서버를 시작하세요
```
**해결방법:**
```bash
# 프로젝트 루트에서
func start
```

#### 2. CORS 오류 (프론트엔드)
```
Access to fetch blocked by CORS policy
```
**해결방법:**
- Azure Functions CORS 설정 확인
- 개발 서버 URL이 허용 목록에 있는지 확인

#### 3. TypeScript 타입 오류
```
Property 'conversation_history' does not exist
```
**해결방법:**
```typescript
import { isAPISuccess } from '@/utils/apiClient';

if (isAPISuccess(response)) {
  // 타입 안전한 접근
  console.log(response.data.conversation_history);
}
```

#### 4. 환경변수 인식 안됨
```
NEXT_PUBLIC_API_URL is undefined
```
**해결방법:**
- `.env.local` 파일 위치 확인 (프로젝트 루트)
- 변수명에 `NEXT_PUBLIC_` 접두사 확인
- Next.js 서버 재시작

### 디버깅 도구

**개발 모드 로깅:**
```typescript
if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
  console.log('API Request:', request);
  console.log('API Response:', response);
}
```

**연결 상태 확인:**
```typescript
import { useConnectionStatus } from '@/hooks/useTutorAPI';

const { isConnected, checkConnection } = useConnectionStatus();
```

### 성능 최적화

**1. API 호출 최적화**
- 재시도 로직으로 안정성 확보
- 타임아웃 설정으로 응답성 보장
- 에러 처리로 사용자 경험 개선

**2. React 성능 최적화**
- 메모이제이션 활용 (`useMemo`, `useCallback`)
- 컴포넌트 분할로 재렌더링 최소화
- 가상화로 대용량 대화 기록 처리

**3. 메모리 관리**
- 자동 저장으로 데이터 손실 방지
- 적절한 클린업으로 메모리 누수 방지

## 📞 지원 및 문의

- **백엔드 API 이슈**: 기존 `test_api.py` 실행 및 로그 확인
- **프론트엔드 컴포넌트 이슈**: 브라우저 개발자 도구 네트워크 탭 확인
- **타입 관련 이슈**: `tests/frontend/types/api.types.ts` 참조
- **성능 이슈**: `tests/api/examples/test_complete_flow.py`의 성능 테스트 실행

## 🔄 업데이트 및 버전 관리

이 테스트 가이드는 API 변경사항에 따라 지속적으로 업데이트됩니다:

- **API 스키마 변경**: `api.types.ts` 자동 업데이트
- **컴포넌트 개선**: 새로운 UI 패턴 및 접근성 향상
- **성능 최적화**: 새로운 최적화 기법 및 베스트 프랙티스 적용

---

📝 **문서 버전**: v1.0.0
🕒 **마지막 업데이트**: 2024년 12월
👥 **작성자**: LLM Tutor Development Team