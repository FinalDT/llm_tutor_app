import logging
from typing import Dict, Any, Optional
from database.db_service import DatabaseService
from services.llm_service import LLMService


class GeneratedItemHandler:
    """생성된 문항 힌트 처리 핸들러"""

    def __init__(self):
        self.db_service = DatabaseService()
        self.llm_service = LLMService()

    def handle(self, generated_question_data: Dict[str, Any], student_message: str,
              conversation_history: list, learner_id: Optional[str] = None,
              original_concept: Optional[str] = None, attempt_count: Optional[int] = None) -> Dict[str, Any]:
        """생성된 문항 힌트 처리"""
        try:
            question_text = generated_question_data.get("new_question_text")
            correct_answer = generated_question_data.get("correct_answer", "")
            if not question_text:
                raise ValueError("Generated question text not found")

            # 3번 시도 후에는 정답 공개
            if attempt_count and attempt_count > 3:
                return self._handle_answer_reveal(generated_question_data, attempt_count)

            # 정답 판단 먼저 수행
            answer_analysis = self._analyze_student_answer(student_message, correct_answer, question_text)

            logging.info(f"Answer analysis: {answer_analysis}")

            # 정답인 경우 축하 메시지 반환
            if answer_analysis["is_correct"]:
                return self._handle_correct_answer(answer_analysis, generated_question_data, personalization_data if 'personalization_data' in locals() else {})

            # 개인화 정보 수집 (정답이 아닌 경우에만)
            personalization_data = self._get_personalization_data(
                learner_id, original_concept, generated_question_data
            )

            logging.info(f"Personalization data: {personalization_data}")

            # 부분 정답이나 접근 방법이 맞는 경우 특별 처리
            if answer_analysis["is_partial_correct"] or answer_analysis["has_good_approach"]:
                return self._handle_partial_answer(answer_analysis, question_text, student_message, personalization_data, conversation_history)

            # 일반 힌트 제공 (기존 로직)
            prompts = self.llm_service.generate_personalized_hint_prompt(
                question_text, student_message, personalization_data
            )

            # LLM 호출
            ai_feedback = self.llm_service.call_llm(
                prompts["system"], prompts["user"], conversation_history
            )

            # 힌트 품질 분석
            hint_analysis = self._analyze_hint_quality(ai_feedback, personalization_data)

            return {
                "feedback": ai_feedback,
                "personalization_info": personalization_data,
                "hint_analysis": hint_analysis,
                "answer_analysis": answer_analysis
            }

        except Exception as e:
            logging.error(f"Generated item handler error: {e}")
            raise

    def _get_personalization_data(self, learner_id: Optional[str],
                                original_concept: Optional[str],
                                generated_question_data: Dict[str, Any]) -> Dict[str, Any]:
        """개인화 데이터 수집"""
        personalization_data = {
            "learner_id": learner_id,
            "original_concept": original_concept,
            "question_difficulty": "medium",  # 기본값
            "personal_accuracy": None,
            "hint_level": "beginner",
            "learning_style": "step_by_step"
        }

        # learner_id가 있고 original_concept이 있는 경우 개인 데이터 조회
        if learner_id and original_concept:
            try:
                # 개념별 개인 정확도 조회 (가장 최근 학습 기록)
                # 실제로는 더 복잡한 쿼리가 필요하지만, 기본 구조 제공
                personal_accuracy = self._get_concept_accuracy(learner_id, original_concept)
                if personal_accuracy is not None:
                    personalization_data["personal_accuracy"] = personal_accuracy
                    personalization_data["hint_level"] = self._determine_hint_level(personal_accuracy)

                logging.info(f"Personal accuracy for {original_concept}: {personal_accuracy}")

            except Exception as e:
                logging.warning(f"Could not fetch personalization data: {e}")

        return personalization_data

    def _get_concept_accuracy(self, learner_id: str, concept_name: str) -> Optional[float]:
        """개념별 개인 정확도 조회"""
        try:
            # 해당 개념의 최근 학습 기록에서 정확도 조회
            # 이는 간단한 구현이며, 실제로는 더 정교한 로직 필요
            query = """
            SELECT TOP 1 tag_accuracy
            FROM gold.vw_personal_item_enriched
            WHERE learnerID = ? AND concept_name = ?
            ORDER BY session_id DESC
            """

            with self.db_service.get_connection() as cnxn:
                cursor = cnxn.cursor()
                cursor.execute(query, learner_id, concept_name)
                row = cursor.fetchone()
                return row[0] if row else None

        except Exception as e:
            logging.warning(f"Error fetching concept accuracy: {e}")
            return None

    def _determine_hint_level(self, accuracy: float) -> str:
        """정확도 기반 힌트 레벨 결정"""
        if accuracy >= 0.8:
            return "advanced"  # 고급 - 간단한 힌트
        elif accuracy >= 0.5:
            return "intermediate"  # 중급 - 중간 수준 힌트
        else:
            return "beginner"  # 초급 - 상세한 힌트

    def _analyze_hint_quality(self, hint: str, personalization_data: Dict[str, Any]) -> Dict[str, Any]:
        """힌트 품질 분석"""
        analysis = {
            "is_socratic": "?" in hint and "정답은" not in hint,
            "hint_length": len(hint),
            "contains_encouragement": any(word in hint for word in ["좋아", "잘", "훌륭"]),
            "difficulty_appropriate": True,  # 실제로는 더 복잡한 분석 필요
            "personalization_level": "basic" if not personalization_data.get("personal_accuracy") else "personalized"
        }

        # 힌트 레벨에 따른 적절성 체크
        hint_level = personalization_data.get("hint_level", "beginner")
        if hint_level == "beginner" and len(hint) < 20:
            analysis["difficulty_appropriate"] = False
            analysis["recommendation"] = "초급 학습자에게는 더 상세한 힌트가 필요합니다"
        elif hint_level == "advanced" and len(hint) > 100:
            analysis["difficulty_appropriate"] = False
            analysis["recommendation"] = "고급 학습자에게는 더 간결한 힌트가 적합합니다"

        return analysis

    def _analyze_student_answer(self, student_message: str, correct_answer: str, question_text: str) -> Dict[str, Any]:
        """학생 답안 분석"""
        import re

        # 기본 분석 결과
        analysis = {
            "is_correct": False,
            "is_partial_correct": False,
            "has_good_approach": False,
            "confidence": 0.0,
            "student_answer": student_message,
            "correct_answer": correct_answer,
            "feedback_type": "hint_needed"
        }

        # 힌트 요청인지 확인
        hint_keywords = ["힌트", "모르겠", "도와", "어떻게", "방법", "help", "hint"]
        if any(keyword in student_message.lower() for keyword in hint_keywords):
            analysis["feedback_type"] = "hint_request"
            return analysis

        # 정답에서 숫자와 단위 추출
        correct_numbers = re.findall(r'\d+(?:\.\d+)?', correct_answer)
        correct_units = re.findall(r'[a-zA-Z²³°]+', correct_answer)

        # 학생 답안에서 숫자와 단위 추출
        student_numbers = re.findall(r'\d+(?:\.\d+)?', student_message)
        student_units = re.findall(r'[a-zA-Z²³°]+', student_message)

        # 완전 정답 판단
        if correct_numbers and student_numbers:
            # 정답에서 가능한 모든 숫자와 학생 답안 비교
            for correct_num in correct_numbers:
                for student_num in student_numbers:
                    if correct_num == student_num:
                        # 숫자만 맞아도 정답으로 인정 (태블릿 환경 고려)
                        analysis["is_correct"] = True
                        analysis["confidence"] = 1.0
                        analysis["feedback_type"] = "correct_answer"

                        # 단위까지 맞으면 완벽한 정답
                        if correct_units and student_units:
                            if any(unit in student_message for unit in correct_units):
                                analysis["confidence"] = 1.0  # 완벽
                            else:
                                analysis["confidence"] = 0.9  # 단위 없지만 정답
                        else:
                            analysis["confidence"] = 0.9  # 단위 없지만 정답

                        return analysis

        # 부분 정답 판단 (접근 방법 분석)
        approach_keywords = {
            "각기둥": ["밑면", "옆면", "겉넓이", "넓이", "더하기", "+"],
            "원뿔": ["밑면", "옆면", "부채꼴", "반지름"],
            "부채꼴": ["호의길이", "반지름", "중심각", "넓이"]
        }

        for concept, keywords in approach_keywords.items():
            if concept in question_text:
                if any(keyword in student_message for keyword in keywords):
                    analysis["has_good_approach"] = True
                    analysis["confidence"] = 0.6
                    break

        # 계산 과정이 보이는 경우
        if "×" in student_message or "*" in student_message or "=" in student_message:
            analysis["has_good_approach"] = True
            analysis["confidence"] = max(analysis["confidence"], 0.4)

        return analysis

    def _handle_correct_answer(self, answer_analysis: Dict[str, Any],
                             generated_question_data: Dict[str, Any],
                             personalization_data: Dict[str, Any]) -> Dict[str, Any]:
        """정답 처리"""

        congratulation_messages = [
            "🎉 정답입니다! 정말 훌륭해요!",
            "✨ 맞았어요! 각기둥의 겉넓이를 완벽하게 구했네요!",
            "👏 대단해요! 밑면과 옆면의 넓이를 모두 고려해서 정답을 구했어요!",
            "🌟 완벽합니다! 수학 실력이 많이 늘었네요!"
        ]

        import random
        congratulation = random.choice(congratulation_messages)

        # 학습 완료 피드백
        completion_feedback = f"""{congratulation}

📊 해결 과정 분석:
• 정답: {answer_analysis['correct_answer']}
• 학생 답안: {answer_analysis['student_answer']}
• 정확도: {answer_analysis['confidence']*100:.0f}%

🎯 이번 문제를 통해 '{generated_question_data.get('explanation', '개념')}' 을 잘 이해했어요!

💡 다음 단계: 비슷한 다른 도형의 겉넓이 문제도 도전해보시겠어요?"""

        return {
            "feedback": completion_feedback,
            "personalization_info": personalization_data,
            "answer_analysis": answer_analysis,
            "is_completed": True,
            "next_suggestion": "similar_concept_practice"
        }

    def _handle_partial_answer(self, answer_analysis: Dict[str, Any], question_text: str,
                             student_message: str, personalization_data: Dict[str, Any],
                             conversation_history: list) -> Dict[str, Any]:
        """부분 정답 또는 좋은 접근 방법 처리"""

        if answer_analysis["is_partial_correct"]:
            encouragement = "🎯 숫자는 맞았어요! 하지만 단위를 확인해보세요."
        else:
            encouragement = "👍 접근 방법이 좋아요! 계속 그 방향으로 생각해보세요."

        # 개선된 힌트 프롬프트 생성
        prompts = self.llm_service.generate_guided_hint_prompt(
            question_text, student_message, answer_analysis, personalization_data
        )

        # LLM 호출
        ai_feedback = self.llm_service.call_llm(
            prompts["system"], prompts["user"], conversation_history
        )

        # 격려 메시지와 AI 힌트 결합
        combined_feedback = f"{encouragement}\n\n{ai_feedback}"

        return {
            "feedback": combined_feedback,
            "personalization_info": personalization_data,
            "answer_analysis": answer_analysis,
            "hint_analysis": {"is_guided_hint": True, "encouragement_included": True}
        }

    def _handle_answer_reveal(self, generated_question_data: Dict[str, Any], attempt_count: int) -> Dict[str, Any]:
        """3번 시도 후 정답 공개"""
        correct_answer = generated_question_data.get("correct_answer", "")
        explanation = generated_question_data.get("explanation", "")

        reveal_feedback = f"""🎯 {attempt_count-1}번의 시도로 충분히 노력했어요! 이제 정답을 알려드릴게요.

📍 정답: {correct_answer}

💡 해설:
{explanation}

🌟 이 문제를 통해 개념을 잘 이해했으니, 다음에는 더 쉽게 풀 수 있을 거예요!
다시 한 번 비슷한 문제에 도전해보시겠어요?"""

        return {
            "feedback": reveal_feedback,
            "is_completed": True,
            "is_answer_revealed": True,
            "attempt_count": attempt_count - 1,
            "answer_analysis": {
                "is_correct": False,
                "feedback_type": "answer_revealed",
                "student_answer": "시도 횟수 초과",
                "correct_answer": correct_answer
            }
        }