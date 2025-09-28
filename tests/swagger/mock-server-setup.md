# 🎭 Mock 서버 설정 가이드

백엔드 개발 완료 전에 프론트엔드 개발을 시작할 수 있도록 하는 Mock 서버 설정 가이드입니다.

## 📋 목차

- [Mock 서버란?](#mock-서버란)
- [Prism Mock 서버](#prism-mock-서버)
- [JSON Server Mock](#json-server-mock)
- [MSW (Mock Service Worker)](#msw-mock-service-worker)
- [실제 응답 시뮬레이션](#실제-응답-시뮬레이션)
- [팀 워크플로우](#팀-워크플로우)

## 🤔 Mock 서버란?

Mock 서버는 실제 백엔드 API가 준비되지 않은 상황에서 API 스펙에 따라 가짜 응답을 제공하는 서버입니다.

### 장점
- ✅ **병렬 개발**: 백엔드 완성을 기다리지 않고 프론트엔드 개발 시작
- ✅ **빠른 프로토타이핑**: UI/UX 검증을 위한 빠른 데모 제작
- ✅ **테스트 환경**: 일관된 테스트 데이터로 안정적인 테스트
- ✅ **API 스펙 검증**: 실제 구현 전에 API 설계 검증

### LLM Tutor API Mock 서버 특징
- 🤖 실제 한국어 AI 응답 시뮬레이션
- 📊 3단계 학습 플로우 완전 구현
- 🎯 소크라틱 방식 응답 패턴
- 💬 대화 기록 상태 관리

## 🚀 Prism Mock 서버

### 설치 및 실행
```bash
# Prism 설치
npm install -g @stoplight/prism-cli

# 기본 Mock 서버 실행
prism mock tests/swagger/api-spec.yaml

# 포트 지정 실행
prism mock -p 4010 tests/swagger/api-spec.yaml

# 다이나믹 응답 (매번 다른 예제 응답)
prism mock --dynamic tests/swagger/api-spec.yaml

# 디버그 모드
prism mock --verbosity debug tests/swagger/api-spec.yaml
```

### 실행 결과
```
[CLI] …  awaiting  Starting Prism…
[CLI] ℹ  info      POST http://127.0.0.1:4010/tutor_api
[CLI] ▶  start     Prism is listening on http://127.0.0.1:4010
```

### Mock API 테스트
```bash
# 1단계: 진단테스트 요약 테스트
curl -X POST http://localhost:4010/tutor_api \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "session_summary",
    "learnerID": "A070001768",
    "session_id": "rt-20250918:first6:A070001768:0"
  }'

# 특정 예제 응답 요청
curl -X POST http://localhost:4010/tutor_api \
  -H "Content-Type: application/json" \
  -H "Prefer: example=session_summary_response" \
  -d '{
    "request_type": "session_summary",
    "learnerID": "A070001768",
    "session_id": "rt-20250918:first6:A070001768:0"
  }'
```

### 프론트엔드에서 Mock 서버 사용
```typescript
// API 클라이언트 Mock 모드 설정
const apiClient = new TutorAPIClient({
  baseURL: process.env.NODE_ENV === 'development'
    ? 'http://localhost:4010'  // Mock 서버
    : 'http://localhost:7071/api'  // 실제 서버
});

// 환경변수로 제어
// .env.local
NEXT_PUBLIC_USE_MOCK=true
NEXT_PUBLIC_MOCK_API_URL=http://localhost:4010
NEXT_PUBLIC_REAL_API_URL=http://localhost:7071/api
```

## 📦 JSON Server Mock

더 간단한 Mock 서버가 필요한 경우 JSON Server를 사용할 수 있습니다.

### 설치 및 데이터 준비
```bash
# JSON Server 설치
npm install -g json-server

# Mock 데이터 생성
cat > tests/swagger/mock-data.json << 'EOF'
{
  "session_summary": {
    "feedback": "진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.\n\n전체 6 문제 중에서 2 문제를 맞혔네. 정말 잘했어! 👍\n\n이번 테스트에서는 아쉽게도 1, 2, 4, 5 번 문제를 틀렸더라. 데이터를 분석해보니, 주로 \"부채꼴의 호의 길이와 넓이 사이의 관계, 다각형의 내각의 크기의 합, 원뿔의 겉넓이, 각기둥의 겉넓이\" 개념들이 조금 헷갈리는 것 같아.\n\n우리 같이 \"부채꼴의 호의 길이와 넓이 사이의 관계\"에 대한 학습을 시작해볼까?",
    "conversation_history": [
      {"role": "user", "content": "피드백 요청"},
      {"role": "assistant", "content": "진단 테스트 푸느라 수고 많았어! 결과를 알려줄게..."}
    ]
  },
  "item_feedback": {
    "feedback": "좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까? 아래 문제를 풀어봐.\n\n높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요. 정사각형의 한 변의 길이는 4cm입니다.",
    "conversation_history": [
      {"role": "user", "content": "1번문제 유사 문항 주세요"},
      {"role": "assistant", "content": "좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까?"}
    ],
    "generated_question_data": {
      "new_question_text": "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요. 정사각형의 한 변의 길이는 4cm입니다.",
      "correct_answer": "72 cm²",
      "explanation": "각기둥의 겉넓이는 밑면의 넓이와 옆면의 넓이를 모두 더하여 구합니다..."
    }
  },
  "generated_item": {
    "feedback": "각기둥의 겉넓이를 구하려면 어떤 면들의 넓이를 더해야 할까요?",
    "conversation_history": [
      {"role": "user", "content": "모르겠어요"},
      {"role": "assistant", "content": "각기둥의 겉넓이를 구하려면 어떤 면들의 넓이를 더해야 할까요?"}
    ]
  }
}
EOF
```

### JSON Server 실행 및 라우팅
```bash
# 기본 실행
json-server --watch tests/swagger/mock-data.json --port 3001

# CORS 활성화
json-server --watch tests/swagger/mock-data.json --port 3001 --middlewares cors

# 커스텀 라우팅
cat > tests/swagger/routes.json << 'EOF'
{
  "/tutor_api": "/session_summary",
  "/tutor_api?request_type=item_feedback": "/item_feedback",
  "/tutor_api?request_type=generated_item": "/generated_item"
}
EOF

json-server --watch tests/swagger/mock-data.json --routes tests/swagger/routes.json --port 3001
```

## 🌐 MSW (Mock Service Worker)

브라우저에서 직접 동작하는 서비스 워커 기반 모킹 라이브러리입니다.

### 설치 및 설정
```bash
# MSW 설치
npm install --save-dev msw

# 서비스 워커 파일 생성
npx msw init public/ --save
```

### Mock 핸들러 설정
```typescript
// src/mocks/handlers.ts
import { rest } from 'msw';
import { TutorAPIResponse } from '../types/api.types';

export const handlers = [
  // 1단계: 진단테스트 요약
  rest.post('/api/tutor_api', (req, res, ctx) => {
    const body = req.body as any;

    if (body.request_type === 'session_summary') {
      const response: TutorAPIResponse = {
        feedback: "진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.\n\n전체 6 문제 중에서 2 문제를 맞혔네. 정말 잘했어! 👍",
        conversation_history: [
          { role: "user", content: "피드백 요청" },
          { role: "assistant", content: "진단 테스트 푸느라 수고 많았어!" }
        ]
      };

      return res(
        ctx.delay(1000), // 실제 API 지연 시뮬레이션
        ctx.status(200),
        ctx.json(response)
      );
    }

    // 2단계: 유사문항 생성
    if (body.request_type === 'item_feedback') {
      const response: TutorAPIResponse = {
        feedback: "좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까?",
        conversation_history: [
          ...body.conversation_history,
          { role: "user", content: body.message },
          { role: "assistant", content: "좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까?" }
        ],
        generated_question_data: {
          new_question_text: "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요.",
          correct_answer: "72 cm²",
          explanation: "각기둥의 겉넓이는 밑면의 넓이와 옆면의 넓이를 모두 더하여 구합니다..."
        }
      };

      return res(ctx.status(200), ctx.json(response));
    }

    // 3단계: 힌트 제공
    if (body.request_type === 'generated_item') {
      const socraticHints = [
        "각기둥의 겉넓이를 구하려면 어떤 면들의 넓이를 더해야 할까요?",
        "정사각형 밑면이 몇 개 있는지 생각해보세요.",
        "옆면은 어떤 도형일까요?",
        "각각의 면의 넓이를 구해서 더해보세요."
      ];

      const randomHint = socraticHints[Math.floor(Math.random() * socraticHints.length)];

      const response: TutorAPIResponse = {
        feedback: randomHint,
        conversation_history: [
          ...body.conversation_history,
          { role: "user", content: body.message },
          { role: "assistant", content: randomHint }
        ]
      };

      return res(ctx.status(200), ctx.json(response));
    }

    // 에러 케이스
    return res(
      ctx.status(400),
      ctx.json({ error: "Invalid request_type" })
    );
  }),

  // 에러 시뮬레이션
  rest.post('/api/tutor_api/error', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ error: "Internal server error" })
    );
  })
];
```

### 브라우저에서 MSW 활성화
```typescript
// src/mocks/browser.ts
import { setupWorker } from 'msw';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);

// src/index.tsx 또는 _app.tsx
if (process.env.NODE_ENV === 'development') {
  const { worker } = await import('./mocks/browser');
  worker.start();
}
```

## 📊 실제 응답 시뮬레이션

### 동적 응답 생성
```typescript
// 실제와 유사한 동적 응답 생성
function generateDynamicResponse(requestType: string, userMessage: string) {
  const responses = {
    hint_request: [
      "각기둥의 겉넓이를 구하려면 어떤 면들의 넓이를 더해야 할까요?",
      "정사각형 밑면의 넓이부터 계산해볼까요?",
      "옆면은 직사각형인데, 몇 개나 있을까요?"
    ],
    confusion: [
      "어떤 부분이 헷갈리는지 더 구체적으로 말해줄래요?",
      "지금까지 계산한 것을 한번 보여주세요.",
      "문제를 차근차근 다시 읽어볼까요?"
    ],
    encouragement: [
      "좋은 시도예요! 조금만 더 생각해보세요.",
      "정답에 가까워지고 있어요!",
      "이미 잘하고 있으니 자신감을 가지세요."
    ]
  };

  // 사용자 메시지 분석
  const messageType = userMessage.includes('힌트') ? 'hint_request' :
                     userMessage.includes('모르') ? 'confusion' : 'encouragement';

  const possibleResponses = responses[messageType];
  return possibleResponses[Math.floor(Math.random() * possibleResponses.length)];
}
```

### 상태 기반 응답
```typescript
// 대화 상태에 따른 응답 변화
function getContextualResponse(conversationHistory: ConversationMessage[], currentMessage: string) {
  const aiMessageCount = conversationHistory.filter(m => m.role === 'assistant').length;

  // 첫 번째 힌트
  if (aiMessageCount === 0) {
    return "차근차근 시작해볼까요? 각기둥은 어떤 면들로 이루어져 있을까요?";
  }

  // 두 번째 힌트
  if (aiMessageCount === 1) {
    return "맞아요! 밑면 2개와 옆면들이 있겠네요. 각각의 넓이를 구해볼까요?";
  }

  // 세 번째 힌트 이후
  return generateDynamicResponse('hint_request', currentMessage);
}
```

### 에러 시나리오 시뮬레이션
```typescript
// 다양한 에러 상황 시뮬레이션
const errorScenarios = [
  {
    condition: (req) => !req.body.learnerID,
    response: { error: "Required fields are missing: learnerID" },
    status: 400
  },
  {
    condition: (req) => req.body.learnerID === 'INVALID',
    response: { error: "Invalid learner ID format" },
    status: 400
  },
  {
    condition: () => Math.random() < 0.1, // 10% 확률로 서버 오류
    response: { error: "Temporary server error" },
    status: 500
  }
];
```

## 👥 팀 워크플로우

### 개발 단계별 Mock 서버 활용

#### 1단계: API 설계 및 검증
```bash
# 1. OpenAPI 스펙 작성
# 2. Swagger UI로 스펙 검토
swagger-ui-serve tests/swagger/api-spec.yaml

# 3. Mock 서버로 초기 검증
prism mock tests/swagger/api-spec.yaml
```

#### 2단계: 프론트엔드 개발
```bash
# 1. Mock 서버 실행
prism mock --dynamic tests/swagger/api-spec.yaml

# 2. 프론트엔드 개발 서버 실행
npm run dev

# 3. Mock 응답으로 UI 개발 및 테스트
```

#### 3단계: 백엔드 개발 및 통합
```bash
# 1. 백엔드 개발 완료 후 실제 서버 실행
func start

# 2. 프론트엔드 API URL 변경
# NEXT_PUBLIC_API_URL=http://localhost:7071/api

# 3. 실제 API와 Mock API 응답 비교 테스트
```

### 팀 컨벤션 설정
```typescript
// 환경별 API 설정
const getAPIConfig = () => {
  if (process.env.NEXT_PUBLIC_USE_MOCK === 'true') {
    return {
      baseURL: 'http://localhost:4010',
      mode: 'mock'
    };
  }

  if (process.env.NODE_ENV === 'development') {
    return {
      baseURL: 'http://localhost:7071/api',
      mode: 'development'
    };
  }

  return {
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    mode: 'production'
  };
};
```

### Mock 데이터 관리
```bash
# Mock 데이터 버전 관리
tests/swagger/mock-data/
├── v1.0/
│   ├── session-summary.json
│   ├── item-feedback.json
│   └── generated-item.json
├── scenarios/
│   ├── happy-path.json
│   ├── error-cases.json
│   └── edge-cases.json
└── current -> v1.0/
```

## 📋 체크리스트

### Mock 서버 설정 완료 확인
- [ ] Prism Mock 서버 실행 가능
- [ ] 모든 API 엔드포인트 응답 확인
- [ ] 한국어 응답 데이터 품질 검증
- [ ] 에러 시나리오 동작 확인
- [ ] 프론트엔드 연동 테스트 완료

### 팀 협업 준비
- [ ] Mock 서버 실행 스크립트 공유
- [ ] 환경변수 설정 가이드 전달
- [ ] API 응답 예제 문서화
- [ ] 에러 케이스 대응 방법 정리

---

Mock 서버를 통해 백엔드 완성을 기다리지 않고 효율적인 프론트엔드 개발이 가능합니다! 🚀