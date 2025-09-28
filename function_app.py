import azure.functions as func
import logging
from handlers.session_handler import SessionHandler
from handlers.feedback_handler import FeedbackHandler
from handlers.generated_item_handler import GeneratedItemHandler
from utils.response_builder import ResponseBuilder

# Function App을 초기화합니다.
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="tutor_api")
def tutor_api(req: func.HttpRequest) -> func.HttpResponse:
    """LLM 튜터 API 메인 엔드포인트"""
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # 요청 데이터 파싱
        req_body = req.get_json()
        request_type = req_body.get("request_type")
        learner_id = req_body.get("learnerID")
        student_message = req_body.get("message", "피드백 요청")
        conversation_history = req_body.get("conversation_history", [])

        # 필수 필드 검증 (generated_item은 learnerID 불필요)
        if not request_type:
            return ResponseBuilder.build_validation_error_response(["request_type"])
        
        if request_type != "generated_item" and not learner_id:
            return ResponseBuilder.build_validation_error_response(["learnerID"])

        # 요청 타입별 처리
        if request_type == "session_summary":
            session_id = req_body.get("session_id")
            if not session_id:
                return ResponseBuilder.build_validation_error_response(["session_id"])

            handler = SessionHandler()
            result = handler.handle(learner_id, session_id, conversation_history)

        elif request_type == "item_feedback":
            session_id = req_body.get("session_id")
            if not session_id:
                return ResponseBuilder.build_validation_error_response(["session_id"])

            handler = FeedbackHandler()
            result = handler.handle(learner_id, session_id, student_message, conversation_history)

        elif request_type == "generated_item":
            generated_question_data = req_body.get("generated_question_data")
            if not generated_question_data:
                return ResponseBuilder.build_validation_error_response(["generated_question_data"])

            # 개인화 정보 추출 (선택적)
            original_concept = req_body.get("original_concept")

            handler = GeneratedItemHandler()
            result = handler.handle(
                generated_question_data,
                student_message,
                conversation_history,
                learner_id,  # learner_id 전달 (선택적)
                original_concept  # 원본 개념 전달 (선택적)
            )

        else:
            return ResponseBuilder.build_error_response("Invalid request_type.")

        # 성공 응답 반환
        return ResponseBuilder.build_success_response(result, conversation_history, student_message)

    except Exception as e:
        logging.error(f"Error: {e}")
        return ResponseBuilder.build_internal_error_response(e)
