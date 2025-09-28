import logging
from typing import Dict, Any
from database.db_service import DatabaseService
from services.llm_service import LLMService


class SessionHandler:
    """세션 요약 처리 핸들러"""

    def __init__(self):
        self.db_service = DatabaseService()
        self.llm_service = LLMService()

    def handle(self, learner_id: str, session_id: str, conversation_history: list) -> Dict[str, Any]:
        """세션 요약 처리"""
        try:
            # 세션 결과 조회
            session_rows = self.db_service.get_session_results(learner_id, session_id)

            if not session_rows:
                raise ValueError(f"No data found for session {session_id}")

            # Python 코드에서 사실 관계를 미리 계산하여 LLM의 오류 가능성을 원천 차단
            total_questions = len(session_rows)
            correct_count = sum(1 for row in session_rows if row[3] == 1)
            wrong_question_numbers = [str(row[0]) for row in session_rows if row[3] == 0]
            weakest_concepts = list(set([row[2] for row in session_rows if row[3] == 0]))

            # 프롬프트 생성
            prompts = self.llm_service.generate_session_summary_prompt(
                total_questions, correct_count, wrong_question_numbers, weakest_concepts
            )

            # LLM 호출
            ai_feedback = self.llm_service.call_llm(
                prompts["system"], prompts["user"], conversation_history
            )

            return {
                "feedback": ai_feedback,
                "weakest_concepts": weakest_concepts,  # 보충이 필요한 개념 목록 추가
                "total_questions": total_questions,
                "correct_count": correct_count,
                "quick_replies": [
                    {"text": "문제 풀기", "action": "start_practice"},
                    {"text": "개념 설명 듣기", "action": "explain_concepts"},
                    {"text": "질문하기", "action": "ask_questions"},
                    {"text": "다른 진단테스트", "action": "new_diagnosis"},
                    {"text": "학습 마무리", "action": "end_session"}
                ]
            }

        except Exception as e:
            logging.error(f"Session handler error: {e}")
            raise