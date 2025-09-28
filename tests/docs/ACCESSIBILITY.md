# ♿ 접근성 가이드라인

모든 사용자가 동등하게 LLM Tutor를 사용할 수 있도록 하는 접근성 가이드입니다.

## 📋 목차

- [접근성 원칙](#접근성-원칙)
- [키보드 접근성](#키보드-접근성)
- [스크린 리더 지원](#스크린-리더-지원)
- [시각적 접근성](#시각적-접근성)
- [인지적 접근성](#인지적-접근성)
- [다국어 및 국제화](#다국어-및-국제화)
- [테스트 가이드라인](#테스트-가이드라인)

## 🎯 접근성 원칙

### WCAG 2.1 준수
LLM Tutor는 웹 콘텐츠 접근성 가이드라인(WCAG) 2.1 AA 수준을 준수합니다.

#### 4가지 핵심 원칙
1. **인식 가능(Perceivable)**: 모든 정보가 사용자가 인식할 수 있는 형태로 제공
2. **운용 가능(Operable)**: 모든 기능이 사용자가 조작할 수 있는 형태로 제공
3. **이해 가능(Understandable)**: 정보와 UI 작동이 이해 가능한 형태로 제공
4. **견고성(Robust)**: 다양한 기술(보조 기술 포함)로 콘텐츠 해석 가능

### 교육 접근성 특별 고려사항
- **학습 장애 지원**: 다양한 학습 스타일과 인지적 차이 고려
- **수학 접근성**: 수식과 도형에 대한 접근 가능한 대체 설명
- **언어 접근성**: 명확하고 이해하기 쉬운 언어 사용

## ⌨️ 키보드 접근성

### 키보드 내비게이션

#### 기본 키보드 단축키
```typescript
const keyboardShortcuts = {
  // 기본 내비게이션
  'Tab': '다음 요소로 이동',
  'Shift+Tab': '이전 요소로 이동',
  'Enter': '활성화/선택',
  'Space': '버튼 활성화/체크박스 토글',
  'Escape': '모달 닫기/취소',

  // 메시지 입력
  'Ctrl+Enter': '메시지 전송',
  'Shift+Enter': '줄바꿈',

  // 학습 기능
  'H': '힌트 요청',
  'N': '새 문제',
  'S': '답안 제출',

  // 접근성 기능
  'Ctrl+;': '고대비 모드 토글',
  'Ctrl+Plus': '텍스트 크기 증가',
  'Ctrl+Minus': '텍스트 크기 감소'
};
```

#### 포커스 관리
```css
/* 포커스 표시 - 명확하고 눈에 잘 띄는 포커스 링 */
*:focus {
  outline: 3px solid #3b82f6;
  outline-offset: 2px;
  border-radius: 4px;
}

/* 고대비 모드에서의 포커스 */
@media (prefers-contrast: high) {
  *:focus {
    outline: 4px solid #000000;
    outline-offset: 2px;
    background-color: #ffff00;
  }
}

/* 포커스 순서가 논리적이 되도록 tabindex 관리 */
.chat-interface {
  /* 포커스 트랩 - 모달 내에서만 포커스 이동 */
}

.modal-overlay {
  /* 모달이 열렸을 때 배경 포커스 차단 */
  inert: true;
}
```

#### 포커스 트랩 구현
```typescript
const useFocusTrap = (isActive: boolean) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }, [isActive]);

  return containerRef;
};
```

## 📢 스크린 리더 지원

### ARIA 라벨링

#### 의미 있는 라벨 제공
```jsx
const ChatMessage = ({ message, sender, timestamp }) => {
  return (
    <div
      role="log"
      aria-live="polite"
      aria-label={`${sender}가 ${timestamp}에 보낸 메시지`}
      className={`message ${sender}`}
    >
      {/* 발신자 정보 */}
      <div
        aria-label={`메시지 발신자: ${sender}`}
        className="message-sender"
      >
        {sender === 'ai' ? '🤖 AI 튜터' : '👤 학생'}
      </div>

      {/* 메시지 내용 */}
      <div
        aria-label="메시지 내용"
        className="message-content"
      >
        {message.content}
      </div>

      {/* 타임스탬프 */}
      <time
        dateTime={timestamp.toISOString()}
        aria-label={`전송 시간: ${timestamp.toLocaleString()}`}
        className="message-timestamp"
      >
        {timestamp.toLocaleTimeString()}
      </time>
    </div>
  );
};
```

#### 상태 알림
```jsx
const LoadingAnnouncer = ({ isLoading, loadingMessage }) => {
  return (
    <div
      aria-live="assertive"
      aria-atomic="true"
      className="sr-only"
    >
      {isLoading && (
        <span>
          {loadingMessage || 'AI가 응답을 준비하고 있습니다. 잠시 기다려주세요.'}
        </span>
      )}
    </div>
  );
};

const SuccessAnnouncer = ({ success }) => {
  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    >
      {success && (
        <span>
          정답입니다! 축하합니다. 다음 단계로 진행할 수 있습니다.
        </span>
      )}
    </div>
  );
};
```

### 수학 내용 접근성

#### 수식 읽기 지원
```jsx
const MathExpression = ({ expression, description }) => {
  return (
    <div className="math-expression">
      {/* 시각적 수식 */}
      <div aria-hidden="true" className="math-visual">
        {expression}
      </div>

      {/* 스크린 리더용 설명 */}
      <div className="sr-only">
        {description}
      </div>

      {/* 대체 텍스트 버튼 */}
      <button
        className="math-alt-text"
        onClick={() => speakMathDescription(description)}
        aria-label="수식 음성 설명 듣기"
      >
        🔊
      </button>
    </div>
  );
};

// 사용 예시
<MathExpression
  expression="x² + 2x + 1 = 0"
  description="x의 제곱 더하기 2x 더하기 1은 0과 같다"
/>
```

#### 도형 및 그래프 설명
```jsx
const GeometryDescription = ({ shape, dimensions, description }) => {
  return (
    <figure role="img" aria-labelledby="shape-title" aria-describedby="shape-desc">
      <h4 id="shape-title">{shape} 도형</h4>

      {/* 시각적 도형 */}
      <div aria-hidden="true" className="shape-visual">
        {/* SVG 또는 Canvas 도형 */}
      </div>

      {/* 상세 설명 */}
      <figcaption id="shape-desc">
        <p>{description}</p>
        <ul>
          {Object.entries(dimensions).map(([key, value]) => (
            <li key={key}>
              {key}: {value}
            </li>
          ))}
        </ul>
      </figcaption>

      {/* 촉각적 탐색 버튼 */}
      <button
        onClick={() => provideTactileExploration(shape)}
        aria-label="도형 촉각적 탐색 시작"
      >
        촉각 탐색
      </button>
    </figure>
  );
};
```

## 👁️ 시각적 접근성

### 색상 및 대비

#### 고대비 모드 지원
```css
/* 기본 색상 */
:root {
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --border-color: #e5e7eb;
  --focus-color: #3b82f6;
}

/* 고대비 모드 */
@media (prefers-contrast: high) {
  :root {
    --text-primary: #000000;
    --text-secondary: #333333;
    --bg-primary: #ffffff;
    --bg-secondary: #f0f0f0;
    --border-color: #000000;
    --focus-color: #000000;
  }

  .btn-primary {
    background: #000000;
    color: #ffffff;
    border: 2px solid #000000;
  }

  .message.ai {
    background: #ffffff;
    border: 2px solid #000000;
    color: #000000;
  }

  .message.user {
    background: #000000;
    color: #ffffff;
    border: 2px solid #000000;
  }
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
  :root {
    --text-primary: #f9fafb;
    --text-secondary: #d1d5db;
    --bg-primary: #111827;
    --bg-secondary: #1f2937;
    --border-color: #374151;
    --focus-color: #60a5fa;
  }
}
```

#### 색상 대비 비율 확인
```typescript
// 색상 대비 검사 유틸리티
const checkColorContrast = (foreground: string, background: string): number => {
  // WCAG 색상 대비 비율 계산
  const luminance1 = getRelativeLuminance(foreground);
  const luminance2 = getRelativeLuminance(background);

  const lighter = Math.max(luminance1, luminance2);
  const darker = Math.min(luminance1, luminance2);

  return (lighter + 0.05) / (darker + 0.05);
};

// AA 수준 (4.5:1) 및 AAA 수준 (7:1) 검사
const isAccessibleContrast = (ratio: number, level: 'AA' | 'AAA' = 'AA'): boolean => {
  return level === 'AA' ? ratio >= 4.5 : ratio >= 7;
};
```

### 텍스트 크기 조절

#### 확대/축소 지원
```css
/* 기본 텍스트 크기 */
html {
  font-size: 16px;
}

/* 사용자 설정에 따른 텍스트 크기 */
.text-size-small { font-size: 0.875rem; }
.text-size-normal { font-size: 1rem; }
.text-size-large { font-size: 1.125rem; }
.text-size-extra-large { font-size: 1.25rem; }

/* 200% 확대 시에도 레이아웃 유지 */
@media (min-resolution: 2dppx) {
  .responsive-layout {
    max-width: 50vw;
  }
}
```

#### 동적 텍스트 크기 조절
```tsx
const TextSizeController = () => {
  const [textSize, setTextSize] = useState('normal');

  const adjustTextSize = (direction: 'increase' | 'decrease') => {
    const sizes = ['small', 'normal', 'large', 'extra-large'];
    const currentIndex = sizes.indexOf(textSize);

    if (direction === 'increase' && currentIndex < sizes.length - 1) {
      setTextSize(sizes[currentIndex + 1]);
    } else if (direction === 'decrease' && currentIndex > 0) {
      setTextSize(sizes[currentIndex - 1]);
    }
  };

  useEffect(() => {
    document.documentElement.className = `text-size-${textSize}`;
  }, [textSize]);

  return (
    <div className="text-size-controls" role="group" aria-label="텍스트 크기 조절">
      <button
        onClick={() => adjustTextSize('decrease')}
        aria-label="텍스트 크기 줄이기"
        disabled={textSize === 'small'}
      >
        A-
      </button>

      <span aria-live="polite" className="current-size">
        현재 크기: {textSize}
      </span>

      <button
        onClick={() => adjustTextSize('increase')}
        aria-label="텍스트 크기 늘리기"
        disabled={textSize === 'extra-large'}
      >
        A+
      </button>
    </div>
  );
};
```

## 🧠 인지적 접근성

### 명확한 언어 사용

#### 쉬운 언어 가이드라인
```typescript
// 복잡한 수학 용어의 쉬운 설명
const mathTerms = {
  '이차방정식': {
    simple: 'x가 두 번 곱해진 식',
    example: 'x² + 2x + 1 = 0 같은 식이에요',
    visual: '포물선 모양의 그래프'
  },
  '피타고라스 정리': {
    simple: '직각삼각형에서 변의 길이 관계',
    example: '가장 긴 변의 제곱 = 다른 두 변의 제곱의 합',
    visual: '직각삼각형 그림과 함께 설명'
  }
};

// 단계별 설명 제공
const StepByStepExplanation = ({ concept, steps }) => {
  const [currentStep, setCurrentStep] = useState(0);

  return (
    <div className="step-explanation">
      <h3>{concept} - 단계별 설명</h3>

      <div className="progress-indicator">
        <span>단계 {currentStep + 1} / {steps.length}</span>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>

      <div className="current-step">
        <h4>{steps[currentStep].title}</h4>
        <p>{steps[currentStep].description}</p>

        {steps[currentStep].example && (
          <div className="example">
            <strong>예시:</strong> {steps[currentStep].example}
          </div>
        )}
      </div>

      <div className="step-navigation">
        <button
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
        >
          이전 단계
        </button>

        <button
          onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
          disabled={currentStep === steps.length - 1}
        >
          다음 단계
        </button>
      </div>
    </div>
  );
};
```

### 집중력 지원

#### 산만함 줄이기
```css
/* 집중 모드 */
.focus-mode {
  /* 불필요한 요소 숨기기 */
  .sidebar { display: none; }
  .decorative-elements { display: none; }
  .advertisement { display: none; }

  /* 핵심 콘텐츠만 강조 */
  .main-content {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    background: var(--bg-primary);
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  /* 애니메이션 줄이기 */
  *, *::before, *::after {
    animation-duration: 0.1s !important;
    transition-duration: 0.1s !important;
  }
}

/* 주의력 결핍 지원 */
.adhd-friendly {
  /* 명확한 시각적 구분 */
  .section {
    border: 2px solid var(--border-color);
    margin-bottom: 2rem;
    padding: 1.5rem;
    border-radius: 8px;
  }

  /* 중요한 정보 강조 */
  .important {
    background: #fef3c7;
    border-left: 4px solid #f59e0b;
    padding: 1rem;
    font-weight: 600;
  }

  /* 진행 상황 명확히 표시 */
  .progress-indicator {
    position: sticky;
    top: 0;
    background: var(--bg-primary);
    padding: 1rem;
    border-bottom: 2px solid var(--border-color);
  }
}
```

## 🌍 다국어 및 국제화

### 언어 지원

#### 다국어 인터페이스
```typescript
// 다국어 설정
const languageConfig = {
  ko: {
    code: 'ko-KR',
    name: '한국어',
    direction: 'ltr',
    font: 'Pretendard, sans-serif'
  },
  en: {
    code: 'en-US',
    name: 'English',
    direction: 'ltr',
    font: 'Inter, sans-serif'
  },
  ja: {
    code: 'ja-JP',
    name: '日本語',
    direction: 'ltr',
    font: 'Noto Sans JP, sans-serif'
  },
  ar: {
    code: 'ar-SA',
    name: 'العربية',
    direction: 'rtl',
    font: 'Noto Sans Arabic, sans-serif'
  }
};

// RTL 지원
const LanguageProvider = ({ language, children }) => {
  const config = languageConfig[language];

  useEffect(() => {
    document.documentElement.lang = config.code;
    document.documentElement.dir = config.direction;
    document.documentElement.style.fontFamily = config.font;
  }, [config]);

  return (
    <div className={`language-${language} dir-${config.direction}`}>
      {children}
    </div>
  );
};
```

#### 문화적 고려사항
```typescript
// 문화별 수학 표기법
const mathNotations = {
  ko: {
    decimal: ',',
    thousands: '.',
    currency: '₩',
    dateFormat: 'YYYY년 MM월 DD일'
  },
  en: {
    decimal: '.',
    thousands: ',',
    currency: '$',
    dateFormat: 'MM/DD/YYYY'
  },
  de: {
    decimal: ',',
    thousands: '.',
    currency: '€',
    dateFormat: 'DD.MM.YYYY'
  }
};

// 문화별 색상 의미
const culturalColors = {
  ko: {
    success: '#22c55e', // 초록 - 성공
    warning: '#f59e0b', // 주황 - 주의
    error: '#ef4444',   // 빨강 - 오류
    luck: '#fbbf24'     // 노랑 - 행운
  },
  cn: {
    success: '#dc2626', // 빨강 - 행운, 성공
    warning: '#f59e0b',
    error: '#374151',   // 검정 - 불운
    luck: '#dc2626'
  }
};
```

## 🧪 테스트 가이드라인

### 자동화된 접근성 테스트

#### Jest + Testing Library 테스트
```typescript
// 접근성 테스트 유틸리티
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('ChatInterface Accessibility', () => {
  test('should not have accessibility violations', async () => {
    const { container } = render(
      <ChatInterface learnerID="test" sessionID="test" />
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('should have proper ARIA labels', () => {
    render(<ChatInterface learnerID="test" sessionID="test" />);

    expect(screen.getByRole('log')).toBeInTheDocument();
    expect(screen.getByLabelText('메시지 입력')).toBeInTheDocument();
    expect(screen.getByLabelText('메시지 전송')).toBeInTheDocument();
  });

  test('should support keyboard navigation', () => {
    render(<ChatInterface learnerID="test" sessionID="test" />);

    const input = screen.getByLabelText('메시지 입력');
    const sendButton = screen.getByLabelText('메시지 전송');

    // Tab 키로 포커스 이동 확인
    input.focus();
    expect(document.activeElement).toBe(input);

    // Enter 키로 메시지 전송 확인
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
    // 전송 동작 확인
  });
});
```

### 수동 테스트 체크리스트

#### 스크린 리더 테스트
- [ ] NVDA/JAWS로 전체 인터페이스 탐색 가능
- [ ] 수학 수식이 올바르게 읽힘
- [ ] 로딩 상태가 음성으로 안내됨
- [ ] 오류 메시지가 명확하게 전달됨

#### 키보드 테스트
- [ ] Tab 키만으로 모든 기능 접근 가능
- [ ] 포커스 순서가 논리적
- [ ] 키보드 트랩이 없음
- [ ] 단축키가 올바르게 동작

#### 시각적 테스트
- [ ] 200% 확대 시에도 레이아웃 유지
- [ ] 고대비 모드에서 모든 요소 인식 가능
- [ ] 색상 정보에만 의존하지 않음
- [ ] 포커스 표시가 명확함

이제 모든 디자인 가이드라인이 완성되었습니다!

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "UI/UX \ub514\uc790\uc778 \uac00\uc774\ub4dc\ub77c\uc778 \uc791\uc131", "status": "completed", "activeForm": "\ub514\uc790\uc778 \uac00\uc774\ub4dc\ub77c\uc778 \uc791\uc131 \uc644\ub8e8"}, {"content": "\ucd9c\ub825\uac12 \uc608\uc2dc \ubc0f \uc0c1\ud0dc\ubcc4 UI \ud328\ud134 \uc815\ub9ac", "status": "completed", "activeForm": "UI \ud328\ud134 \uc815\ub9ac \uc644\ub8e8"}, {"content": "\ub300\ud654\ud615 \uc778\ud130\ud398\uc774\uc2a4 \ub514\uc790\uc778 \uc6d0\uce59 \uc791\uc131", "status": "completed", "activeForm": "\ub514\uc790\uc778 \uc6d0\uce59 \uc791\uc131 \uc644\ub8e8"}, {"content": "\uc811\uadfc\uc131 \uace0\ub824\uc0ac\ud56d \uac00\uc774\ub4dc \uc791\uc131", "status": "completed", "activeForm": "\uc811\uadfc\uc131 \uac00\uc774\ub4dc \uc791\uc131 \uc644\ub8e8"}]