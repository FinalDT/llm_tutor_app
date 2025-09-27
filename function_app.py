import azure.functions as func
import logging
import json
import os
import pyodbc
import re
from openai import AzureOpenAI

# Initialize the Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Helper function: Converts DB query results (multiple rows) into a text summary for the LLM
def format_session_results_for_llm(rows):
    """
    Formats the detailed session results from the database into a readable text summary
    for the LLM prompt.
    """
    summary = []
    # Query order: 0:seq, 1:itemID, 2:concept, 3:is_correct, 4:tag_accuracy, 5:global_accuracy, 6:delta
    for row in rows:
        result = "정답" if row[3] == 1 else "오답"
        summary.append(
            f"- {row[0]}번 문항 ({row[2]}): {result}, "
            f"학생의 이 개념 정답률은 {row[4]*100:.1f}%, "
            f"전체 평균 대비 {abs(row[6])*100:.1f}%p {'높음' if row[6] >= 0 else '낮음'}"
        )
    return "\n".join(summary)

@app.route(route="tutor_api")
def tutor_api(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main API endpoint that handles different request types for the AI Tutor.
    """
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # --- 1. Parse Client Request ---
        req_body = req.get_json()
        request_type = req_body.get("request_type")
        learner_id = req_body.get("learnerID")
        student_message = req_body.get("message", "피드백 요청")
        conversation_history = req_body.get("conversation_history", [])

        if not all([request_type, learner_id]):
            return func.HttpResponse(
                json.dumps({"error": "request_type and learnerID are required."}),
                status_code=400, mimetype="application/json"
            )

        cnxn = pyodbc.connect(os.environ.get("SqlConnectionString"))
        cursor = cnxn.cursor()
        
        system_prompt = ""
        user_prompt = ""

        # --- [Feature 1] Session Summary Analysis ---
        if request_type == "session_summary":
            session_id = req_body.get("session_id")
            if not session_id:
                return func.HttpResponse("session_id is required for session_summary.", status_code=400)

            query = """
            SELECT seq_in_session, assessmentItemID, concept_name, is_correct, 
                   tag_accuracy, global_accuracy, personal_vs_global_delta
            FROM gold.vw_personal_item_enriched
            WHERE learnerID = ? AND session_id = ?
            ORDER BY seq_in_session;
            """
            cursor.execute(query, learner_id, session_id)
            session_rows = cursor.fetchall()

            if not session_rows:
                return func.HttpResponse(f"No data found for session {session_id}", status_code=404)
            
            # Use Python code to get the facts straight for the LLM
            total_questions = len(session_rows)
            correct_count = sum(1 for row in session_rows if row[3] == 1)
            wrong_question_numbers = [str(row[0]) for row in session_rows if row[3] == 0]
            weakest_concepts = list(set([row[2] for row in session_rows if row[3] == 0]))

            system_prompt = "너는 학생의 진단 테스트 결과를 정확한 데이터에 기반하여 요약하고 전달하는 AI 어시스턴트야."
            user_prompt = f"""
            ### 🚨 너의 임무 (Your Task)
            너는 아래 "배경 데이터"를 **그대로 읽어서** "출력 형식"에 맞춰 문장을 완성해야 해.
            **절대로 [데이터]에 없는 내용을 추측하거나 지어내면 안 돼.**

            ### [배경 데이터]
            - 전체 문항 수: {total_questions}
            - 맞춘 문항 수: {correct_count}
            - 틀린 문제 번호 목록: {', '.join(wrong_question_numbers)}
            - 보충이 필요한 개념 목록: {', '.join(weakest_concepts)}

            ### [출력 형식]
            진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.
            전체 **[전체 문항 수]** 문제 중에서 **[맞춘 문항 수]** 문제를 맞혔네. 정말 잘했어! 👍
            이번 테스트에서는 아쉽게도 **[틀린 문제 번호 목록]** 번 문제를 틀렸더라. 데이터를 분석해보니, 주로 **"[보충이 필요한 개념 목록]"** 개념들이 조금 헷갈리는 것 같아.
            우리 같이 **"[보충이 필요한 개념 목록 중 첫 번째 개념]"** 에 대한 학습을 시작해볼까?
            """

        # --- [Feature 2] Individual Item Feedback (Hint, Coaching, Similar Items) ---
        elif request_type == "item_feedback":
            session_id = req_body.get("session_id") # Required to find the correct assessmentItemID
            if not session_id:
                return func.HttpResponse("session_id is required for item_feedback.", status_code=400)

            # Extract question number from student's message (e.g., "1번 문제")
            match = re.search(r'\d+', student_message)
            if not match:
                return func.HttpResponse("Could not identify question number from message.", status_code=400)
            question_number = int(match.group(0))

            # Find the actual assessmentItemID using the question number
            cursor.execute(
                "SELECT assessmentItemID FROM gold.vw_personal_item_enriched WHERE learnerID = ? AND session_id = ? AND seq_in_session = ?",
                learner_id, session_id, question_number
            )
            item_id_row = cursor.fetchone()
            if not item_id_row:
                return func.HttpResponse(f"Could not find question number {question_number} in session {session_id}", status_code=404)
            
            assessment_item_id = item_id_row[0]

            # Now, fetch the detailed performance data for that specific item
            query = "SELECT concept_name, tag_accuracy, global_accuracy, personal_vs_global_delta, recommended_level FROM gold.vw_personal_item_enriched WHERE learnerID = ? AND assessmentItemID = ?;"
            cursor.execute(query, learner_id, assessment_item_id)
            personal_info_row = cursor.fetchone()

            if not personal_info_row:
                return func.HttpResponse(f"Personal info not found for item {assessment_item_id}", status_code=404)

            concept_name, tag_accuracy, global_accuracy, delta, rec_level = personal_info_row

            # Intent detection
            intent = "feedback_request"
            if "힌트" in student_message or "모르겠어" in student_message:
                intent = "hint_request"
            elif "비슷한 문제" in student_message or "연습 문제" in student_message or "유사 문항" in student_message:
                intent = "similar_item_request"
            
            # Branching logic based on intent
            if intent == "hint_request":
                system_prompt = "너는 학생의 질문에 대해, 정답을 알려주지 않고 다음 단계를 생각하게 만드는 '소크라틱 방식'의 힌트를 제공하는 AI 튜터야."
                user_prompt = f"""
                ### 배경 정보 (참고용)
                - 관련 개념: {concept_name}
                - 학생 메시지: "{student_message}"
                ### 임무 수행 가이드
                1. 절대로 학습 전략이나 긴 격려 메시지를 말하지 마.
                2. 오직 문제를 푸는 데 도움이 되는 핵심적인 다음 단계 질문을 한두 문장으로 간결하게 제시해.
                """
            elif intent == "similar_item_request":
                # This logic assumes you have the mapping table and dbo.questions_dim available
                # If not, this part needs to be adapted
                system_prompt = "너는 학생에게 수준에 맞는 연습 문제를 추천해주는 AI 튜터야."
                user_prompt = f"""
                ### 너의 임무
                '{concept_name}' 개념에 대한 새로운 연습 문제를 **직접 생성**해줘. 
                문제는 현재 학생의 수준(정답률: {tag_accuracy*100:.1f}%)을 고려하여 너무 어렵지 않게 만들어줘.
                문제 텍스트만 깔끔하게 제공해.
                """
            else: # feedback_request
                system_prompt = "너는 학생의 학습 데이터를 분석하고, 개인화된 학습 전략과 격려를 제공하는 전문 AI 학습 코치야."
                user_prompt = f"""
                ### 학생 학습 데이터
                - 관련 개념: {concept_name}
                - 이 학생의 해당 개념 정확도: {tag_accuracy * 100:.1f}%
                - 전체 학생 평균 정확도: {global_accuracy * 100:.1f}%
                - 평균 대비 성과: {abs(delta) * 100:.1f}%p 만큼 {'높은' if delta >= 0 else '낮은'} 성과
                - 추천 학습 수준: {rec_level}
                ### 너의 임무
                위 데이터를 '해석'해서, 학생에게 격려 메시지와 구체적인 학습 전략을 요약해줘.
                """
        else:
            return func.HttpResponse("Invalid request_type.", status_code=400)

        # --- Common LLM Call and Response Handling ---
        cnxn.close()
        client = AzureOpenAI(
            api_key=os.environ.get("OpenApiKey"),
            azure_endpoint=os.environ.get("OpenAIEndpoint"),
            api_version="2023-05-15"
        )
        
        messages_to_send = [{"role": "system", "content": system_prompt}] + conversation_history
        messages_to_send.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send
        )
        ai_feedback = response.choices[0].message.content
        
        conversation_history.append({"role": "user", "content": student_message})
        conversation_history.append({"role": "assistant", "content": ai_feedback})

        final_response = { 
            "feedback": ai_feedback,
            "conversation_history": conversation_history
        }
        return func.HttpResponse(json.dumps(final_response, ensure_ascii=False), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

