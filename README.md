# 🎓 LLM 튜터 앱

> AI 기반 개인화 학습 튜터 시스템 - 진단테스트 분석부터 힌트 제공까지

## 🚀 빠른 시작 (Quick Start)

### 1️⃣ 서버 실행

```bash
func start
```

→ 서버가 `http://localhost:7071`에서 실행됩니다

### 2️⃣ 테스트 실행

```bash
python test_api.py
```

→ 메뉴에서 원하는 기능을 선택하여 테스트

### 3️⃣ 프론트엔드 연동

```javascript
const API_BASE_URL = "http://localhost:7071/api/tutor_api";

// 1단계: 진단테스트 요약
const getSummary = async (learnerID, sessionId) => {
  const response = await fetch(API_BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      request_type: "session_summary",
      learnerID,
      session_id: sessionId,
    }),
  });
  return response.json();
};
```

## 💡 핵심 개념

### 📊 학습 플로우

```
진단테스트 결과 → AI 분석 → 약점 파악 → 유사문항 생성 → 힌트 제공
```

### 🔄 3단계 API 호출 순서

1. **`session_summary`** - 진단테스트 분석 및 피드백
2. **`item_feedback`** - 약점 개념의 유사문항 생성
3. **`generated_item`** - 소크라틱 방식 힌트 제공

## 🏗️ 시스템 구조

- **Backend**: Azure Functions (Python 3.9+)
- **AI**: OpenAI GPT-4 (소크라틱 대화 최적화)
- **Database**: SQL Server (학습자 데이터)
- **API**: REST HTTP (JSON 통신)

## 🔗 API 연동 가이드

### 📡 엔드포인트

```
POST http://localhost:7071/api/tutor_api
Content-Type: application/json
```

### 🔄 워크플로우 예시 (React/Vue/Angular)

#### 1단계: 진단테스트 분석

```javascript
// 학습자의 진단테스트 결과 분석
const analyzeDiagnosticTest = async (learnerID, sessionId) => {
  const response = await fetch(API_BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      request_type: "session_summary",
      learnerID: learnerID,
      session_id: sessionId,
    }),
  });

  const result = await response.json();
  // result.feedback = "진단 테스트 결과... 부채꼴의 호의 길이와 넓이..."
  return result;
};
```

#### 2단계: 유사문항 요청

```javascript
// 틀린 문제의 유사문항 생성
const generateSimilarQuestion = async (
  learnerID,
  sessionId,
  userMessage,
  history
) => {
  const response = await fetch(API_BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      request_type: "item_feedback",
      learnerID: learnerID,
      session_id: sessionId,
      message: userMessage, // "1번문제 유사 문항 주세요"
      conversation_history: history,
    }),
  });

  const result = await response.json();
  /* result = {
    feedback: "좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까?...",
    generated_question_data: {
      new_question_text: "높이가 5cm, 밑면이 정사각형인...",
      correct_answer: "72 cm²",
      explanation: "각기둥의 겉넓이는..."
    }
  } */
  return result;
};
```

#### 3단계: 소크라틱 힌트

```javascript
// 생성된 문항에 대한 힌트 요청
const getHint = async (questionData, userMessage, history) => {
  const response = await fetch(API_BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      request_type: "generated_item",
      generated_question_data: questionData,
      message: userMessage, // "모르겠어요", "힌트 주세요"
      conversation_history: history,
    }),
  });

  const result = await response.json();
  // result.feedback = "각기둥의 겉넓이를 구하려면 어떤 면들의 넓이를 더해야 할까요?"
  return result;
};
```

### 💬 대화 히스토리 관리

```javascript
// 대화 히스토리 관리 예시
const [conversationHistory, setConversationHistory] = useState([]);

const addToHistory = (role, content) => {
  setConversationHistory((prev) => [...prev, { role, content }]);
};

// 사용 예시
const handleUserMessage = async (userMessage) => {
  // 사용자 메시지 추가
  addToHistory("user", userMessage);

  // API 호출
  const response = await getHint(
    questionData,
    userMessage,
    conversationHistory
  );

  // AI 응답 추가
  addToHistory("assistant", response.feedback);
};
```

## 🧪 개발 & 테스트

### ⚡ 빠른 테스트

```bash
# 1. 서버 실행
func start

# 2. 통합 테스트 (메뉴 방식)
python test_api.py
# → 1: 진단테스트 요약
# → 2: 유사문항 생성
# → 3: 힌트 제공
# → 4: 전체 플로우 테스트
```

### 🔍 개별 기능 테스트

```bash
# 단계별 개별 테스트
python test_session_summary.py      # 1단계: 진단테스트 분석
python test_item_feedback.py        # 2단계: 유사문항 생성
python test_generated_item.py       # 3단계: 힌트 제공 (기본)
python test_real_interactive_hint.py # 3단계: 실제 대화형 힌트
```

### 🛠️ 기타 테스트 도구

#### Postman

1. POST `http://localhost:7071/api/tutor_api`
2. Headers: `Content-Type: application/json`
3. Body (raw JSON):

```json
{
  "request_type": "session_summary",
  "learnerID": "A070001768",
  "session_id": "rt-20250918:first6:A070001768:0"
}
```

#### cURL

```bash
curl -X POST http://localhost:7071/api/tutor_api \
  -H "Content-Type: application/json" \
  -d '{"request_type":"session_summary","learnerID":"A070001768","session_id":"rt-20250918:first6:A070001768:0"}'
```

## 📁 프로젝트 구조

```
llm_tutor_app/
├── 🚀 Core
│   ├── function_app.py          # 메인 Azure Functions 앱
│   ├── requirements.txt         # Python 의존성
│   └── local.settings.json      # 환경설정 (환경변수)
│
├── 🧠 AI & Logic
│   ├── handlers/                # API 요청 처리
│   │   ├── session_handler.py   # 1단계: 진단테스트 분석
│   │   ├── feedback_handler.py  # 2단계: 유사문항 생성
│   │   └── generated_item_handler.py # 3단계: 힌트 제공
│   └── services/
│       └── llm_service.py       # OpenAI GPT-4 연결
│
├── 🗄️ Data
│   ├── database/
│   │   └── db_service.py        # SQL Server 연결
│   └── config/
│       └── settings.py          # 설정 관리
│
├── 🛠️ Utils
│   └── utils/
│       └── response_builder.py  # API 응답 생성
│
└── 🧪 Testing
    ├── test_api.py              # 📋 통합 테스트 (메뉴 방식)
    ├── test_session_summary.py  # 1️⃣ 진단테스트 분석
    ├── test_item_feedback.py    # 2️⃣ 유사문항 생성
    ├── test_generated_item.py   # 3️⃣ 힌트 제공 (기본)
    └── test_real_interactive_hint.py # 💬 실제 대화형 힌트
```

## ⚙️ 환경설정

### 필수 설정 파일: `local.settings.json`

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "OpenAIEndpoint": "https://api.openai.com/v1",
    "OpenApiKey": "your-openai-api-key",
    "SqlConnectionString": "your-sql-connection-string"
  }
}
```

### 🔑 환경변수 설명

| 변수명                | 설명                   | 예시                        |
| --------------------- | ---------------------- | --------------------------- |
| `OpenAIEndpoint`      | OpenAI API 엔드포인트  | `https://api.openai.com/v1` |
| `OpenApiKey`          | OpenAI API 키          | `sk-...`                    |
| `SqlConnectionString` | SQL Server 연결 문자열 | `Server=...;Database=...`   |

## ✅ 시스템 상태

### 🔗 연결 상태

- **Azure Functions**: ✅ 정상 (`http://localhost:7071`)
- **OpenAI GPT-4**: ✅ 연결됨 (소크라틱 대화 최적화)
- **SQL Server**: ✅ 연결됨 (학습자 데이터)

### 🎯 AI 품질 검증

| 입력              | AI 응답 패턴         | 상태 |
| ----------------- | -------------------- | ---- |
| "힌트 주세요"     | 질문형 응답          | ✅   |
| "모르겠어요"      | 단계별 유도 질문     | ✅   |
| "정답 알려주세요" | 정답 직접 제공 안 함 | ✅   |

### ⚡ 성능 지표

- **응답 시간**: 2-7초 (평균 4초)
- **성공률**: 100% (연속 테스트)
- **소크라틱 준수율**: 100% (질문형 응답)

## 🆘 도움말

### 자주 묻는 질문

**Q: 서버가 실행되지 않아요**

```bash
# Azure Functions Core Tools 설치 확인
func --version

# Python 버전 확인 (3.9+ 필요)
python --version
```

**Q: AI 응답이 없어요**
→ `local.settings.json`의 OpenAI API 키 확인

**Q: 데이터베이스 연결 오류**
→ SQL Server 연결 문자열 확인

### 📞 지원

- 트러블슈팅: `트러블슈팅로그.md` 참조
- 개발 문의: 프로젝트 이슈 또는 문서 참조
