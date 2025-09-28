# 🎨 LLM Tutor UI/UX 디자인 가이드라인

프론트엔드 개발자와 UI/UX 디자이너를 위한 완전한 디자인 시스템 가이드입니다.

## 📋 목차

- [디자인 원칙](#디자인-원칙)
- [출력값 예시 및 패턴](#출력값-예시-및-패턴)
- [대화형 인터페이스](#대화형-인터페이스)
- [상태별 UI 패턴](#상태별-ui-패턴)
- [색상 시스템](#색상-시스템)
- [타이포그래피](#타이포그래피)
- [컴포넌트 라이브러리](#컴포넌트-라이브러리)
- [반응형 디자인](#반응형-디자인)
- [접근성 가이드라인](#접근성-가이드라인)

## 🎯 디자인 원칙

### 1. 교육적 중심 (Educational-First)
- **학습 효과 우선**: 모든 UI 요소는 학습 목표 달성을 지원
- **인지 부하 최소화**: 복잡한 인터페이스보다 직관적이고 단순한 설계
- **피드백 즉시성**: 사용자 행동에 대한 빠르고 명확한 피드백

### 2. 대화형 자연스러움 (Conversational)
- **인간적 상호작용**: 기계적이지 않은 따뜻하고 친근한 톤
- **맥락적 응답**: 이전 대화를 고려한 연속적인 상호작용
- **소크라틱 방식**: 답을 직접 주지 않고 질문으로 유도하는 UI 패턴

### 3. 개인화 (Personalized)
- **적응적 인터페이스**: 학습자 수준에 따른 UI 조정
- **진행상황 시각화**: 개인별 학습 진도 및 성취도 표시
- **맞춤형 피드백**: 개인의 학습 패턴을 반영한 UI 요소

### 4. 접근성 우선 (Accessibility-First)
- **모든 사용자 포용**: 장애가 있는 사용자도 동등한 학습 기회
- **다양한 입력 방식**: 마우스, 키보드, 터치, 음성 지원
- **국제화 대응**: 다국어 및 다양한 문화적 맥락 고려

## 📊 출력값 예시 및 패턴

### AI 응답 타입별 UI 패턴

#### 1단계: 진단테스트 분석 응답
```
💬 AI 응답 예시:
"진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.

전체 6 문제 중에서 2 문제를 맞혔네. 정말 잘했어! 👍

이번 테스트에서는 아쉽게도 1, 2, 4, 5 번 문제를 틀렸더라.
데이터를 분석해보니, 주로 "부채꼴의 호의 길이와 넓이 사이의 관계,
다각형의 내각의 크기의 합, 원뿔의 겉넓이, 각기둥의 겉넓이"
개념들이 조금 헷갈리는 것 같아.

우리 같이 "부채꼴의 호의 길이와 넓이 사이의 관계"에 대한
학습을 시작해볼까?"
```

**UI 디자인 요구사항:**
- 📊 **통계 강조**: 숫자 데이터는 시각적으로 두드러지게 표시
- 🎨 **감정 표현**: 이모지와 격려 메시지를 자연스럽게 통합
- 🔗 **개념 링크**: 개념명은 클릭 가능한 요소로 디자인
- 📈 **진행 바**: 전체 학습 단계 중 현재 위치 표시

#### 2단계: 유사문항 생성 응답
```
💬 AI 응답 예시:
"좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까? 아래 문제를 풀어봐.

높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요.
정사각형의 한 변의 길이는 4cm입니다."

📝 문제 데이터:
- 문제: "높이가 5cm, 밑면이 정사각형인..."
- 정답: "72 cm²"
- 해설: "각기둥의 겉넓이는 밑면의 넓이와..."
```

**UI 디자인 요구사항:**
- 📝 **문제 카드**: 생성된 문제는 별도 카드 형태로 분리
- 🎯 **상호작용 유도**: "풀어보기" 버튼 등 명확한 행동 유도
- 📚 **참고 자료**: 해설은 접었다 펼 수 있는 형태
- 🔄 **재생성 옵션**: "다른 문제 생성" 기능 제공

#### 3단계: 소크라틱 힌트 응답
```
💬 AI 응답 예시들:
"각기둥의 겉넓이를 구하려면 어떤 면들의 넓이를 더해야 할까요?"
"정사각형 밑면이 몇 개 있는지 생각해보세요."
"옆면은 어떤 도형일까요?"
"각각의 면의 넓이를 구해서 더해보세요."
```

**UI 디자인 요구사항:**
- ❓ **질문 강조**: 질문 형태임을 시각적으로 명확히 표시
- 💡 **힌트 아이콘**: 전구, 물음표 등 힌트임을 나타내는 시각 요소
- 🎭 **감정 표현**: AI의 격려하는 톤을 UI로 표현
- 🔗 **단계별 연결**: 이전 힌트와의 연관성 표시

### 에러 상태 응답 패턴

#### 네트워크 오류
```
💬 시스템 메시지:
"연결에 문제가 발생했습니다. 인터넷 연결을 확인해주세요."
```

#### 서버 오류
```
💬 시스템 메시지:
"일시적인 서버 문제입니다. 잠시 후 다시 시도해주세요."
```

#### 타임아웃 오류
```
💬 시스템 메시지:
"AI가 응답을 준비하는데 시간이 걸리고 있어요. 다시 시도해주세요."
```

## 💬 대화형 인터페이스 디자인

### 채팅 버블 시스템

#### 사용자 메시지 (우측 정렬)
```css
/* 사용자 버블 스타일 */
.user-message {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 16px;
  max-width: 70%;
  margin-left: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

#### AI 메시지 (좌측 정렬)
```css
/* AI 버블 스타일 */
.ai-message {
  background: #ffffff;
  color: #374151;
  border: 1px solid #e5e7eb;
  border-radius: 18px 18px 18px 4px;
  padding: 16px 20px;
  max-width: 80%;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  position: relative;
}

.ai-message::before {
  content: "🤖";
  position: absolute;
  left: -40px;
  top: 0;
  width: 32px;
  height: 32px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}
```

### 타이핑 인디케이터
```css
.typing-indicator {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: 18px;
  margin: 8px 0;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9ca3af;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
```

### 입력 영역 디자인
```css
.input-area {
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 16px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 22px;
  resize: none;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.5;
  transition: border-color 0.2s ease;
}

.message-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.send-button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.send-button:hover:not(:disabled) {
  background: #2563eb;
  transform: scale(1.05);
}

.send-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
}
```

## 🎨 상태별 UI 패턴

### 로딩 상태

#### 1. AI 응답 준비 중
```jsx
<div className="ai-thinking">
  <div className="thinking-avatar">🤖</div>
  <div className="thinking-message">
    <div className="thinking-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
    <p>AI가 답변을 생각하고 있어요...</p>
  </div>
</div>
```

#### 2. 문제 생성 중
```jsx
<div className="generating-problem">
  <div className="generation-icon">✨</div>
  <div className="generation-text">
    <h4>새로운 문제를 만들고 있어요</h4>
    <p>잠시만 기다려주세요...</p>
  </div>
  <div className="progress-bar">
    <div className="progress-fill"></div>
  </div>
</div>
```

### 성공 상태

#### 1. 문제 해결 완료
```jsx
<div className="success-celebration">
  <div className="success-icon">🎉</div>
  <h3>정답이에요!</h3>
  <p>훌륭해요! 다음 문제로 넘어갈까요?</p>
  <div className="success-actions">
    <button className="next-problem">다음 문제</button>
    <button className="similar-problem">비슷한 문제</button>
  </div>
</div>
```

#### 2. 세션 완료
```jsx
<div className="session-complete">
  <div className="completion-badge">🏆</div>
  <h2>학습 세션 완료!</h2>
  <div className="session-stats">
    <div className="stat">
      <span className="stat-number">5</span>
      <span className="stat-label">문제 해결</span>
    </div>
    <div className="stat">
      <span className="stat-number">25</span>
      <span className="stat-label">분 학습</span>
    </div>
  </div>
</div>
```

### 에러 상태

#### 1. 연결 오류
```jsx
<div className="error-state network-error">
  <div className="error-icon">📡</div>
  <h3>연결 문제가 발생했어요</h3>
  <p>인터넷 연결을 확인하고 다시 시도해주세요.</p>
  <button className="retry-button" onClick={handleRetry}>
    다시 시도
  </button>
</div>
```

#### 2. 서버 오류
```jsx
<div className="error-state server-error">
  <div className="error-icon">🔧</div>
  <h3>일시적인 문제가 발생했어요</h3>
  <p>서버에 문제가 있어요. 잠시 후 다시 시도해주세요.</p>
  <div className="error-actions">
    <button className="retry-button">다시 시도</button>
    <button className="support-button">문의하기</button>
  </div>
</div>
```

## 🌈 색상 시스템

### 주 색상 (Primary Colors)
```css
:root {
  /* 브랜드 색상 */
  --color-primary: #3b82f6;        /* 파란색 - 신뢰감, 학습 */
  --color-primary-light: #60a5fa;  /* 밝은 파란색 */
  --color-primary-dark: #1d4ed8;   /* 어두운 파란색 */

  /* 보조 색상 */
  --color-secondary: #10b981;      /* 초록색 - 성공, 진행 */
  --color-accent: #f59e0b;         /* 주황색 - 주의, 강조 */
}
```

### 의미별 색상 (Semantic Colors)
```css
:root {
  /* 상태 색상 */
  --color-success: #10b981;        /* 성공 - 초록 */
  --color-warning: #f59e0b;        /* 경고 - 주황 */
  --color-error: #ef4444;          /* 오류 - 빨강 */
  --color-info: #3b82f6;           /* 정보 - 파랑 */

  /* 교육 전용 색상 */
  --color-hint: #8b5cf6;           /* 힌트 - 보라 */
  --color-question: #06b6d4;       /* 질문 - 청록 */
  --color-answer: #10b981;         /* 정답 - 초록 */
  --color-thinking: #6b7280;       /* 사고 중 - 회색 */
}
```

### 중성 색상 (Neutral Colors)
```css
:root {
  /* 텍스트 색상 */
  --color-text-primary: #111827;   /* 주 텍스트 */
  --color-text-secondary: #6b7280; /* 보조 텍스트 */
  --color-text-muted: #9ca3af;     /* 흐린 텍스트 */

  /* 배경 색상 */
  --color-bg-primary: #ffffff;     /* 주 배경 */
  --color-bg-secondary: #f9fafb;   /* 보조 배경 */
  --color-bg-muted: #f3f4f6;       /* 흐린 배경 */

  /* 경계선 색상 */
  --color-border: #e5e7eb;         /* 기본 경계선 */
  --color-border-light: #f3f4f6;   /* 밝은 경계선 */
  --color-border-dark: #d1d5db;    /* 어두운 경계선 */
}
```

## 📝 타이포그래피

### 폰트 패밀리
```css
:root {
  /* 기본 폰트 */
  --font-family-base: 'Pretendard', -apple-system, BlinkMacSystemFont,
                      'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;

  /* 수학 폰트 */
  --font-family-math: 'KaTeX_Math', 'Times New Roman', serif;

  /* 코드 폰트 */
  --font-family-mono: 'Fira Code', 'Monaco', 'Consolas', monospace;
}
```

### 폰트 크기 및 행간
```css
:root {
  /* 폰트 크기 */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */

  /* 행간 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### 텍스트 스타일 클래스
```css
/* 제목 스타일 */
.heading-1 {
  font-size: var(--text-4xl);
  font-weight: 700;
  line-height: var(--leading-tight);
  color: var(--color-text-primary);
}

.heading-2 {
  font-size: var(--text-3xl);
  font-weight: 600;
  line-height: var(--leading-tight);
  color: var(--color-text-primary);
}

/* 본문 스타일 */
.body-large {
  font-size: var(--text-lg);
  line-height: var(--leading-relaxed);
  color: var(--color-text-primary);
}

.body-base {
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-text-primary);
}

/* 수학 표현식 */
.math-expression {
  font-family: var(--font-family-math);
  font-size: var(--text-lg);
  color: var(--color-text-primary);
  background: var(--color-bg-muted);
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}
```

## 🧩 컴포넌트 라이브러리

### 버튼 컴포넌트
```css
/* 기본 버튼 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: var(--text-base);
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  text-decoration: none;
}

/* 주 버튼 */
.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* 보조 버튼 */
.btn-secondary {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-bg-muted);
  border-color: var(--color-border-dark);
}

/* 성공 버튼 */
.btn-success {
  background: var(--color-success);
  color: white;
}

/* 위험 버튼 */
.btn-danger {
  background: var(--color-error);
  color: white;
}

/* 버튼 크기 */
.btn-sm {
  padding: 8px 16px;
  font-size: var(--text-sm);
}

.btn-lg {
  padding: 16px 32px;
  font-size: var(--text-lg);
}

/* 비활성화 상태 */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}
```

### 카드 컴포넌트
```css
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.card-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.card-title {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.card-body {
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

/* 문제 카드 */
.problem-card {
  border-left: 4px solid var(--color-primary);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* 힌트 카드 */
.hint-card {
  border-left: 4px solid var(--color-hint);
  background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
}
```

이 디자인 가이드라인이 도움이 되시나요? 다음 단계로 진행할까요?

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "UI/UX \ub514\uc790\uc778 \uac00\uc774\ub4dc\ub77c\uc778 \uc791\uc131", "status": "completed", "activeForm": "\ub514\uc790\uc778 \uac00\uc774\ub4dc\ub77c\uc778 \uc791\uc131 \uc644\ub8e8"}, {"content": "\ucd9c\ub825\uac12 \uc608\uc2dc \ubc0f \uc0c1\ud0dc\ubcc4 UI \ud328\ud134 \uc815\ub9ac", "status": "in_progress", "activeForm": "UI \ud328\ud134 \uc815\ub9ac \uc911"}, {"content": "\ub300\ud654\ud615 \uc778\ud130\ud398\uc774\uc2a4 \ub514\uc790\uc778 \uc6d0\uce59 \uc791\uc131", "status": "pending", "activeForm": "\ub514\uc790\uc778 \uc6d0\uce59 \uc791\uc131 \uc911"}, {"content": "\uc811\uadfc\uc131 \uace0\ub824\uc0ac\ud56d \uac00\uc774\ub4dc \uc791\uc131", "status": "pending", "activeForm": "\uc811\uadfc\uc131 \uac00\uc774\ub4dc \uc791\uc131 \uc911"}]