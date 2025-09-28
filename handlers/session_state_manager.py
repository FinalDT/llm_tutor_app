from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class LearningSession:
    """학습 세션 상태 관리"""
    learner_id: str
    session_id: str
    current_stage: str = "diagnosis"  # diagnosis, practice, hint, completed
    current_concept: Optional[str] = None
    weakest_concepts: List[str] = field(default_factory=list)
    completed_concepts: List[str] = field(default_factory=list)
    current_problem: Optional[Dict[str, Any]] = None
    attempt_count: int = 0
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    learning_progress: Dict[str, Any] = field(default_factory=dict)
    session_start_time: datetime = field(default_factory=datetime.now)
    last_activity_time: datetime = field(default_factory=datetime.now)
    total_problems_solved: int = 0
    total_hints_used: int = 0


class SessionStateManager:
    """세션 상태 관리자"""

    def __init__(self):
        self.active_sessions: Dict[str, LearningSession] = {}

    def create_session(self, learner_id: str, session_id: str, weakest_concepts: List[str]) -> LearningSession:
        """새 학습 세션 생성"""
        session_key = f"{learner_id}_{session_id}"

        session = LearningSession(
            learner_id=learner_id,
            session_id=session_id,
            weakest_concepts=weakest_concepts,
            current_concept=weakest_concepts[0] if weakest_concepts else None
        )

        self.active_sessions[session_key] = session
        return session

    def get_session(self, learner_id: str, session_id: str) -> Optional[LearningSession]:
        """세션 조회"""
        session_key = f"{learner_id}_{session_id}"
        return self.active_sessions.get(session_key)

    def update_session_stage(self, learner_id: str, session_id: str, stage: str):
        """학습 단계 업데이트"""
        session = self.get_session(learner_id, session_id)
        if session:
            session.current_stage = stage
            session.last_activity_time = datetime.now()

    def start_new_problem(self, learner_id: str, session_id: str, problem_data: Dict[str, Any]):
        """새 문제 시작"""
        session = self.get_session(learner_id, session_id)
        if session:
            session.current_problem = problem_data
            session.attempt_count = 0
            session.current_stage = "practice"

    def increment_attempt(self, learner_id: str, session_id: str) -> int:
        """시도 횟수 증가"""
        session = self.get_session(learner_id, session_id)
        if session:
            session.attempt_count += 1
            return session.attempt_count
        return 0

    def complete_problem(self, learner_id: str, session_id: str, success: bool):
        """문제 완료 처리"""
        session = self.get_session(learner_id, session_id)
        if session:
            session.total_problems_solved += 1
            if success and session.current_concept:
                # 성공한 개념을 완료 목록에 추가
                if session.current_concept not in session.completed_concepts:
                    session.completed_concepts.append(session.current_concept)

    def get_next_concept(self, learner_id: str, session_id: str) -> Optional[str]:
        """다음 학습할 개념 반환"""
        session = self.get_session(learner_id, session_id)
        if not session:
            return None

        # 아직 완료하지 않은 취약 개념 찾기
        remaining_concepts = [
            concept for concept in session.weakest_concepts
            if concept not in session.completed_concepts
        ]

        return remaining_concepts[0] if remaining_concepts else None

    def get_session_summary(self, learner_id: str, session_id: str) -> Dict[str, Any]:
        """세션 요약 정보"""
        session = self.get_session(learner_id, session_id)
        if not session:
            return {}

        duration = (datetime.now() - session.session_start_time).total_seconds() / 60

        return {
            "total_problems_solved": session.total_problems_solved,
            "total_hints_used": session.total_hints_used,
            "completed_concepts": session.completed_concepts,
            "remaining_concepts": [
                c for c in session.weakest_concepts
                if c not in session.completed_concepts
            ],
            "session_duration_minutes": round(duration, 1),
            "current_stage": session.current_stage
        }

    def add_conversation(self, learner_id: str, session_id: str, role: str, content: str):
        """대화 히스토리 추가"""
        session = self.get_session(learner_id, session_id)
        if session:
            session.conversation_history.append({"role": role, "content": content})
            # 히스토리가 너무 길어지면 앞부분 제거 (최근 20개만 유지)
            if len(session.conversation_history) > 20:
                session.conversation_history = session.conversation_history[-20:]


# 전역 세션 매니저 인스턴스
session_manager = SessionStateManager()