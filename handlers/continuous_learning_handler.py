import logging
from typing import Dict, Any, List, Optional
from handlers.session_state_manager import session_manager, LearningSession
from handlers.feedback_handler import FeedbackHandler
from handlers.generated_item_handler import GeneratedItemHandler
from services.llm_service import LLMService


class ContinuousLearningHandler:
    """연속 학습 플로우 관리 핸들러"""

    def __init__(self):
        self.feedback_handler = FeedbackHandler()
        self.generated_item_handler = GeneratedItemHandler()
        self.llm_service = LLMService()

    def handle_user_action(self, learner_id: str, session_id: str, action: str,
                          data: Any = None, user_input: str = "") -> Dict[str, Any]:
        """사용자 액션 처리"""
        session = session_manager.get_session(learner_id, session_id)

        if not session:
            return {"error": "세션을 찾을 수 없습니다. 새로 시작해주세요."}

        # 대화 히스토리에 사용자 입력 추가
        if user_input:
            session_manager.add_conversation(learner_id, session_id, "user", user_input)

        try:
            if action == "continue_learning":
                return self._handle_continue_learning(session)
            elif action == "new_problem_same_concept":
                return self._handle_new_problem_same_concept(session)
            elif action == "next_concept":
                return self._handle_next_concept(session)
            elif action == "harder_problem":
                return self._handle_harder_problem(session)
            elif action == "easier_problem":
                return self._handle_easier_problem(session)
            elif action == "concept_explanation":
                return self._handle_concept_explanation(session)
            elif action == "session_summary":
                return self._handle_session_summary(session)
            elif action == "end_session":
                return self._handle_end_session(session)
            elif action == "text_input":
                return self._handle_text_input(session, user_input)
            elif action == "start_practice":
                return self._handle_start_practice(session)
            elif action == "explain_concepts":
                return self._handle_explain_concepts(session)
            elif action == "ask_questions":
                return self._handle_ask_questions(session, user_input)
            elif action == "new_diagnosis":
                return self._handle_new_diagnosis(session)
            else:
                return {"error": f"알 수 없는 액션: {action}"}

        except Exception as e:
            logging.error(f"Action handling error: {e}")
            return {"error": "처리 중 오류가 발생했습니다. 다시 시도해주세요."}

    def _handle_continue_learning(self, session: LearningSession) -> Dict[str, Any]:
        """학습 계속하기"""
        if session.current_stage == "practice" and session.current_problem:
            # 현재 문제 계속 풀기
            return {
                "feedback": "현재 문제를 계속 풀어보세요!",
                "current_problem": session.current_problem,
                "quick_replies": self._get_practice_options(session)
            }
        else:
            # 새 문제 시작
            return self._handle_new_problem_same_concept(session)

    def _handle_new_problem_same_concept(self, session: LearningSession) -> Dict[str, Any]:
        """같은 개념 새 문제"""
        if not session.current_concept:
            return self._handle_next_concept(session)

        # 새 문제 생성
        conversation_history = session.conversation_history[-6:]  # 최근 6개만
        result = self.feedback_handler._handle_similar_item_request(
            session.current_concept, 0.5, "비슷한 문제 주세요", conversation_history
        )

        # 세션 상태 업데이트
        session_manager.start_new_problem(session.learner_id, session.session_id,
                                        result['generated_question_data'])

        # AI 응답에 대화 히스토리 추가
        session_manager.add_conversation(session.learner_id, session.session_id,
                                       "assistant", result['feedback'])

        return {
            "feedback": result['feedback'],
            "generated_question_data": result['generated_question_data'],
            "quick_replies": self._get_practice_options(session)
        }

    def _handle_next_concept(self, session: LearningSession) -> Dict[str, Any]:
        """다음 개념으로 이동"""
        next_concept = session_manager.get_next_concept(session.learner_id, session.session_id)

        if not next_concept:
            return self._handle_session_summary(session)

        session.current_concept = next_concept
        session_manager.update_session_stage(session.learner_id, session.session_id, "practice")

        feedback = f"이제 '{next_concept}' 개념을 학습해볼까요? 새로운 문제를 준비할게요!"

        # 새 개념 문제 생성
        result = self.feedback_handler._handle_similar_item_request(
            next_concept, 0.5, "문제 주세요", session.conversation_history[-6:]
        )

        session_manager.start_new_problem(session.learner_id, session.session_id,
                                        result['generated_question_data'])

        return {
            "feedback": f"{feedback}\n\n{result['feedback']}",
            "generated_question_data": result['generated_question_data'],
            "quick_replies": self._get_practice_options(session)
        }

    def _handle_concept_explanation(self, session: LearningSession) -> Dict[str, Any]:
        """개념 설명 요청"""
        if not session.current_concept:
            return {"feedback": "현재 학습 중인 개념이 없습니다."}

        explanation_prompt = f"'{session.current_concept}' 개념을 중학생이 이해하기 쉽게 설명해주세요."

        explanation = self.llm_service.call_llm(
            "너는 중학생에게 수학 개념을 쉽고 친근하게 설명하는 선생님이야.",
            explanation_prompt,
            session.conversation_history[-6:]
        )

        session_manager.add_conversation(session.learner_id, session.session_id,
                                       "assistant", explanation)

        return {
            "feedback": explanation,
            "quick_replies": [
                {"text": "예제 문제 풀어보기", "action": "new_problem_same_concept"},
                {"text": "다른 개념 배우기", "action": "next_concept"},
                {"text": "더 자세한 설명", "action": "concept_explanation"},
                {"text": "학습 마무리", "action": "session_summary"}
            ]
        }

    def _handle_session_summary(self, session: LearningSession) -> Dict[str, Any]:
        """세션 요약"""
        summary = session_manager.get_session_summary(session.learner_id, session.session_id)

        feedback = f"""🎓 오늘 학습 요약

✅ 풀어본 문제: {summary['total_problems_solved']}개
💡 사용한 힌트: {summary['total_hints_used']}개
📚 완료한 개념: {', '.join(summary['completed_concepts']) if summary['completed_concepts'] else '없음'}
⏰ 학습 시간: {summary['session_duration_minutes']}분

{"🎉 모든 취약 개념을 완료했어요!" if not summary['remaining_concepts'] else f"📝 남은 개념: {', '.join(summary['remaining_concepts'])}"}"""

        quick_replies = []
        if summary['remaining_concepts']:
            quick_replies.extend([
                {"text": "남은 개념 계속 학습", "action": "next_concept"},
                {"text": "완료한 개념 복습", "action": "review_completed"}
            ])

        quick_replies.extend([
            {"text": "새로운 진단테스트", "action": "new_diagnosis"},
            {"text": "학습 종료", "action": "end_session"}
        ])

        return {
            "feedback": feedback,
            "quick_replies": quick_replies,
            "session_summary": summary
        }

    def _handle_end_session(self, session: LearningSession) -> Dict[str, Any]:
        """세션 종료"""
        summary = session_manager.get_session_summary(session.learner_id, session.session_id)

        feedback = f"""👋 수고했어요!

오늘 {summary['total_problems_solved']}개 문제를 풀면서 {len(summary['completed_concepts'])}개 개념을 학습했네요.
{summary['session_duration_minutes']}분 동안 열심히 공부한 모습이 정말 멋져요!

다음에 또 만나요! 🌟"""

        session_manager.update_session_stage(session.learner_id, session.session_id, "completed")

        return {
            "feedback": feedback,
            "is_session_ended": True,
            "session_summary": summary
        }

    def _handle_text_input(self, session: LearningSession, user_input: str) -> Dict[str, Any]:
        """일반 텍스트 입력 처리 - 향상된 의도 분석"""

        # 컨텍스트 정보 구성
        context = {
            "current_stage": session.current_stage,
            "has_current_problem": session.current_problem is not None,
            "current_concept": session.current_concept
        }

        # LLM 기반 의도 분석
        try:
            prompts = self.llm_service.analyze_user_intent(user_input, context)
            response = self.llm_service.call_llm(
                prompts["system"], prompts["user"], session.conversation_history[-4:], "json_object"
            )

            import json
            intent_result = json.loads(response)
            detected_intent = intent_result.get("intent", "general_chat")
            confidence = intent_result.get("confidence", 0.5)

            logging.info(f"Detected intent: {detected_intent} (confidence: {confidence})")

            # 신뢰도가 높은 경우 의도에 따라 처리
            if confidence >= 0.7:
                if detected_intent == "answer_request":
                    return self._handle_answer_reveal_request(session)
                elif detected_intent == "easier_problem":
                    return self._handle_easier_problem(session)
                elif detected_intent == "harder_problem":
                    return self._handle_harder_problem(session)
                elif detected_intent == "different_problem":
                    return self._handle_new_problem_same_concept(session)
                elif detected_intent == "different_concept":
                    return self._handle_next_concept(session)
                elif detected_intent == "concept_explanation":
                    return self._handle_concept_explanation(session)
                elif detected_intent == "session_control":
                    return self._handle_session_summary(session)
                elif detected_intent == "clarification":
                    return self._handle_clarification_request(session, user_input)

        except Exception as e:
            logging.error(f"Intent analysis failed, falling back to original logic: {e}")

        # 기존 로직: 문제 풀이 중이면 정답 시도로 처리
        if session.current_stage == "practice" and session.current_problem:
            # 숫자가 포함된 경우만 정답 시도로 처리
            import re
            if re.search(r'\d', user_input):
                attempt_count = session_manager.increment_attempt(session.learner_id, session.session_id)

                result = self.generated_item_handler.handle(
                    session.current_problem,
                    user_input,
                    session.conversation_history[-6:],
                    session.learner_id,
                    session.current_concept,
                    attempt_count
                )

                # 정답이거나 정답 공개된 경우
                if result.get('is_completed'):
                    session_manager.complete_problem(
                        session.learner_id, session.session_id,
                        not result.get('is_answer_revealed', False)
                    )

                    # 완료 후 선택지 추가
                    result['quick_replies'] = self._get_completion_options(session)

                session_manager.add_conversation(session.learner_id, session.session_id,
                                               "assistant", result['feedback'])
                return result
            else:
                # 숫자가 없으면 일반 대화나 요청으로 처리
                return self._handle_general_conversation(session, user_input)
        else:
            # 일반 대화 처리
            return self._handle_general_conversation(session, user_input)

    def _handle_general_conversation(self, session: LearningSession, user_input: str) -> Dict[str, Any]:
        """일반 대화 처리"""
        response = self.llm_service.call_llm(
            "너는 친근한 AI 수학 튜터야. 학생의 질문에 도움이 되도록 답변하고, 적절한 학습 방향을 제시해줘.",
            user_input,
            session.conversation_history[-6:]
        )

        session_manager.add_conversation(session.learner_id, session.session_id,
                                       "assistant", response)

        return {
            "feedback": response,
            "quick_replies": self._get_general_options(session)
        }

    def _get_practice_options(self, session: LearningSession) -> List[Dict[str, str]]:
        """문제 풀이 중 선택지"""
        return [
            {"text": "힌트 주세요", "action": "text_input", "data": "힌트 주세요"},
            {"text": "개념 설명 듣기", "action": "concept_explanation"},
            {"text": "다른 문제", "action": "new_problem_same_concept"},
            {"text": "다른 개념", "action": "next_concept"}
        ]

    def _get_completion_options(self, session: LearningSession) -> List[Dict[str, str]]:
        """문제 완료 후 선택지"""
        options = [
            {"text": "비슷한 문제 더 풀기", "action": "new_problem_same_concept"},
            {"text": "더 어려운 문제", "action": "harder_problem"}
        ]

        if session_manager.get_next_concept(session.learner_id, session.session_id):
            options.append({"text": "다른 개념 학습", "action": "next_concept"})

        options.extend([
            {"text": "학습 현황 보기", "action": "session_summary"},
            {"text": "오늘 학습 마무리", "action": "end_session"}
        ])

        return options

    def _get_general_options(self, session: LearningSession) -> List[Dict[str, str]]:
        """일반 상황 선택지"""
        return [
            {"text": "문제 풀기", "action": "continue_learning"},
            {"text": "개념 설명", "action": "concept_explanation"},
            {"text": "학습 현황", "action": "session_summary"},
            {"text": "학습 마무리", "action": "end_session"}
        ]

    def _handle_answer_reveal_request(self, session: LearningSession) -> Dict[str, Any]:
        """정답 공개 요청 처리"""
        if not session.current_problem:
            return {"feedback": "현재 풀고 있는 문제가 없습니다."}

        correct_answer = session.current_problem.get("correct_answer", "")
        explanation = session.current_problem.get("explanation", "")

        feedback = f"""📍 정답: {correct_answer}

💡 해설:
{explanation}

이제 이해되었나요? 비슷한 문제를 더 연습해볼까요?"""

        session_manager.complete_problem(session.learner_id, session.session_id, False)

        return {
            "feedback": feedback,
            "quick_replies": self._get_completion_options(session),
            "is_completed": True,
            "is_answer_revealed": True
        }

    def _handle_clarification_request(self, session: LearningSession, user_input: str) -> Dict[str, Any]:
        """명확화 요청 처리"""
        clarification_prompt = f"""사용자가 "{user_input}"라고 했어요.
현재 문제: {session.current_problem.get('new_question_text', '없음') if session.current_problem else '없음'}
현재 개념: {session.current_concept}

사용자가 무엇을 궁금해하는지 파악해서 친절하게 설명해주세요."""

        response = self.llm_service.call_llm(
            "너는 학생의 질문을 이해하고 명확하게 설명해주는 친절한 튜터야.",
            clarification_prompt,
            session.conversation_history[-6:]
        )

        return {
            "feedback": response,
            "quick_replies": self._get_practice_options(session) if session.current_problem else self._get_general_options(session)
        }

    def _handle_start_practice(self, session: LearningSession) -> Dict[str, Any]:
        """진단테스트 후 문제 풀기 시작"""
        return self._handle_continue_learning(session)

    def _handle_explain_concepts(self, session: LearningSession) -> Dict[str, Any]:
        """약한 개념들 설명"""
        if not session.weakest_concepts:
            return {"feedback": "설명할 약한 개념이 없습니다."}

        # 첫 번째 약한 개념 설명
        target_concept = session.weakest_concepts[0]
        explanation_prompt = f"'{target_concept}' 개념을 중학생이 이해하기 쉽게 설명해주세요."

        explanation = self.llm_service.call_llm(
            "너는 중학생에게 수학 개념을 쉽고 친근하게 설명하는 선생님이야.",
            explanation_prompt,
            session.conversation_history[-6:]
        )

        session_manager.add_conversation(session.learner_id, session.session_id,
                                       "assistant", explanation)

        return {
            "feedback": explanation,
            "quick_replies": [
                {"text": "문제 풀기", "action": "start_practice"},
                {"text": "다른 개념 설명", "action": "explain_concepts"},
                {"text": "질문하기", "action": "ask_questions"},
                {"text": "학습 마무리", "action": "end_session"}
            ]
        }

    def _handle_ask_questions(self, session: LearningSession, user_input: str) -> Dict[str, Any]:
        """진단 결과에 대한 질문 처리"""
        if not user_input:
            return {
                "feedback": "진단 결과에 대해 궁금한 점이 있으시면 언제든 물어보세요!",
                "quick_replies": [
                    {"text": "문제 풀기", "action": "start_practice"},
                    {"text": "개념 설명 듣기", "action": "explain_concepts"},
                    {"text": "학습 마무리", "action": "end_session"}
                ]
            }

        # 진단 결과 컨텍스트와 함께 질문 처리
        context_prompt = f"""진단테스트 결과:
- 전체 문제: {session.total_problems_solved if hasattr(session, 'total_problems_solved') else '정보 없음'}개
- 약한 개념: {', '.join(session.weakest_concepts) if session.weakest_concepts else '없음'}

사용자 질문: "{user_input}"

이 질문에 대해 친절하게 답변해주세요."""

        response = self.llm_service.call_llm(
            "너는 진단테스트 결과를 분석하고 학생의 질문에 답하는 친절한 AI 튜터야.",
            context_prompt,
            session.conversation_history[-6:]
        )

        session_manager.add_conversation(session.learner_id, session.session_id,
                                       "assistant", response)

        return {
            "feedback": response,
            "quick_replies": [
                {"text": "문제 풀기", "action": "start_practice"},
                {"text": "개념 설명 듣기", "action": "explain_concepts"},
                {"text": "다시 질문하기", "action": "ask_questions"},
                {"text": "학습 마무리", "action": "end_session"}
            ]
        }

    def _handle_new_diagnosis(self, session: LearningSession) -> Dict[str, Any]:
        """새로운 진단테스트 시작"""
        feedback = """새로운 진단테스트를 시작하려면 새로운 학습자 ID와 세션 ID가 필요합니다.

현재 세션 정보:
- 학습자 ID: {session.learner_id}
- 세션 ID: {session.session_id}

새로운 진단테스트를 원하시면 새로운 learnerID와 session_id로 다시 시작해주세요."""

        return {
            "feedback": feedback,
            "quick_replies": [
                {"text": "현재 세션으로 문제 풀기", "action": "start_practice"},
                {"text": "개념 설명 듣기", "action": "explain_concepts"},
                {"text": "학습 마무리", "action": "end_session"}
            ]
        }