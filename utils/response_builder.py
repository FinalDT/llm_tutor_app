import json
from typing import Dict, Any, List
import azure.functions as func


class ResponseBuilder:
    """HTTP 응답 생성 유틸리티"""

    @staticmethod
    def build_success_response(data: Dict[str, Any], conversation_history: List[Dict[str, str]],
                             student_message: str) -> func.HttpResponse:
        """성공 응답 생성"""
        # conversation_history 업데이트
        conversation_history.append({"role": "user", "content": student_message})
        conversation_history.append({"role": "assistant", "content": data.get("feedback", "")})

        # 최종 응답 데이터 구성
        final_response_data = data.copy()
        final_response_data["conversation_history"] = conversation_history

        return func.HttpResponse(
            json.dumps(final_response_data, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    @staticmethod
    def build_error_response(message: str, status_code: int = 400) -> func.HttpResponse:
        """에러 응답 생성"""
        return func.HttpResponse(
            json.dumps({"error": message}, ensure_ascii=False),
            mimetype="application/json",
            status_code=status_code
        )

    @staticmethod
    def build_validation_error_response(missing_fields: List[str]) -> func.HttpResponse:
        """유효성 검사 에러 응답 생성"""
        message = f"Required fields are missing: {', '.join(missing_fields)}"
        return ResponseBuilder.build_error_response(message, 400)

    @staticmethod
    def build_internal_error_response(error: Exception) -> func.HttpResponse:
        """내부 서버 에러 응답 생성"""
        return ResponseBuilder.build_error_response(str(error), 500)