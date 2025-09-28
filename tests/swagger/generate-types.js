#!/usr/bin/env node

/**
 * TypeScript 타입 자동 생성 스크립트
 * OpenAPI 스펙에서 TypeScript 인터페이스를 자동 생성합니다.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 설정
const CONFIG = {
  specFile: path.join(__dirname, 'api-spec.yaml'),
  outputDir: path.join(__dirname, '../frontend/types/generated'),
  generatedFile: 'api.generated.ts',
  tempDir: path.join(__dirname, 'temp')
};

// 색상 출력을 위한 유틸리티
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkDependencies() {
  log('📦 의존성 확인 중...', 'blue');

  const requiredCommands = [
    { cmd: 'npm', desc: 'Node.js 패키지 매니저' },
    { cmd: 'npx', desc: 'NPX 실행 도구' }
  ];

  for (const { cmd, desc } of requiredCommands) {
    try {
      execSync(`${cmd} --version`, { stdio: 'ignore' });
      log(`✅ ${desc} 설치됨`, 'green');
    } catch (error) {
      log(`❌ ${desc} 설치 필요: ${cmd}`, 'red');
      process.exit(1);
    }
  }
}

function installOpenAPIGenerator() {
  log('🔧 OpenAPI Generator 설치 확인 중...', 'blue');

  try {
    execSync('npx @openapitools/openapi-generator-cli version', { stdio: 'ignore' });
    log('✅ OpenAPI Generator 설치됨', 'green');
  } catch (error) {
    log('📥 OpenAPI Generator 설치 중...', 'yellow');
    try {
      execSync('npm install -g @openapitools/openapi-generator-cli', { stdio: 'inherit' });
      log('✅ OpenAPI Generator 설치 완료', 'green');
    } catch (installError) {
      log('❌ OpenAPI Generator 설치 실패', 'red');
      log('수동 설치: npm install -g @openapitools/openapi-generator-cli', 'yellow');
      process.exit(1);
    }
  }
}

function createDirectories() {
  log('📁 디렉토리 생성 중...', 'blue');

  [CONFIG.outputDir, CONFIG.tempDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      log(`✅ 디렉토리 생성: ${dir}`, 'green');
    }
  });
}

function generateTypes() {
  log('🔄 TypeScript 타입 생성 중...', 'blue');

  const command = [
    'npx @openapitools/openapi-generator-cli generate',
    `-i "${CONFIG.specFile}"`,
    '-g typescript-fetch',
    `-o "${CONFIG.tempDir}"`,
    '--additional-properties=',
    'typescriptThreePlus=true,',
    'supportsES6=true,',
    'npmName=llm-tutor-api,',
    'npmVersion=1.0.0'
  ].join(' ');

  try {
    execSync(command, { stdio: 'inherit' });
    log('✅ 타입 생성 완료', 'green');
  } catch (error) {
    log('❌ 타입 생성 실패', 'red');
    throw error;
  }
}

function processGeneratedTypes() {
  log('⚙️ 생성된 타입 후처리 중...', 'blue');

  const apiFile = path.join(CONFIG.tempDir, 'src', 'apis', 'TutoringApi.ts');
  const modelsFile = path.join(CONFIG.tempDir, 'src', 'models', 'index.ts');
  const outputFile = path.join(CONFIG.outputDir, CONFIG.generatedFile);

  if (!fs.existsSync(apiFile) || !fs.existsSync(modelsFile)) {
    log('❌ 생성된 파일을 찾을 수 없습니다', 'red');
    return;
  }

  // 생성된 파일들을 읽어서 하나로 합치기
  let combinedContent = `/**
 * 자동 생성된 TypeScript 타입 정의
 * OpenAPI 스펙: ${CONFIG.specFile}
 * 생성 시간: ${new Date().toISOString()}
 *
 * ⚠️ 주의: 이 파일은 자동 생성됩니다. 직접 수정하지 마세요.
 * 변경이 필요한 경우 OpenAPI 스펙 파일을 수정하고 다시 생성하세요.
 */

`;

  // 모델 타입들 추가
  const modelsContent = fs.readFileSync(modelsFile, 'utf8');
  combinedContent += modelsContent;

  // API 클래스 추가 (선택적)
  const apiContent = fs.readFileSync(apiFile, 'utf8');
  combinedContent += '\n\n// API 클래스 (선택적 사용)\n';
  combinedContent += apiContent;

  // 우리 프로젝트에 맞게 조정
  combinedContent = combinedContent
    .replace(/from '\.\.\/models'/g, "from './api.generated'")
    .replace(/from '\.\.\/runtime'/g, "// Runtime imports (구현 필요)")
    .replace(/export \* from '\.\/models';/g, '');

  fs.writeFileSync(outputFile, combinedContent);
  log(`✅ 타입 파일 생성: ${outputFile}`, 'green');
}

function createUsageExample() {
  log('📝 사용 예제 생성 중...', 'blue');

  const exampleFile = path.join(CONFIG.outputDir, 'usage-example.ts');
  const exampleContent = `/**
 * 자동 생성된 타입 사용 예제
 */

import {
  SessionSummaryRequest,
  ItemFeedbackRequest,
  GeneratedItemRequest,
  TutorAPIResponse,
  ConversationMessage,
  GeneratedQuestion
} from './api.generated';

// 1단계: 진단테스트 요약 요청 예제
const sessionSummaryExample: SessionSummaryRequest = {
  request_type: 'session_summary',
  learnerID: 'A070001768',
  session_id: 'rt-20250918:first6:A070001768:0',
  conversation_history: []
};

// 2단계: 유사문항 생성 요청 예제
const itemFeedbackExample: ItemFeedbackRequest = {
  request_type: 'item_feedback',
  learnerID: 'A070001768',
  session_id: 'rt-20250918:first6:A070001768:0',
  message: '1번문제 유사 문항 주세요',
  conversation_history: [
    {
      role: 'user',
      content: '피드백 요청'
    }
  ]
};

// 3단계: 힌트 제공 요청 예제
const generatedItemExample: GeneratedItemRequest = {
  request_type: 'generated_item',
  generated_question_data: {
    new_question_text: '높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요.',
    correct_answer: '72 cm²',
    explanation: '각기둥의 겉넓이는...'
  },
  message: '모르겠어요',
  conversation_history: [],
  learnerID: 'A070001768',
  original_concept: '각기둥의 겉넓이'
};

// API 응답 타입 가드 함수
export function isTutorAPIResponse(response: any): response is TutorAPIResponse {
  return (
    typeof response === 'object' &&
    typeof response.feedback === 'string' &&
    Array.isArray(response.conversation_history)
  );
}

// 대화 메시지 생성 헬퍼
export function createMessage(role: 'user' | 'assistant' | 'system', content: string): ConversationMessage {
  return { role, content };
}

// 타입 안전한 API 호출 예제
export async function callTutorAPI(request: SessionSummaryRequest | ItemFeedbackRequest | GeneratedItemRequest): Promise<TutorAPIResponse> {
  const response = await fetch('/api/tutor_api', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    throw new Error(\`API 호출 실패: \${response.status}\`);
  }

  const data = await response.json();

  if (!isTutorAPIResponse(data)) {
    throw new Error('잘못된 API 응답 형식');
  }

  return data;
}
`;

  fs.writeFileSync(exampleFile, exampleContent);
  log(`✅ 사용 예제 생성: ${exampleFile}`, 'green');
}

function cleanup() {
  log('🧹 임시 파일 정리 중...', 'blue');

  if (fs.existsSync(CONFIG.tempDir)) {
    fs.rmSync(CONFIG.tempDir, { recursive: true, force: true });
    log('✅ 임시 파일 정리 완료', 'green');
  }
}

function createPackageScript() {
  log('📜 package.json 스크립트 생성 가이드', 'blue');

  const packageScripts = `
다음 스크립트를 package.json에 추가하세요:

{
  "scripts": {
    "generate-types": "node tests/swagger/generate-types.js",
    "swagger-ui": "swagger-ui-serve tests/swagger/api-spec.yaml",
    "api-docs": "npm run swagger-ui"
  },
  "devDependencies": {
    "@openapitools/openapi-generator-cli": "^2.7.0",
    "swagger-ui-serve": "^3.0.0"
  }
}
`;

  log(packageScripts, 'cyan');
}

function main() {
  log('🚀 TypeScript 타입 자동 생성 시작', 'bright');

  try {
    checkDependencies();
    installOpenAPIGenerator();
    createDirectories();
    generateTypes();
    processGeneratedTypes();
    createUsageExample();
    cleanup();
    createPackageScript();

    log('🎉 TypeScript 타입 생성 완료!', 'green');
    log(`📁 출력 디렉토리: ${CONFIG.outputDir}`, 'blue');
    log(`📄 메인 파일: ${CONFIG.generatedFile}`, 'blue');
    log(`📄 예제 파일: usage-example.ts`, 'blue');

  } catch (error) {
    log('❌ 타입 생성 실패', 'red');
    log(error.message, 'red');

    cleanup();
    process.exit(1);
  }
}

// 직접 실행 시
if (require.main === module) {
  main();
}

module.exports = { main, CONFIG };
`;

  fs.writeFileSync(exampleFile, exampleContent);
  log(`✅ 사용 예제 생성: ${exampleFile}`, 'green');
}

function cleanup() {
  log('🧹 임시 파일 정리 중...', 'blue');

  if (fs.existsSync(CONFIG.tempDir)) {
    fs.rmSync(CONFIG.tempDir, { recursive: true, force: true });
    log('✅ 임시 파일 정리 완료', 'green');
  }
}

function createPackageScript() {
  log('📜 package.json 스크립트 생성 가이드', 'blue');

  const packageScripts = `
다음 스크립트를 package.json에 추가하세요:

{
  "scripts": {
    "generate-types": "node tests/swagger/generate-types.js",
    "swagger-ui": "swagger-ui-serve tests/swagger/api-spec.yaml",
    "api-docs": "npm run swagger-ui"
  },
  "devDependencies": {
    "@openapitools/openapi-generator-cli": "^2.7.0",
    "swagger-ui-serve": "^3.0.0"
  }
}
`;

  log(packageScripts, 'cyan');
}

function main() {
  log('🚀 TypeScript 타입 자동 생성 시작', 'bright');

  try {
    checkDependencies();
    installOpenAPIGenerator();
    createDirectories();
    generateTypes();
    processGeneratedTypes();
    createUsageExample();
    cleanup();
    createPackageScript();

    log('🎉 TypeScript 타입 생성 완료!', 'green');
    log(`📁 출력 디렉토리: ${CONFIG.outputDir}`, 'blue');
    log(`📄 메인 파일: ${CONFIG.generatedFile}`, 'blue');
    log(`📄 예제 파일: usage-example.ts`, 'blue');

  } catch (error) {
    log('❌ 타입 생성 실패', 'red');
    log(error.message, 'red');

    cleanup();
    process.exit(1);
  }
}

// 직접 실행 시
if (require.main === module) {
  main();
}

module.exports = { main, CONFIG };