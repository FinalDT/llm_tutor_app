# 📋 Swagger/OpenAPI 문서 가이드

LLM Tutor API의 완전한 OpenAPI 3.0 스펙과 활용 가이드입니다.

## 📋 목차

- [빠른 시작](#빠른-시작)
- [Swagger UI 실행](#swagger-ui-실행)
- [TypeScript 타입 생성](#typescript-타입-생성)
- [Mock 서버 설정](#mock-서버-설정)
- [팀 협업 활용](#팀-협업-활용)
- [자동화 및 CI/CD](#자동화-및-cicd)

## 🚀 빠른 시작

### 파일 구조
```
tests/swagger/
├── README.md              # 📖 이 가이드
├── api-spec.yaml          # 📋 OpenAPI 3.0 스펙
├── generate-types.js      # 🔧 TypeScript 자동 생성
└── temp/                  # 🗂️ 임시 생성 파일들 (자동)
```

### 사전 요구사항
```bash
# Node.js 및 npm 설치 필요
node --version  # v16.0.0 이상 권장
npm --version   # v8.0.0 이상 권장
```

## 🌐 Swagger UI 실행

### 방법 1: 글로벌 설치 (권장)
```bash
# swagger-ui-serve 글로벌 설치
npm install -g swagger-ui-serve

# Swagger UI 실행
swagger-ui-serve tests/swagger/api-spec.yaml

# 브라우저에서 확인
# http://localhost:3000
```

### 방법 2: NPX 사용 (일회성)
```bash
# 설치 없이 바로 실행
npx swagger-ui-serve tests/swagger/api-spec.yaml

# 포트 지정 실행
npx swagger-ui-serve -p 8080 tests/swagger/api-spec.yaml
```

### 방법 3: Docker 사용
```bash
# Docker로 Swagger UI 실행
docker run -p 8080:8080 \
  -v $(pwd)/tests/swagger:/tmp \
  -e SWAGGER_JSON=/tmp/api-spec.yaml \
  swaggerapi/swagger-ui
```

### 방법 4: VS Code 확장
```bash
# VS Code에서 OpenAPI 미리보기
# 확장: "OpenAPI (Swagger) Editor" 설치
# Ctrl+Shift+P → "OpenAPI: Preview"
```

## 🔧 TypeScript 타입 생성

### 자동 생성 스크립트 실행
```bash
# 타입 자동 생성 (모든 의존성 자동 설치)
node tests/swagger/generate-types.js

# 생성된 파일 확인
ls tests/frontend/types/generated/
# ├── api.generated.ts      # 자동 생성된 타입
# └── usage-example.ts      # 사용 예제
```

### 수동 설치 및 실행
```bash
# OpenAPI Generator 설치
npm install -g @openapitools/openapi-generator-cli

# TypeScript 타입 생성
openapi-generator-cli generate \
  -i tests/swagger/api-spec.yaml \
  -g typescript-fetch \
  -o ./generated \
  --additional-properties=typescriptThreePlus=true,supportsES6=true
```

### 생성된 타입 사용법
```typescript
// 자동 생성된 타입 import
import {
  SessionSummaryRequest,
  TutorAPIResponse,
  ConversationMessage
} from './types/generated/api.generated';

// 타입 안전한 API 호출
const request: SessionSummaryRequest = {
  request_type: 'session_summary',
  learnerID: 'A070001768',
  session_id: 'rt-20250918:first6:A070001768:0'
};

const response: TutorAPIResponse = await callAPI(request);
```

## 🎭 Mock 서버 설정

### Prism을 사용한 Mock 서버
```bash
# Prism 설치
npm install -g @stoplight/prism-cli

# Mock 서버 실행
prism mock tests/swagger/api-spec.yaml

# 포트 지정 실행
prism mock -p 4010 tests/swagger/api-spec.yaml

# 다이나믹 응답 활성화
prism mock --dynamic tests/swagger/api-spec.yaml
```

### Mock 서버 활용법
```typescript
// Mock 서버 URL로 API 클라이언트 설정
const mockClient = new TutorAPIClient({
  baseURL: 'http://localhost:4010'  // Mock 서버
});

// 실제 응답 구조로 프론트엔드 개발 가능
const response = await mockClient.getSessionSummary('test', 'test');
console.log(response.data.feedback);  // Mock 데이터 응답
```

### JSON Server를 이용한 간단한 Mock
```bash
# json-server 설치
npm install -g json-server

# Mock 데이터 생성 (한국어 예제)
cat > mock-data.json << 'EOF'
{
  "tutor_api": {
    "feedback": "진단 테스트 푸느라 수고 많았어! 결과를 알려줄게...",
    "conversation_history": [
      {"role": "user", "content": "피드백 요청"},
      {"role": "assistant", "content": "진단 결과..."}
    ]
  }
}
EOF

# Mock 서버 실행
json-server --watch mock-data.json --port 3001
```

## 👥 팀 협업 활용

### 프론트엔드 개발자용
```bash
# 1. API 스펙 확인
swagger-ui-serve tests/swagger/api-spec.yaml

# 2. TypeScript 타입 생성
node tests/swagger/generate-types.js

# 3. Mock 서버로 개발
prism mock tests/swagger/api-spec.yaml

# 4. 실제 API 연동 테스트
npm run test:api
```

### 백엔드 개발자용
```bash
# 1. 스펙 검증
swagger-codegen validate -i tests/swagger/api-spec.yaml

# 2. API 구현 후 스펙 동기화 확인
# (실제 응답과 스펙이 일치하는지 확인)

# 3. 문서 업데이트
swagger-ui-serve tests/swagger/api-spec.yaml
```

### 디자이너용
```bash
# 1. API 응답 구조 확인
swagger-ui-serve tests/swagger/api-spec.yaml

# 2. 실제 응답 데이터 예제 확인
# "Examples" 섹션에서 실제 한국어 응답 확인

# 3. 상태별 UI 디자인 가이드
# - 로딩 상태 (isLoading: true)
# - 에러 상태 (4xx, 5xx 응답)
# - 성공 상태 (200 응답)
```

## 🔄 자동화 및 CI/CD

### Package.json 스크립트 설정
```json
{
  "scripts": {
    "docs:serve": "swagger-ui-serve tests/swagger/api-spec.yaml",
    "docs:generate": "node tests/swagger/generate-types.js",
    "docs:validate": "swagger-codegen validate -i tests/swagger/api-spec.yaml",
    "mock:server": "prism mock tests/swagger/api-spec.yaml",
    "mock:test": "prism mock --dynamic tests/swagger/api-spec.yaml"
  },
  "devDependencies": {
    "@openapitools/openapi-generator-cli": "^2.7.0",
    "@stoplight/prism-cli": "^5.5.0",
    "swagger-ui-serve": "^3.0.0"
  }
}
```

### GitHub Actions 워크플로우 예제
```yaml
# .github/workflows/api-docs.yml
name: API Documentation

on:
  push:
    paths:
      - 'tests/swagger/**'
  pull_request:
    paths:
      - 'tests/swagger/**'

jobs:
  validate-api-spec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Validate OpenAPI Spec
        run: |
          npm install -g @openapitools/openapi-generator-cli
          openapi-generator-cli validate -i tests/swagger/api-spec.yaml

      - name: Generate TypeScript Types
        run: |
          node tests/swagger/generate-types.js

      - name: Deploy Swagger UI
        if: github.ref == 'refs/heads/main'
        run: |
          # GitHub Pages 배포 로직
          echo "API 문서 배포..."
```

### 스펙 변경 감지 및 알림
```bash
# API 스펙 변경 감지 스크립트
#!/bin/bash

# 이전 스펙과 현재 스펙 비교
diff_output=$(git diff HEAD~1 tests/swagger/api-spec.yaml)

if [ ! -z "$diff_output" ]; then
  echo "🚨 API 스펙 변경 감지!"
  echo "변경 내용:"
  echo "$diff_output"

  # Slack/Discord 알림 (선택적)
  # curl -X POST -H 'Content-type: application/json' \
  #   --data '{"text":"API 스펙이 변경되었습니다."}' \
  #   $SLACK_WEBHOOK_URL
fi
```

## 📊 고급 활용법

### API 스펙 분할 관리
```yaml
# api-spec.yaml (메인)
openapi: 3.0.3
info:
  title: LLM Tutor API
  version: 1.0.0

paths:
  $ref: './paths/index.yaml'

components:
  schemas:
    $ref: './schemas/index.yaml'
```

### 스펙 버전 관리
```bash
# 버전별 스펙 관리
tests/swagger/
├── v1.0/
│   └── api-spec.yaml      # 안정 버전
├── v1.1/
│   └── api-spec.yaml      # 개발 버전
└── latest/
    └── api-spec.yaml      # 최신 버전 (심볼릭 링크)
```

### 멀티 환경 스펙
```yaml
# 환경별 서버 설정
servers:
  - url: http://localhost:7071/api
    description: 로컬 개발
  - url: https://dev-api.example.com/api
    description: 개발 환경
  - url: https://staging-api.example.com/api
    description: 스테이징 환경
  - url: https://api.example.com/api
    description: 운영 환경
```

## 🔍 문제 해결

### 자주 발생하는 문제들

#### 1. OpenAPI Generator 설치 오류
```bash
# 권한 문제 시
sudo npm install -g @openapitools/openapi-generator-cli

# 또는 npx 사용
npx @openapitools/openapi-generator-cli generate \
  -i tests/swagger/api-spec.yaml \
  -g typescript-fetch \
  -o ./temp
```

#### 2. Swagger UI 포트 충돌
```bash
# 다른 포트 사용
swagger-ui-serve -p 8080 tests/swagger/api-spec.yaml

# 사용 중인 포트 확인
netstat -tulpn | grep :3000
```

#### 3. Mock 서버 응답 커스터마이징
```bash
# Prism 예제 응답 사용
prism mock --dynamic tests/swagger/api-spec.yaml

# 특정 응답 강제 지정
curl -H "Prefer: example=session_summary_response" \
  http://localhost:4010/tutor_api
```

#### 4. TypeScript 컴파일 오류
```typescript
// 생성된 타입이 기존 타입과 충돌하는 경우
// 네임스페이스 사용
namespace Generated {
  export interface TutorAPIResponse {
    // 자동 생성된 타입
  }
}

// 또는 별칭 사용
import {
  TutorAPIResponse as GeneratedTutorAPIResponse
} from './generated/api.generated';
```

## 📚 참고 자료

- [OpenAPI 3.0 공식 문서](https://swagger.io/specification/)
- [Swagger UI 가이드](https://swagger.io/tools/swagger-ui/)
- [Prism Mock 서버 가이드](https://stoplight.io/open-source/prism)
- [OpenAPI Generator 문서](https://openapi-generator.tech/)

## 🆘 지원

- **스펙 문법 오류**: [OpenAPI Validator](https://apitools.dev/swagger-parser/online/) 사용
- **타입 생성 문제**: `generate-types.js` 스크립트 로그 확인
- **Mock 서버 이슈**: Prism 로그 레벨 조정 (`--verbosity debug`)

---

📝 **문서 버전**: v1.0.0
🕒 **마지막 업데이트**: 2024년 12월
👥 **작성자**: LLM Tutor Development Team