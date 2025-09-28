# 💬 대화형 인터페이스 디자인 가이드

LLM Tutor의 대화형 인터페이스 설계를 위한 상세 가이드입니다.

## 📋 목차

- [대화형 UI 원칙](#대화형-ui-원칙)
- [소크라틱 방식 UI 패턴](#소크라틱-방식-ui-패턴)
- [상황별 인터페이스 설계](#상황별-인터페이스-설계)
- [애니메이션 및 마이크로 인터랙션](#애니메이션-및-마이크로-인터랙션)
- [음성 및 다중 입력 지원](#음성-및-다중-입력-지원)

## 🎯 대화형 UI 원칙

### 1. 자연스러운 대화 흐름 (Natural Flow)

#### 대화 턴 관리
```typescript
// 대화 턴 상태 관리
interface ConversationTurn {
  speaker: 'user' | 'ai';
  timestamp: Date;
  messageType: 'question' | 'answer' | 'hint' | 'encouragement';
  context: {
    previousTurn?: ConversationTurn;
    expectingResponse: boolean;
    timeoutDuration: number;
  };
}
```

#### UI 구현 원칙
- **대기 시간 표시**: 사용자가 응답할 시간을 충분히 제공
- **응답 유도**: 자연스럽게 다음 액션을 제안
- **컨텍스트 유지**: 이전 대화 내용과 연결성 표시

### 2. 감정적 연결 (Emotional Connection)

#### AI 페르소나 표현
```css
/* AI 아바타 상태별 표현 */
.ai-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  position: relative;
  transition: all 0.3s ease;
}

.ai-avatar.thinking {
  animation: gentle-pulse 2s infinite ease-in-out;
}

.ai-avatar.encouraging {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  box-shadow: 0 0 20px rgba(252, 211, 77, 0.3);
}

.ai-avatar.questioning {
  background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
}

@keyframes gentle-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

#### 감정 상태 표시
```jsx
const EmotionalStateIndicator = ({ mood, message }) => {
  const moodEmojis = {
    encouraging: '😊',
    questioning: '🤔',
    celebrating: '🎉',
    patient: '😌',
    thinking: '💭'
  };

  return (
    <div className={`emotion-indicator mood-${mood}`}>
      <span className="mood-emoji">{moodEmojis[mood]}</span>
      <div className="mood-pulse"></div>
    </div>
  );
};
```

### 3. 진행 상황 인식 (Progress Awareness)

#### 학습 단계 시각화
```jsx
const LearningProgressBar = ({ currentStep, totalSteps, stepTitles }) => {
  return (
    <div className="learning-progress">
      <div className="progress-header">
        <h4>학습 진행 상황</h4>
        <span>{currentStep} / {totalSteps}</span>
      </div>

      <div className="progress-steps">
        {stepTitles.map((title, index) => (
          <div
            key={index}
            className={`step ${index < currentStep ? 'completed' :
                               index === currentStep ? 'current' : 'upcoming'}`}
          >
            <div className="step-indicator">
              {index < currentStep ? '✅' :
               index === currentStep ? '🔄' : '⏳'}
            </div>
            <span className="step-title">{title}</span>
          </div>
        ))}
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        ></div>
      </div>
    </div>
  );
};
```

## 🎭 소크라틱 방식 UI 패턴

### 1. 질문 중심 인터페이스

#### 질문 카드 디자인
```css
.socratic-question {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #0ea5e9;
  border-radius: 16px;
  padding: 20px;
  margin: 16px 0;
  position: relative;
  animation: gentle-entrance 0.5s ease-out;
}

.socratic-question::before {
  content: "💡";
  position: absolute;
  top: -12px;
  left: 20px;
  background: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 16px;
}

.question-text {
  font-size: 18px;
  font-weight: 500;
  color: #0c4a6e;
  line-height: 1.6;
  margin-bottom: 12px;
}

.question-type {
  font-size: 12px;
  text-transform: uppercase;
  color: #0ea5e9;
  font-weight: 600;
  letter-spacing: 0.5px;
}

@keyframes gentle-entrance {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
```

#### 사고 유도 UI 요소
```jsx
const ThinkingPrompt = ({ question, thinkingTime, onAnswer }) => {
  const [timeLeft, setTimeLeft] = useState(thinkingTime);
  const [showHint, setShowHint] = useState(false);

  return (
    <div className="thinking-prompt">
      <div className="question-container">
        <h3>🤔 잠깐, 생각해볼까요?</h3>
        <p className="question-text">{question}</p>
      </div>

      <div className="thinking-timer">
        <div className="timer-circle">
          <span>{timeLeft}초</span>
        </div>
        <p>충분히 생각해보세요</p>
      </div>

      <div className="thinking-actions">
        <button
          className="btn-secondary"
          onClick={() => setShowHint(true)}
          disabled={timeLeft > 10}
        >
          힌트가 필요해요
        </button>
        <button
          className="btn-primary"
          onClick={onAnswer}
        >
          답변할게요
        </button>
      </div>

      {showHint && (
        <div className="gentle-hint">
          <p>💡 힌트: 각기둥은 어떤 면들로 이루어져 있을까요?</p>
        </div>
      )}
    </div>
  );
};
```

### 2. 단계적 발견 유도

#### 스텝별 가이드 컴포넌트
```jsx
const DiscoveryGuide = ({ steps, currentStep, onStepComplete }) => {
  return (
    <div className="discovery-guide">
      <h3>🔍 함께 알아볼까요?</h3>

      <div className="discovery-steps">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`discovery-step ${
              index < currentStep ? 'completed' :
              index === currentStep ? 'active' : 'locked'
            }`}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-content">
              <h4>{step.title}</h4>
              <p>{step.description}</p>

              {index === currentStep && (
                <div className="step-interaction">
                  {step.type === 'question' && (
                    <div className="question-input">
                      <input
                        type="text"
                        placeholder={step.placeholder}
                        onKeyPress={(e) => e.key === 'Enter' && onStepComplete(e.target.value)}
                      />
                    </div>
                  )}

                  {step.type === 'choice' && (
                    <div className="choice-buttons">
                      {step.choices.map((choice, i) => (
                        <button
                          key={i}
                          onClick={() => onStepComplete(choice)}
                          className="choice-btn"
                        >
                          {choice}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🎬 상황별 인터페이스 설계

### 1. 학습자가 막혔을 때

#### 좌절감 감지 및 대응
```jsx
const FrustrationDetector = ({
  consecutiveWrongAttempts,
  timeSpentOnProblem,
  onEncouragementNeeded
}) => {
  const frustrationLevel = calculateFrustration(
    consecutiveWrongAttempts,
    timeSpentOnProblem
  );

  if (frustrationLevel > 0.7) {
    return (
      <div className="encouragement-overlay">
        <div className="encouragement-content">
          <div className="encouragement-icon">🌟</div>
          <h3>잠깐, 쉬어갈까요?</h3>
          <p>어려운 문제네요. 다른 방식으로 접근해볼까요?</p>

          <div className="encouragement-options">
            <button onClick={() => onEncouragementNeeded('easier-explanation')}>
              더 쉬운 설명
            </button>
            <button onClick={() => onEncouragementNeeded('different-approach')}>
              다른 방법으로
            </button>
            <button onClick={() => onEncouragementNeeded('break-time')}>
              잠깐 쉬기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};
```

### 2. 성공 순간의 축하

#### 성취감 극대화 UI
```jsx
const SuccessCelebration = ({ achievementType, nextAction }) => {
  const celebrations = {
    'first-correct': {
      icon: '🎉',
      title: '첫 정답이에요!',
      message: '정말 잘했어요! 이제 감이 오는 것 같죠?'
    },
    'breakthrough': {
      icon: '💡',
      title: '완전히 이해했네요!',
      message: '훌륭해요! 이 방법을 다른 문제에도 적용해볼까요?'
    },
    'session-complete': {
      icon: '🏆',
      title: '모든 문제 해결!',
      message: '오늘 정말 많이 성장했어요!'
    }
  };

  const celebration = celebrations[achievementType];

  return (
    <div className="success-celebration">
      <div className="celebration-animation">
        <div className="confetti"></div>
        <div className="success-icon">{celebration.icon}</div>
      </div>

      <div className="success-content">
        <h2>{celebration.title}</h2>
        <p>{celebration.message}</p>
      </div>

      <div className="success-actions">
        <button className="btn-primary" onClick={nextAction.primary.action}>
          {nextAction.primary.label}
        </button>
        <button className="btn-secondary" onClick={nextAction.secondary.action}>
          {nextAction.secondary.label}
        </button>
      </div>
    </div>
  );
};
```

## ✨ 애니메이션 및 마이크로 인터랙션

### 1. 메시지 등장 애니메이션

#### 순차적 메시지 등장
```css
.message-entrance {
  animation: message-slide-in 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  animation-fill-mode: both;
}

.message-entrance:nth-child(1) { animation-delay: 0s; }
.message-entrance:nth-child(2) { animation-delay: 0.2s; }
.message-entrance:nth-child(3) { animation-delay: 0.4s; }

@keyframes message-slide-in {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 타이핑 효과 */
.typing-effect {
  border-right: 2px solid #3b82f6;
  animation: typing-cursor 1s infinite;
}

@keyframes typing-cursor {
  0%, 50% { border-color: #3b82f6; }
  51%, 100% { border-color: transparent; }
}
```

### 2. 상호작용 피드백

#### 버튼 호버 및 클릭 효과
```css
.interactive-btn {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.interactive-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transition: width 0.6s, height 0.6s;
  transform: translate(-50%, -50%);
}

.interactive-btn:active::before {
  width: 300px;
  height: 300px;
}

/* 성공 피드백 */
.btn-success-feedback {
  animation: success-pulse 0.6s ease-out;
}

@keyframes success-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); box-shadow: 0 0 20px rgba(34, 197, 94, 0.4); }
  100% { transform: scale(1); }
}
```

### 3. 로딩 및 대기 상태

#### 지능적 로딩 인디케이터
```jsx
const IntelligentLoader = ({ loadingType, estimatedTime, currentProgress }) => {
  const loaderConfigs = {
    'ai-thinking': {
      icon: '🤖',
      messages: [
        '문제를 분석하고 있어요...',
        '최적의 힌트를 찾고 있어요...',
        '답변을 준비하고 있어요...'
      ],
      animation: 'thinking-dots'
    },
    'problem-generating': {
      icon: '✨',
      messages: [
        '새로운 문제를 만들고 있어요...',
        '난이도를 조절하고 있어요...',
        '거의 완성되었어요...'
      ],
      animation: 'sparkle-effect'
    }
  };

  const config = loaderConfigs[loadingType];
  const currentMessage = config.messages[Math.floor(currentProgress * config.messages.length)];

  return (
    <div className="intelligent-loader">
      <div className={`loader-icon ${config.animation}`}>
        {config.icon}
      </div>

      <div className="loader-message">
        <p>{currentMessage}</p>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${currentProgress * 100}%` }}
          />
        </div>
      </div>

      <div className="estimated-time">
        약 {Math.ceil(estimatedTime - (currentProgress * estimatedTime))}초 남음
      </div>
    </div>
  );
};
```

## 🎤 음성 및 다중 입력 지원

### 1. 음성 입력 인터페이스

#### 음성 인식 버튼
```jsx
const VoiceInputButton = ({ onVoiceInput, isListening }) => {
  return (
    <button
      className={`voice-input-btn ${isListening ? 'listening' : ''}`}
      onClick={onVoiceInput}
    >
      <div className="voice-icon">
        {isListening ? '🎙️' : '🎤'}
      </div>

      {isListening && (
        <div className="voice-visualizer">
          <div className="sound-wave"></div>
          <div className="sound-wave"></div>
          <div className="sound-wave"></div>
        </div>
      )}

      <span className="voice-label">
        {isListening ? '듣고 있어요...' : '음성으로 답변'}
      </span>
    </button>
  );
};
```

### 2. 수식 입력 지원

#### 수학 수식 입력기
```jsx
const MathInputPanel = ({ onMathInput, currentExpression }) => {
  const mathSymbols = [
    { symbol: '²', label: '제곱' },
    { symbol: '√', label: '루트' },
    { symbol: 'π', label: '파이' },
    { symbol: '∞', label: '무한대' },
    { symbol: '±', label: '플러스마이너스' }
  ];

  return (
    <div className="math-input-panel">
      <div className="math-display">
        <div className="current-expression">
          {currentExpression || '수식을 입력하세요'}
        </div>
      </div>

      <div className="math-symbols">
        {mathSymbols.map((item, index) => (
          <button
            key={index}
            className="math-symbol-btn"
            onClick={() => onMathInput(item.symbol)}
            title={item.label}
          >
            {item.symbol}
          </button>
        ))}
      </div>

      <div className="math-actions">
        <button className="btn-secondary">지우기</button>
        <button className="btn-primary">입력 완료</button>
      </div>
    </div>
  );
};
```

이 대화형 인터페이스 가이드가 완성되었습니다. 다음 단계로 진행할까요?

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "UI/UX \ub514\uc790\uc778 \uac00\uc774\ub4dc\ub77c\uc778 \uc791\uc131", "status": "completed", "activeForm": "\ub514\uc790\uc778 \uac00\uc774\ub4dc\ub77c\uc778 \uc791\uc131 \uc644\ub8e8"}, {"content": "\ucd9c\ub825\uac12 \uc608\uc2dc \ubc0f \uc0c1\ud0dc\ubcc4 UI \ud328\ud134 \uc815\ub9ac", "status": "completed", "activeForm": "UI \ud328\ud134 \uc815\ub9ac \uc644\ub8e8"}, {"content": "\ub300\ud654\ud615 \uc778\ud130\ud398\uc774\uc2a4 \ub514\uc790\uc778 \uc6d0\uce59 \uc791\uc131", "status": "completed", "activeForm": "\ub514\uc790\uc778 \uc6d0\uce59 \uc791\uc131 \uc644\ub8e8"}, {"content": "\uc811\uadfc\uc131 \uace0\ub824\uc0ac\ud56d \uac00\uc774\ub4dc \uc791\uc131", "status": "in_progress", "activeForm": "\uc811\uadfc\uc131 \uac00\uc774\ub4dc \uc791\uc131 \uc911"}]