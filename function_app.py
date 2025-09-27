import azure.functions as func
import logging
import json
import os
import pyodbc
import re
from openai import AzureOpenAI

# Function App을 초기화합니다.
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# 학생의 자연어 답변에서 숫자만 추출하는 헬퍼 함수
def extract_answer_from_text(text):
    if not isinstance(text, str):
        text = str(text)
    # 문장에서 숫자(소수점, 음수 포함)를 모두 찾아 리스트로 반환
    numbers = re.findall(r'-?\d+\.?\d*', text)
    if numbers:
        return numbers[0] # 첫 번째로 찾은 숫자를 반환
    return None

# 헬퍼 함수: DB에서 조회한 세션 결과(여러 행)를 LLM이 읽기 쉬운 텍스트로 변환
def format_session_results_for_llm(rows):
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


# Function App을 초기화합니다.
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# 헬퍼 함수: DB에서 조회한 세션 결과(여러 행)를 LLM이 읽기 쉬운 텍스트로 변환
def format_session_results_for_llm(rows):
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

@app.route(route="tutor_api")
def tutor_api(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        request_type = req_body.get("request_type")
        learner_id = req_body.get("learnerID")
        student_message = req_body.get("message", "피드백 요청")
        conversation_history = req_body.get("conversation_history", [])

        if not all([request_type, learner_id]):
            return func.HttpResponse("request_type and learnerID are required.", status_code=400)

        cnxn = pyodbc.connect(os.environ.get("SqlConnectionString"))
        cursor = cnxn.cursor()
        
        system_prompt = ""
        user_prompt = ""

        # --- [기능 1] 세션 전체 결과 분석 ---
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

            total_questions = len(session_rows)
            correct_count = sum(1 for row in session_rows if row[3] == 1)
            wrong_question_numbers = [str(row[0]) for row in session_rows if row[3] == 0]
            weakest_concepts = list(set([row[2] for row in session_rows if row[3] == 0]))

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
            진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.\n\n전체 [전체 문항 수] 문제 중에서 [맞춘 문항 수] 문제를 맞혔네. 정말 잘했어! 👍\n\n이번 테스트에서는 아쉽게도 [틀린 문제 번호 목록] 번 문제를 틀렸더라. 데이터를 분석해보니, 주로 "[보충이 필요한 개념 목록]" 개념들이 조금 헷갈리는 것 같아.\n\n우리 같이 "[보충이 필요한 개념 목록 중 첫 번째 개념]"에 대한 학습을 시작해볼까?
            """

        # --- [기능 2] 개별 문항 피드백 (힌트/코칭/유사문항) ---
        elif request_type == "item_feedback":
            session_id = req_body.get("session_id") # 💡 세션 ID를 받음
            if not session_id:
                return func.HttpResponse("session_id is required for item_feedback.", status_code=400)

            # 💡 [핵심 1] 학생 메시지에서 문제 번호를 숫자로 추출합니다.
            match = re.search(r'\d+', student_message)
            if not match:
                return func.HttpResponse("Could not identify question number from message.", status_code=400)
            question_number = int(match.group(0))

            # 💡 [핵심 2] 문제 번호(seq_in_session)를 사용하여 assessmentItemID를 조회합니다.
            cursor.execute(
                "SELECT assessmentItemID FROM gold.vw_personal_item_enriched WHERE learnerID = ? AND session_id = ? AND seq_in_session = ?",
                learner_id, session_id, question_number
            )
            item_id_row = cursor.fetchone()
            if not item_id_row:
                return func.HttpResponse(f"Could not find question number {question_number} in session {session_id}", status_code=404)
            
            assessment_item_id = item_id_row[0] # 👈 진짜 assessmentItemID 확보!

            # 💡 [핵심 3] 이제 확보된 assessmentItemID로 개인화 정보를 조회합니다.
            query = "SELECT concept_name, tag_accuracy FROM gold.vw_personal_item_enriched WHERE learnerID = ? AND assessmentItemID = ?;"
            cursor.execute(query, learner_id, assessment_item_id)
            personal_info_row = cursor.fetchone()

            if not personal_info_row:
                 return func.HttpResponse(f"Personal info not found for item {assessment_item_id}", status_code=404)

            concept_name, tag_accuracy = personal_info_row

            intent = "feedback_request"
            if "힌트" in student_message or "모르겠어" in student_message:
                intent = "hint_request"
            elif "비슷한 문제" in student_message or "연습 문제" in student_message or "유사 문항" in student_message:
                intent = "similar_item_request"
            
            if intent == "hint_request":
                system_prompt = "너는 정답을 알려주지 않고 다음 단계를 생각하게 만드는 '소크라틱 방식'의 힌트를 제공하는 AI 튜터야."
                user_prompt = f"### 배경 정보\n- 관련 개념: {concept_name}\n- 학생 메시지: \"{student_message}\"\n\n### 임무\n절대 학습 전략이나 긴 격려 메시지를 말하지 말고, 오직 문제 풀이에 도움이 되는 다음 단계 질문을 한두 문장으로 간결하게 제시해."
            
            elif intent == "similar_item_request":
                system_prompt = "너는 학생의 수준에 맞는 새로운 수학 연습 문제를 생성하는 AI야. 반드시 지정된 JSON 형식으로만 답변해야 해."
                user_prompt = f"### 정보\n- 개념: '{concept_name}'\n- 학생의 이 개념 정확도: {tag_accuracy * 100:.1f}%\n\n### 임무\n'{concept_name}' 개념에 대한 새로운 유사 문항을 생성해. 학생의 정확도를 고려하여 너무 어렵지 않게 만들어야 해. 아래 JSON 형식에 맞춰 문제, 정답, 해설을 모두 생성해줘.\n\n### 출력 형식 (JSON)\n{{\"new_question_text\": \"...\", \"correct_answer\": \"...\", \"explanation\": \"...\"}}"
            
            else: # feedback_request
                system_prompt = "너는 학생의 학습 데이터를 분석하고, 개인화된 학습 전략과 격려를 제공하는 전문 AI 학습 코치야."
                user_prompt = f"### 학생 학습 데이터\n- 관련 개념: {concept_name}\n- 학생의 해당 개념 정확도: {tag_accuracy * 100:.1f}%\n\n### 너의 임무\n위 데이터를 '해석'해서, 학생에게 격려 메시지와 구체적인 학습 전략을 요약해줘."

        # --- [기능 3] 생성된 문항 채점 ---
        elif request_type == "check_generated_answer":
            student_answer_text = req_body.get("student_answer")
            generated_question_data = req_body.get("generated_question_data")

            if not generated_question_data:
                return func.HttpResponse("generated_question_data is required.", status_code=400)

            correct_answer = generated_question_data.get("correct_answer")
            explanation = generated_question_data.get("explanation")
            
            student_answer_num = extract_answer_from_text(student_answer_text)
            is_correct = False
            try:
                if student_answer_num is not None and float(student_answer_num) == float(correct_answer):
                    is_correct = True
            except (ValueError, TypeError):
                is_correct = False

            if is_correct:
                ai_feedback = "정답이야! 이 개념을 완벽하게 이해했네. 훌륭해! 👍"
            else:
                ai_feedback = f"아쉽지만 틀렸어. 정답은 '{correct_answer}'이야.\n\n자세한 해설은 다음과 같아:\n{explanation}"
            
            conversation_history.append({"role": "user", "content": f"내 답은 {student_answer_text}이야."})
            conversation_history.append({"role": "assistant", "content": ai_feedback})
            final_response = { "feedback": ai_feedback, "conversation_history": conversation_history }
            return func.HttpResponse(json.dumps(final_response, ensure_ascii=False), mimetype="application/json")

        else:
            return func.HttpResponse("Invalid request_type.", status_code=400)

        # --- 공통 LLM 호출 ---
        cnxn.close()
        client = AzureOpenAI(
            api_key=os.environ.get("OpenApiKey"),
            azure_endpoint=os.environ.get("OpenAIEndpoint"),
            api_version="2023-05-15"
        )
        
        # 'similar_item_request'일 경우에만 response_format을 json_object로 설정
        response_format_config = {"type": "text"}
        if 'intent' in locals() and intent == "similar_item_request":
            response_format_config = {"type": "json_object"}

        messages_to_send = [{"role": "system", "content": system_prompt}] + conversation_history
        messages_to_send.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send,
            response_format=response_format_config
        )
        
        # --- 최종 응답 생성 ---
        # 'intent' 변수가 item_feedback 블록 내에서만 정의되므로, 여기서도 확인
        if 'intent' in locals() and intent == "similar_item_request":
            generated_data = json.loads(response.choices[0].message.content)
            ai_feedback = f"좋아! '{concept_name}' 개념을 더 연습해볼까? 아래 문제를 풀어봐.\n\n{generated_data.get('new_question_text')}"
            final_response_data = {
                "feedback": ai_feedback,
                "generated_question_data": generated_data 
            }
        else:
            ai_feedback = response.choices[0].message.content
            final_response_data = { "feedback": ai_feedback }
        
        conversation_history.append({"role": "user", "content": student_message})
        conversation_history.append({"role": "assistant", "content": ai_feedback})
        final_response_data["conversation_history"] = conversation_history
        
        return func.HttpResponse(json.dumps(final_response_data, ensure_ascii=False), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

