import re
import logging
from typing import Dict, Any, Optional
from database.db_service import DatabaseService
from services.llm_service import LLMService


class FeedbackHandler:
    """문항 피드백 처리 핸들러"""

    def __init__(self):
        self.db_service = DatabaseService()
        self.llm_service = LLMService()

    def handle(self, learner_id: str, session_id: str, student_message: str,
              conversation_history: list, weakest_concepts: list = None) -> Dict[str, Any]:
        """문항 피드백 처리"""
        try:
            # 의도 분석 먼저
            intent = self._analyze_intent(student_message)

            # 유사문항 요청인 경우 보충 개념 사용
            if intent == "similar_item_request":
                return self._handle_similar_item_request_with_concepts(learner_id, session_id, student_message, conversation_history, weakest_concepts)

            # 기존 로직 (문제 번호 필요한 경우)
            question_number = self._extract_question_number(student_message)
            if question_number is None:
                raise ValueError("Could not identify question number from message.")

            # 평가 아이템 ID 조회
            assessment_item_id = self.db_service.get_assessment_item_id(
                learner_id, session_id, question_number
            )
            if not assessment_item_id:
                raise ValueError(f"Could not find question number {question_number} in session {session_id}")

            # 개인 학습 정보 조회
            personal_info = self.db_service.get_personal_info(learner_id, assessment_item_id)
            if not personal_info:
                raise ValueError(f"Personal info not found for item {assessment_item_id}")

            concept_name, tag_accuracy = personal_info

            # 의도별 처리
            if intent == "hint_request":
                return self._handle_hint_request(concept_name, student_message, conversation_history)
            elif intent == "similar_item_request":
                return self._handle_similar_item_request(concept_name, tag_accuracy, student_message, conversation_history)
            else:  # feedback_request
                return self._handle_feedback_request(concept_name, tag_accuracy, student_message, conversation_history)

        except Exception as e:
            logging.error(f"Feedback handler error: {e}")
            raise

    def _extract_question_number(self, message: str) -> Optional[int]:
        """메시지에서 문제 번호 추출"""
        match = re.search(r'\d+', message)
        return int(match.group(0)) if match else None

    def _analyze_intent(self, message: str, context: Dict[str, Any] = None) -> str:
        """학생 메시지 의도 분석 - LLM 기반"""
        try:
            if context is None:
                context = {"current_stage": "unknown", "has_current_problem": False}

            # LLM 의도 분석 호출
            prompts = self.llm_service.analyze_user_intent(message, context)
            response = self.llm_service.call_llm(
                prompts["system"], prompts["user"], [], "json_object"
            )

            import json
            intent_result = json.loads(response)
            detected_intent = intent_result.get("intent", "general_chat")
            confidence = intent_result.get("confidence", 0.5)

            logging.info(f"Intent analysis: {detected_intent} (confidence: {confidence}) - {intent_result.get('reasoning', '')}")

            # 기존 시스템과 호환되도록 매핑
            intent_mapping = {
                "answer_attempt": "answer_attempt",
                "hint_request": "hint_request",
                "answer_request": "answer_request",
                "concept_explanation": "concept_explanation",
                "easier_problem": "similar_item_request",  # 더 쉬운 문제도 유사문항으로
                "harder_problem": "similar_item_request",
                "different_problem": "similar_item_request",
                "different_concept": "different_concept",
                "session_control": "session_control",
                "clarification": "clarification",
                "general_chat": "feedback_request"
            }

            mapped_intent = intent_mapping.get(detected_intent, "feedback_request")

            # 낮은 신뢰도면 안전한 기본값 사용
            if confidence < 0.6:
                logging.warning(f"Low confidence intent detection: {confidence}")
                if any(keyword in message.lower() for keyword in ["문제", "유사", "비슷"]):
                    return "similar_item_request"
                elif any(keyword in message.lower() for keyword in ["힌트", "도움"]):
                    return "hint_request"
                else:
                    return "feedback_request"

            return mapped_intent

        except Exception as e:
            logging.error(f"Intent analysis failed: {e}")
            # 백업: 기존 키워드 방식
            if any(keyword in message for keyword in ["비슷한 문제", "연습 문제", "유사 문항", "유사문항"]):
                return "similar_item_request"
            elif any(keyword in message for keyword in ["힌트", "모르겠어"]):
                return "hint_request"
            else:
                return "feedback_request"

    def _handle_hint_request(self, concept_name: str, student_message: str,
                           conversation_history: list) -> Dict[str, Any]:
        """힌트 요청 처리"""
        prompts = self.llm_service.generate_hint_prompt(concept_name, student_message)
        ai_feedback = self.llm_service.call_llm(
            prompts["system"], prompts["user"], conversation_history
        )
        return {"feedback": ai_feedback}

    def _handle_similar_item_request(self, concept_name: str, tag_accuracy: float,
                                   student_message: str, conversation_history: list) -> Dict[str, Any]:
        """유사 문항 요청 처리"""
        prompts = self.llm_service.generate_similar_item_prompt(concept_name, tag_accuracy)
        response_content = self.llm_service.call_llm(
            prompts["system"], prompts["user"], conversation_history, "json_object"
        )
        result = self.llm_service.parse_similar_item_response(response_content, concept_name)
        # 개념명을 추가로 반환 (3단계에서 사용)
        result["concept_name"] = concept_name
        return result

    def _handle_feedback_request(self, concept_name: str, tag_accuracy: float,
                               student_message: str, conversation_history: list) -> Dict[str, Any]:
        """일반 피드백 요청 처리"""
        prompts = self.llm_service.generate_feedback_prompt(concept_name, tag_accuracy)
        ai_feedback = self.llm_service.call_llm(
            prompts["system"], prompts["user"], conversation_history
        )
        return {"feedback": ai_feedback}

    def _handle_similar_item_request_auto(self, learner_id: str, session_id: str,
                                        student_message: str, conversation_history: list) -> Dict[str, Any]:
        """유사문항 요청 자동 처리 (첫 번째 틀린 문제 사용)"""
        # 세션 결과 조회
        session_rows = self.db_service.get_session_results(learner_id, session_id)
        if not session_rows:
            raise ValueError(f"No data found for session {session_id}")

        # 첫 번째 틀린 문제 찾기
        wrong_questions = [row for row in session_rows if row[3] == 0]  # is_correct == 0
        if not wrong_questions:
            raise ValueError("No wrong questions found in session")

        # 첫 번째 틀린 문제의 정보 사용
        first_wrong = wrong_questions[0]
        concept_name = first_wrong[2]  # concept_name
        tag_accuracy = first_wrong[4]  # tag_accuracy

        # 유사문항 생성
        result = self._handle_similar_item_request(concept_name, tag_accuracy, student_message, conversation_history)
        result["concept_name"] = concept_name
        return result

    def _handle_similar_item_request_with_concepts(self, learner_id: str, session_id: str,
                                                 student_message: str, conversation_history: list,
                                                 weakest_concepts: list) -> Dict[str, Any]:
        """진단결과 보충 개념 기반 유사문항 요청 처리"""
        if not weakest_concepts:
            # 보충 개념이 없으면 기존 방식 사용
            return self._handle_similar_item_request_auto(learner_id, session_id, student_message, conversation_history)

        # 첫 번째 보충이 필요한 개념 사용
        target_concept = weakest_concepts[0]

        # 해당 개념의 정확도 조회 (세션 데이터에서)
        session_rows = self.db_service.get_session_results(learner_id, session_id)
        concept_accuracy = 0.5  # 기본값

        for row in session_rows:
            if row[2] == target_concept and row[3] == 0:  # 틀린 문제 중에서 해당 개념
                concept_accuracy = row[4]  # tag_accuracy
                break

        # 유사문항 생성 (설명 메시지 포함)
        result = self._handle_similar_item_request(target_concept, concept_accuracy, student_message, conversation_history)

        # 보충 필요 이유 추가
        reason_message = f"진단 결과 '{target_concept}' 개념이 보충이 필요해 보여서 관련 문제를 준비했어요!"
        result["feedback"] = f"{reason_message}\n\n{result['feedback']}"
        result["concept_name"] = target_concept
        result["is_weakness_targeted"] = True

        return result