import pyodbc
import logging
from typing import List, Tuple, Optional
from config.settings import settings


class DatabaseService:
    """데이터베이스 연결 및 쿼리 서비스"""

    def __init__(self):
        self.connection_string = settings.sql_connection_string

    def get_connection(self) -> pyodbc.Connection:
        """데이터베이스 연결 생성"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def get_session_results(self, learner_id: str, session_id: str) -> List[Tuple]:
        """세션 결과 조회"""
        query = """
        SELECT seq_in_session, assessmentItemID, concept_name, is_correct,
               tag_accuracy, global_accuracy, personal_vs_global_delta
        FROM gold.vw_personal_item_enriched
        WHERE learnerID = ? AND session_id = ?
        ORDER BY seq_in_session;
        """

        with self.get_connection() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(query, learner_id, session_id)
            return cursor.fetchall()

    def get_assessment_item_id(self, learner_id: str, session_id: str, question_number: int) -> Optional[str]:
        """문제 번호로 평가 아이템 ID 조회"""
        query = """
        SELECT assessmentItemID
        FROM gold.vw_personal_item_enriched
        WHERE learnerID = ? AND session_id = ? AND seq_in_session = ?
        """

        with self.get_connection() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(query, learner_id, session_id, question_number)
            row = cursor.fetchone()
            return row[0] if row else None

    def get_personal_info(self, learner_id: str, assessment_item_id: str) -> Optional[Tuple[str, float]]:
        """개인 학습 정보 조회"""
        query = """
        SELECT concept_name, tag_accuracy
        FROM gold.vw_personal_item_enriched
        WHERE learnerID = ? AND assessmentItemID = ?
        """

        with self.get_connection() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(query, learner_id, assessment_item_id)
            row = cursor.fetchone()
            return (row[0], row[1]) if row else None

    @staticmethod
    def format_session_results_for_llm(rows: List[Tuple]) -> str:
        """DB 조회 결과를 LLM이 읽기 쉬운 텍스트로 변환"""
        summary = []
        # 쿼리 순서: 0:seq, 1:itemID, 2:concept, 3:is_correct, 4:tag_accuracy, 5:global_accuracy, 6:delta
        for row in rows:
            result = "정답" if row[3] == 1 else "오답"
            summary.append(
                f"- {row[0]}번 문항 ({row[2]}): {result}, "
                f"학생의 이 개념 정답률은 {row[4]*100:.1f}%, "
                f"전체 평균 대비 {abs(row[6])*100:.1f}%p {'높음' if row[6] >= 0 else '낮음'}"
            )
        return "\n".join(summary)