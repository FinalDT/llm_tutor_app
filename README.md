# LLM 튜터 앱

## 📋 프로젝트 개요
LLM 기반 개인화 학습 튜터 시스템으로, 진단테스트 분석 → 유사문항 추천 → 힌트 제공의 3단계 학습 플로우를 제공합니다.

## 🏗️ 아키텍처
- **Backend**: Azure Functions (Python)
- **LLM**: OpenAI GPT-4
- **Database**: SQL Server
- **API**: RESTful HTTP API

## 🚀 로컬 개발 환경 설정

### 1. 사전 요구사항
- Python 3.9+
- Azure Functions Core Tools
- Azure Storage Emulator (Azurite)

### 2. 설치 및 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# Azure Functions 로컬 실행
func start
```

### 3. API 엔드포인트
- **로컬 URL**: `http://localhost:7071/api/tutor_api`
- **인증**: FUNCTION 레벨

## 📊 API 기능

### 1단계: 진단테스트 요약
학습자의 진단테스트 결과를 분석하여 틀린 문제와 약한 개념을 파악합니다.

**요청 형식:**
```json
{
  "request_type": "session_summary",
  "learnerID": "A070001768",
  "session_id": "rt-20250918:first6:A070001768:0"
}
```

**응답 예시:**
```json
{
  "feedback": "진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.\n\n전체 6 문제 중에서 2 문제를 맞혔네. 정말 잘했어! 👍\n\n이번 테스트에서는 아쉽게도 1, 2, 4, 5 번 문제를 틀렸더라. 데이터를 분석해보니, 주로 \"부채꼴의 호의 길이와 넓이 사이의 관계, 다각형의 내각의 크기의 합, 원뿔의 겉넓이, 각기둥의 겉넓이\" 개념들이 조금 헷갈리는 것 같아.\n\n우리 같이 \"부채꼴의 호의 길이와 넓이 사이의 관계\"에 대한 학습을 시작해볼까?"
}
```

### 2단계: 유사문항 생성
틀린 문제의 개념을 기반으로 학생 수준에 맞는 유사문항을 생성합니다.

**요청 형식:**
```json
{
  "request_type": "item_feedback",
  "learnerID": "A070001768",
  "session_id": "rt-20250918:first6:A070001768:0",
  "message": "1번문제 유사 문항 주세요",
  "conversation_history": [
    {
      "role": "user",
      "content": "피드백 요청"
    },
    {
      "role": "assistant",
      "content": "진단 테스트 결과..."
    }
  ]
}
```

**응답 예시:**
```json
{
  "feedback": "좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까? 아래 문제를 풀어봐.\n\n높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요. 정사각형의 한 변의 길이는 4cm입니다.",
  "generated_question_data": {
    "new_question_text": "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요. 정사각형의 한 변의 길이는 4cm입니다.",
    "correct_answer": "72 cm²",
    "explanation": "각기둥의 겉넓이는 밑면의 넓이와 옆면의 넓이를 모두 더하여 구합니다..."
  }
}
```

### 3단계: 힌트 제공
생성된 문항에 대해 소크라틱 방식의 힌트를 제공합니다.

**요청 형식:**
```json
{
  "request_type": "generated_item",
  "generated_question_data": {
    "new_question_text": "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요...",
    "correct_answer": "72 cm²",
    "explanation": "각기둥의 겉넓이는..."
  },
  "message": "모르겠어요",
  "conversation_history": [...]
}
```

**응답 예시:**
```json
{
  "feedback": "각기둥의 겉넓이를 구하려면 어떤 면들의 넓이를 더해야 할까요?"
}
```

## 🧪 테스트 방법

### 🚀 자동화된 테스트 스크립트 (권장)

#### 통합 테스트 (메뉴 선택 방식)
```bash
python test_api.py
```
- 1: 진단테스트 요약
- 2: 유사문항 생성  
- 3: 힌트 제공
- 4: 모든 기능 테스트
- 0: 종료

#### 개별 기능 테스트
```bash
# 1단계: 진단테스트 요약
python test_session_summary.py

# 2단계: 유사문항 생성
python test_item_feedback.py

# 3단계: 기본 힌트 제공
python test_generated_item.py

# 3단계: 실제 사용환경 대화형 힌트 (NEW!)
python test_real_interactive_hint.py
```

### 📮 Postman 사용법
1. **새 Request 생성**: POST 방식으로 설정
2. **URL 입력**: `http://localhost:7071/api/tutor_api`
3. **Headers 설정**: `Content-Type: application/json`
4. **Body 설정**: Raw → JSON 형식으로 요청 데이터 입력

### 💻 PowerShell 사용법
```powershell
# 1단계 테스트
$body = @{
    request_type = "session_summary"
    learnerID = "A070001768"
    session_id = "rt-20250918:first6:A070001768:0"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7071/api/tutor_api" -Method Post -Body $body -ContentType "application/json"
```

## 📁 프로젝트 구조
```
llm_tutor_app/
├── function_app.py          # 메인 Azure Functions 앱
├── config/
│   └── settings.py          # 환경설정 관리
├── database/
│   └── db_service.py        # 데이터베이스 서비스
├── handlers/
│   ├── session_handler.py   # 세션 요약 처리
│   ├── feedback_handler.py  # 문항 피드백 처리
│   └── generated_item_handler.py # 생성 문항 처리
├── services/
│   └── llm_service.py       # LLM 서비스
├── utils/
│   └── response_builder.py  # 응답 생성 유틸리티
├── test_api.py              # 통합 테스트 스크립트
├── test_session_summary.py  # 진단테스트 요약 테스트
├── test_item_feedback.py    # 유사문항 생성 테스트
├── test_generated_item.py      # 기본 힌트 제공 테스트
├── test_interactive_hint.py    # 대화형 힌트 시스템 테스트 (하드코딩)
└── test_real_interactive_hint.py # 실제 사용환경 대화형 힌트 테스트
```

## 🔧 환경설정
`local.settings.json`에서 다음 환경변수를 설정하세요:
- `OpenAIEndpoint`: OpenAI 엔드포인트
- `OpenApiKey`: OpenAI API 키
- `SqlConnectionString`: SQL Server 연결 문자열

## ✅ AI 연결 상태 및 테스트 결과

### 🔍 **AI 연결 테스트 완료**
- **Azure Functions 서버**: ✅ 정상 실행 중 (`http://localhost:7071`)
- **AI 연결**: ✅ 완벽하게 연결됨
- **응답 품질**: ✅ 소크라틱 질문 형태로 응답
- **안정성**: ✅ 연속 요청 모두 성공

### 🤖 **AI 응답 품질 검증**
모든 AI 응답이 완벽한 소크라틱 방식으로 구현됨:

| 사용자 입력 | AI 응답 | 소크라틱 검증 |
|-------------|---------|---------------|
| "힌트 주세요" | "각기둥의 겉넓이를 구할 때, 어떤 면들이 포함되어야 할까요?" | ✅ 질문 형태 |
| "모르겠어요" | "각기둥의 겉넓이를 구하기 위해서, 어떤 부분들의 넓이를 합쳐야 할까요?" | ✅ 질문 형태 |
| "어떻게 풀어요?" | "각기둥의 겉넓이를 구하기 위해 어떤 부분의 넓이를 먼저 계산해야 할까요?" | ✅ 질문 형태 |

### 🎯 **핵심 기능 검증**
- ✅ **정답 직접 공개 없음**: "정답은", "답은" 등 키워드 사용 안 함
- ✅ **소크라틱 질문**: 모든 응답이 "?"로 끝나는 질문 형태
- ✅ **응답 시간**: 평균 2-7초로 빠른 응답
- ✅ **연결 안정성**: 여러 번 연속 요청 모두 성공

### 🚀 **실제 사용환경 테스트**
```bash
# AI 연결 상태 확인
python test_ai_connection.py

# 실제 대화형 힌트 테스트
python test_real_interactive_hint.py
```

## 📝 로그
문제 해결 과정은 `트러블슈팅로그.md` 파일에 기록됩니다.