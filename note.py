import os
import json
import logging
from openai import AzureOpenAI
 
 
def get_openai_client():
    """Azure OpenAI 클라이언트 초기화"""
    return AzureOpenAI(
        api_key=os.environ["AOAI_KEY"],
        api_version="2024-02-01",
        azure_endpoint=os.environ["AOAI_ENDPOINT"]
    )
 
 
def test_ai_connection():
    """AI 연결 테스트"""
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=os.environ["AOAI_DEPLOYMENT"],
            messages=[
                {"role": "user", "content": "Hello, this is a connection test."}
            ],
            max_tokens=10
        )
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)
 
 
def create_question_prompt(grade, term, topic_name, question_type, difficulty, existing_questions, generated_problems=[], include_svg=False):
    """문제 생성용 프롬프트 작성"""
    from .utils import get_grade_description
 
    # 도형/그래프 관련 주제 확인
    requires_svg = any(keyword in topic_name.lower() for keyword in [
        '도형', '삼각형', '사각형', '원', '다각형', '기하',
        '그래프', '좌표', '직선', '곡선',
        '통계', '차트', '막대', '원그래프', '히스토그램',
        '각', '넓이', '부피', '길이', '거리'
    ])
 
    if requires_svg:
        svg_instructions = """
 
        🔴 **SVG 필수 생성**: 이 주제는 도형/그래프 관련이므로 SVG가 반드시 필요합니다!
 
        **문제-그림 완벽 일치 원칙**:
        1. 문제에서 언급하는 모든 점, 변, 각을 SVG에 정확히 표시
        2. 문제에서 사용하는 기호/이름을 SVG에 동일하게 라벨링
        3. 문제에서 주어진 수치나 각도를 SVG에 반드시 표시
        4. 문제 상황과 100% 일치하는 도형/그래프 그리기
 
        **구체적 지침**:
        - 점: 문제에서 "점 A, B, C"라고 하면 SVG에서 정확히 A, B, C로 라벨링
        - 각: 문제에서 "∠A, ∠B"라고 하면 SVG에서 해당 각에 각도 표시선과 라벨
        - 변: 문제에서 "변 AB"라고 하면 SVG에서 AB 변을 명확히 표시
        - 수치: 문제에서 "5cm, 60°"라고 하면 SVG에서 해당 위치에 수치 표시
        - 비례: 문제의 수치 비율을 SVG에서 시각적으로 맞추기
 
        다음 유형에 맞는 SVG를 생성하세요:
        - 도형: 삼각형, 사각형, 원 등의 정확한 도형 그리기
        - 그래프: 좌표평면, 함수 그래프, 직선/곡선
        - 통계: 막대그래프, 원그래프, 히스토그램
        - 기하: 각도, 길이, 넓이 표시
 
        SVG 사양 (태블릿 화면 최적화):
        - 뷰박스 사용: viewBox="0 0 400 300" width="100%" height="auto"
        - 반응형 디자인: 태블릿 화면에 맞게 자동 크기 조절
        - 스타일: 검은색 선(stroke="#000" stroke-width="2"), 회색 채우기(fill="#f0f0f0")
        - 텍스트: font-family="Arial" font-size="16" (태블릿용 크기)
        - 격자, 축, 수치, 라벨 명확히 표시
        - 터치 친화적 요소 크기 (최소 44px 터치 영역)
 
        **각도 표현 중요 규칙**:
        - 각도를 시각적으로 그리지 마세요 (호나 부채꼴 금지)
        - 대신 각의 꼭짓점과 두 변만 그리고 알파벳으로 표시
        - 예: ∠ABC는 점 A, B, C만 표시하고 "∠ABC" 텍스트 라벨 사용
        - 각도의 크기나 모양을 추측해서 그리지 말고 기하학적 관계만 표현
        - 정확도를 위해 각도 표시는 텍스트 라벨로만 처리
 
        **절대 금지**: svg_code를 null로 설정하지 마세요!
        **필수**: 문제 내용과 완벽히 일치하는 그림만 생성하세요!
        """
    else:
        svg_instructions = """
 
        SVG 생성 판단:
        - 순수 계산/대수 문제: svg_code를 null로 설정
        - 시각적 요소가 조금이라도 있으면: SVG 생성
 
        SVG 사양 (필요한 경우, 태블릿 최적화):
        - 뷰박스 사용: viewBox="0 0 300 200" width="100%" height="auto"
        - 스타일: 검은색 선(stroke="#000" stroke-width="2"), 회색 채우기(fill="#f0f0f0")
        - 텍스트: font-family="Arial" font-size="14" (태블릿용)
 
        **각도 표현**: 시각적 각도 그리기 금지, 알파벳 라벨만 사용
        """
 
    # 항상 SVG 포함 가능한 응답 형식 사용
    response_format = f"""
    응답 형식 (JSON):
    {{
        "question_text": "문제 내용 (LaTeX 수식 포함)",
        "question_type": "{question_type}",
        "choices": ["① 선택지1", "② 선택지2", "③ 선택지3", "④ 선택지4", "⑤ 선택지5"] (선택형인 경우만),
        "correct_answer": "정답 (①~⑤ 또는 숫자/식)",
        "answer_explanation": "상세한 풀이 과정 (LaTeX 수식 포함)",
        "svg_code": "<svg>...</svg> 또는 null (문제 풀이에 시각 자료가 필요한 경우만)"
    }}
 
    **중요한 JSON 형식 주의사항:**
    - LaTeX 수식에서 백슬래시(\\)는 JSON에서 이중 백슬래시(\\\\)로 작성하세요
    - 예: "\\\\(" 대신 "\\\\\\\\(" 사용, "\\\\frac" 대신 "\\\\\\\\frac" 사용
    - JSON 문자열 내의 모든 백슬래시는 두 번씩 작성하세요
    - SVG 코드도 마찬가지로 백슬래시를 이중으로 이스케이프하세요
    """
 
    # 난이도별 문장 수 요구사항
    sentence_requirements = {
        '하': "1~2문장의 간단한 문제",
        '중': "3문장 정도의 적당한 문제",
        '상': "4문장 정도의 복합적인 문제"
    }
 
    sentence_req = sentence_requirements.get(difficulty, "적당한 길이의 문제")
 
    return f"""
    다음 조건에 맞는 중학교 수학 문제를 생성해주세요:
    - 학년: {grade} ({get_grade_description(grade)})
    - 학기: {term}학기
    - 주제: {topic_name}
    - 문제 유형: {question_type}
    - 난이도: {difficulty} → {sentence_req}
 
    제약조건:
    - 명확한 정답이 있는 문제만 생성
    - 선택형의 경우 5개 선택지 (①, ②, ③, ④, ⑤)
    - 단답형의 경우 숫자나 간단한 식으로 답할 수 있는 문제
    - LaTeX 수식 사용 권장
    - **문제 길이**: {sentence_req} (난이도에 맞게 조절){svg_instructions}
 
    기존 문제 스타일 참고:
    {existing_questions}
 
    이미 생성된 문제들 (중복 피하기):
    {chr(10).join([f"- {p}" for p in generated_problems]) if generated_problems else "없음"}
 
    **중요**: 위에 나열된 문제들과 다른 새로운 문제를 생성하세요. 계수나 상수를 바꾸어 다양한 문제를 만드세요.
 
    {response_format}
    """
 
 
def generate_question_with_ai(client, grade, term, topic_name, question_type, difficulty, existing_questions, generated_problems=[], include_svg=False):
    """OpenAI를 사용하여 문제 생성"""
    try:
        prompt = create_question_prompt(grade, term, topic_name, question_type, difficulty, existing_questions, generated_problems, include_svg)
 
        response = client.chat.completions.create(
            model=os.environ["AOAI_DEPLOYMENT"],
            messages=[
                {"role": "system", "content": "당신은 한국 중학교 수학 문제 출제 전문가입니다. 교육부 교육과정에 맞는 고품질 문제를 JSON 형식으로 생성해주세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
 
        content = response.choices[0].message.content.strip()
 
        # JSON 추출
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_content = content[json_start:json_end].strip()
        elif content.startswith("{"):
            json_content = content
        else:
            # JSON이 없으면 전체 응답에서 JSON 부분 찾기
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                json_content = content[start_idx:end_idx]
            else:
                logging.error("No valid JSON found in AI response")
                return None
 
        try:
            # LaTeX 백슬래시 이스케이프 처리 (검증된 정규식 접근법)
            import re
 
            def fix_latex_in_json_string(match):
                content = match.group(1)
                # LaTeX 수식 패턴만 안전하게 이스케이프 (JSON에서 valid하지 않은 백슬래시들)
                content = re.sub(r'(?<!\\)\\(?!["\\/bfnrt])', r'\\\\', content)
                return f'"{content}"'
 
            # JSON 문자열 값들에서만 백슬래시 처리
            safe_json_content = re.sub(r'"([^"]*\\[^"]*)"', fix_latex_in_json_string, json_content)
 
            question_data = json.loads(safe_json_content)
 
            # svg_code를 svg_content로 변환
            if 'svg_code' in question_data:
                question_data['svg_content'] = question_data.pop('svg_code')
 
            return question_data
 
        except json.JSONDecodeError as je:
            logging.error(f"JSON parsing error: {str(je)}")
            logging.error(f"Raw JSON content: {json_content}")
 
            # 백업 파싱 시도 - 단순한 백슬래시 두 배 처리
            try:
                logging.info("Attempting backup JSON parsing with simple backslash doubling...")
                backup_content = json_content.replace('\\', '\\\\')
                # 과도하게 이스케이프된 것들 수정
                backup_content = backup_content.replace('\\\\\\\\', '\\\\')
                backup_content = backup_content.replace('\\\\"', '\\"')  # 따옴표는 원래대로
 
                question_data = json.loads(backup_content)
 
                # svg_code를 svg_content로 변환
                if 'svg_code' in question_data:
                    question_data['svg_content'] = question_data.pop('svg_code')
 
                logging.info("Backup JSON parsing successful")
                return question_data
 
            except json.JSONDecodeError as backup_je:
                logging.error(f"Backup JSON parsing also failed: {str(backup_je)}")
                return None
 
    except Exception as e:
        logging.error(f"AI question generation error: {str(e)}")
        return None