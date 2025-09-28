import json
import logging
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from config.settings import settings


class LLMService:
    """OpenAI LLM 서비스 클래스"""

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.openai_api_key,
            azure_endpoint=settings.openai_endpoint,
            api_version=settings.openai_api_version
        )

    def generate_session_summary_prompt(self, total_questions: int, correct_count: int,
                                      wrong_question_numbers: List[str], weakest_concepts: List[str]) -> Dict[str, str]:
        """세션 요약 프롬프트 생성"""
        system_prompt = "너는 학생의 진단 테스트 결과를 정확한 데이터에 기반하여 요약하고 전달하는 AI 어시스턴트야."

        user_prompt = f"""
        ### [배경 데이터]
        - 전체 문항 수: {total_questions}
        - 맞춘 문항 수: {correct_count}
        - 틀린 문제 번호 목록: {', '.join(wrong_question_numbers)}
        - 보충이 필요한 개념 목록: {', '.join(weakest_concepts)}

        ### [너의 임무]
        위 [배경 데이터]를 그대로 읽어서 [출력 형식]에 맞춰 문장을 완성해. 절대로 데이터를 수정하거나 다른 말을 추가하면 안 돼.

        ### [출력 형식]
        진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.\\n\\n전체 [전체 문항 수] 문제 중에서 [맞춘 문항 수] 문제를 맞혔네. 정말 잘했어! 👍\\n\\n이번 테스트에서는 아쉽게도 [틀린 문제 번호 목록] 번 문제를 틀렸더라. 데이터를 분석해보니, 주로 "[보충이 필요한 개념 목록]" 개념들이 조금 헷갈리는 것 같아.\\n\\n우리 같이 "[보충이 필요한 개념 목록 중 첫 번째 개념]"에 대한 학습을 시작해볼까?
        """

        return {"system": system_prompt, "user": user_prompt}

    def generate_hint_prompt(self, concept_name: str, student_message: str) -> Dict[str, str]:
        """힌트 요청 프롬프트 생성"""
        system_prompt = "너는 정답을 알려주지 않고 다음 단계를 생각하게 만드는 '소크라틱 방식'의 힌트를 제공하는 AI 튜터야."

        user_prompt = f"""### 배경 정보
- 관련 개념: {concept_name}
- 학생 메시지: "{student_message}"

### 임무
절대 학습 전략이나 긴 격려 메시지를 말하지 말고, 오직 문제 풀이에 도움이 되는 다음 단계 질문을 한두 문장으로 간결하게 제시해."""

        return {"system": system_prompt, "user": user_prompt}

    def generate_similar_item_prompt(self, concept_name: str, tag_accuracy: float) -> Dict[str, str]:
        """유사 문항 생성 프롬프트 생성"""
        system_prompt = "너는 학생의 수준에 맞는 새로운 수학 연습 문제를 생성하는 AI야. 반드시 지정된 JSON 형식으로만 답변해야 해."

        user_prompt = f"""### 정보
- 개념: '{concept_name}'
- 학생의 이 개념 정확도: {tag_accuracy * 100:.1f}%

### 임무
'{concept_name}' 개념에 대한 새로운 유사 문항을 생성해. 학생의 정확도를 고려하여 너무 어렵지 않게 만들어야 해.

### 중요한 주의사항
1. 반드시 해설의 계산 과정을 먼저 완료한 후, 그 결과를 correct_answer에 입력해야 해
2. correct_answer와 explanation의 최종 답이 일치해야 해
3. 계산 실수가 없도록 단계별로 검증해줘

### 출력 형식 (JSON)
{{"new_question_text": "...", "correct_answer": "...", "explanation": "..."}}

### 예시 검증 과정
문제를 만든 후 반드시:
1. explanation에서 단계별 계산 수행
2. 최종 결과 값 확인
3. correct_answer에 동일한 값 입력
4. 두 값이 일치하는지 재확인"""

        return {"system": system_prompt, "user": user_prompt}

    def generate_feedback_prompt(self, concept_name: str, tag_accuracy: float) -> Dict[str, str]:
        """일반 피드백 프롬프트 생성"""
        system_prompt = "너는 학생의 학습 데이터를 분석하고, 개인화된 학습 전략과 격려를 제공하는 전문 AI 학습 코치야."

        user_prompt = f"""### 학생 학습 데이터
- 관련 개념: {concept_name}
- 이 학생의 해당 개념 정확도: {tag_accuracy * 100:.1f}%

### 너의 임무
위 데이터를 '해석'해서, 학생에게 격려 메시지와 구체적인 학습 전략을 요약해줘."""

        return {"system": system_prompt, "user": user_prompt}

    def generate_generated_item_hint_prompt(self, question_text: str, student_message: str) -> Dict[str, str]:
        """생성된 문항 힌트 프롬프트 생성 (기존 버전 - 호환성 유지)"""
        system_prompt = "너는 학생이 보고 있는 문제에 대해, 정답을 알려주지 않고 다음 단계를 생각하게 만드는 '소크라틱 방식'의 힌트를 제공하는 AI 튜터야."

        user_prompt = f"""### 문제 텍스트
{question_text}

### 학생 메시지
"{student_message}"

### 임무
위 문제에 대한 간결한 힌트를 질문 형태로 제공해줘."""

        return {"system": system_prompt, "user": user_prompt}

    def generate_personalized_hint_prompt(self, question_text: str, student_message: str,
                                        personalization_data: Dict[str, Any]) -> Dict[str, str]:
        """개인화된 힌트 프롬프트 생성"""
        learner_id = personalization_data.get("learner_id", "Unknown")
        original_concept = personalization_data.get("original_concept", "Unknown")
        personal_accuracy = personalization_data.get("personal_accuracy")
        hint_level = personalization_data.get("hint_level", "beginner")

        system_prompt = f"""너는 학생의 개인 학습 데이터를 분석하여 맞춤형 소크라틱 힌트를 제공하는 AI 튜터야.

### 학습자 정보
- 학습자 ID: {learner_id}
- 관련 개념: {original_concept}
- 개인 정확도: {f"{personal_accuracy*100:.1f}%" if personal_accuracy else "정보 없음"}
- 힌트 레벨: {hint_level}

### 힌트 제공 원칙
- {hint_level} 학습자에게 적합한 수준으로 조절
- 절대 정답을 직접 알려주지 말고 소크라틱 질문으로 유도
- 학습자의 이해도에 맞는 단계별 접근"""

        # 힌트 레벨별 상세 지침
        level_instructions = {
            "beginner": "매우 구체적이고 단계별로 천천히 안내. 기본 개념부터 확인",
            "intermediate": "중간 수준의 힌트. 핵심 포인트를 제시하되 스스로 생각할 여지 제공",
            "advanced": "간결하고 핵심적인 힌트. 최소한의 가이드로 자율적 사고 유도"
        }

        user_prompt = f"""### 문제 텍스트
{question_text}

### 학생 메시지
"{student_message}"

### 개인화 지침
{level_instructions.get(hint_level, level_instructions["beginner"])}

### 임무
위 정보를 종합하여 이 학습자에게 가장 적합한 소크라틱 힌트를 제공해줘."""

        return {"system": system_prompt, "user": user_prompt}

    def generate_guided_hint_prompt(self, question_text: str, student_message: str,
                                   answer_analysis: Dict[str, Any], personalization_data: Dict[str, Any]) -> Dict[str, str]:
        """부분 정답이나 좋은 접근에 대한 가이드 힌트 프롬프트 생성"""
        confidence = answer_analysis.get("confidence", 0.0)
        is_partial_correct = answer_analysis.get("is_partial_correct", False)
        has_good_approach = answer_analysis.get("has_good_approach", False)
        hint_level = personalization_data.get("hint_level", "beginner")

        system_prompt = f"""너는 학생의 부분 정답이나 좋은 접근 방법을 인정하고 격려하며, 완전한 정답으로 이끄는 AI 튜터야.

### 학생 상황 분석
- 답안 신뢰도: {confidence*100:.1f}%
- 부분 정답 여부: {'예' if is_partial_correct else '아니오'}
- 접근 방법 적절성: {'좋음' if has_good_approach else '보통'}
- 힌트 레벨: {hint_level}

### 가이드 원칙
1. 먼저 학생의 시도를 인정하고 격려
2. 부족한 부분을 구체적으로 지적
3. 다음 단계로 자연스럽게 유도
4. 정답에 가까워지도록 방향 제시"""

        if is_partial_correct:
            focus = "숫자는 정확하지만 단위나 표기법을 완성하도록 도움"
        elif has_good_approach:
            focus = "접근 방법이 좋으니 계산 과정을 더 정확하게 진행하도록 도움"
        else:
            focus = "현재 시도를 바탕으로 올바른 방향으로 안내"

        user_prompt = f"""### 문제
{question_text}

### 학생 답안
"{student_message}"

### 가이드 방향
{focus}

### 임무
학생의 시도를 격려하고, 정답에 더 가까워질 수 있는 구체적인 다음 단계를 소크라틱 질문으로 제시해줘."""

        return {"system": system_prompt, "user": user_prompt}

    def analyze_user_intent(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 의도 분석"""
        current_stage = context.get("current_stage", "unknown")
        has_current_problem = context.get("has_current_problem", False)

        system_prompt = """너는 학습자의 메시지를 분석해서 정확한 의도를 파악하는 AI야.
반드시 JSON 형식으로만 답변해야 해."""

        user_prompt = f"""### 상황 정보
- 현재 단계: {current_stage}
- 문제 풀이 중: {'예' if has_current_problem else '아니오'}

### 사용자 메시지
"{user_message}"

### 의도 분류 기준
1. answer_attempt: 숫자나 구체적 답을 제시 (예: "210", "210cm²", "답은 5야")
2. hint_request: 힌트나 도움 요청 (예: "힌트 주세요", "어떻게 풀어요?", "모르겠어요")
3. answer_request: 정답을 직접 알려달라는 요청 (예: "정답 알려줘", "답이 뭐야?")
4. concept_explanation: 개념 설명 요청 (예: "이 개념 설명해줘", "원리가 뭐야?")
5. easier_problem: 더 쉬운 문제 요청 (예: "너무 어려워", "쉬운 문제 줘")
6. harder_problem: 더 어려운 문제 요청 (예: "더 어려운 것", "도전적인 문제")
7. different_problem: 다른 문제 요청 (예: "다른 문제", "새로운 문제")
8. different_concept: 다른 개념 학습 (예: "다른 개념", "이거 말고 다른 거")
9. session_control: 학습 중단/종료 (예: "그만할래", "나가기", "쉬고 싶어")
10. clarification: 설명이나 재질문 (예: "무슨 뜻이야?", "다시 말해줘")
11. general_chat: 일반 대화 (예: "안녕", "고마워", "화장실 가야 해")

### 출력 형식 (JSON)
{{"intent": "분류된_의도", "confidence": 0.0-1.0_신뢰도, "reasoning": "판단_근거"}}"""

        return {"system": system_prompt, "user": user_prompt}

    def call_llm(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]],
                 response_format: str = "text") -> str:
        """LLM 호출 및 응답 반환"""
        try:
            response_format_config = {"type": response_format}

            messages_to_send = [{"role": "system", "content": system_prompt}] + conversation_history
            messages_to_send.append({"role": "user", "content": user_prompt})

            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages_to_send,
                response_format=response_format_config
            )

            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"LLM call failed: {e}")
            raise

    def parse_similar_item_response(self, response_content: str, concept_name: str) -> Dict[str, Any]:
        """유사 문항 생성 응답 파싱"""
        try:
            generated_data = json.loads(response_content)

            # 답안과 해설 일치성 검증
            correct_answer = generated_data.get('correct_answer', '')
            explanation = generated_data.get('explanation', '')

            # 정답에서 숫자 추출
            import re
            answer_numbers = re.findall(r'\d+(?:\.\d+)?', correct_answer)
            explanation_numbers = re.findall(r'\d+(?:\.\d+)?', explanation)

            # 일치성 검증: 정답의 숫자가 해설에 포함되어 있는지 확인
            if answer_numbers and explanation_numbers:
                if not any(num in explanation_numbers for num in answer_numbers):
                    logging.warning(f"Answer-explanation mismatch detected: answer={correct_answer}, explanation numbers={explanation_numbers}")
                    # 해설에서 가장 큰 숫자를 정답으로 수정 (일반적으로 최종 답)
                    if explanation_numbers:
                        largest_num = max(explanation_numbers, key=float)
                        # 단위 유지하면서 숫자만 교체
                        original_units = re.findall(r'[a-zA-Z²³°]+', correct_answer)
                        corrected_answer = largest_num + (original_units[0] if original_units else '')
                        generated_data['correct_answer'] = corrected_answer
                        logging.info(f"Corrected answer from {correct_answer} to {corrected_answer}")

            ai_feedback = f"좋아! '{concept_name}' 개념을 더 연습해볼까? 아래 문제를 풀어봐.\n\n{generated_data.get('new_question_text')}"

            return {
                "feedback": ai_feedback,
                "generated_question_data": generated_data
            }
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse similar item response: {e}")
            raise