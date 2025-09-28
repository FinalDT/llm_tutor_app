#!/usr/bin/env python3
"""
완전한 3단계 플로우 테스트 예제
진단테스트 요약 → 유사문항 생성 → 힌트 제공까지 전체 흐름 테스트
"""

import requests
import json
import time
from typing import Dict, Any, List

# API 설정
API_URL = "http://localhost:7071/api/tutor_api"
TIMEOUT = 30

def print_separator(title: str):
    """섹션 구분선 출력"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def send_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """API 요청 전송 및 응답 처리"""
    try:
        print(f"📤 요청 전송:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        response = requests.post(API_URL, json=payload, timeout=TIMEOUT)
        print(f"\n📊 상태 코드: {response.status_code}")

        result = response.json()
        print(f"📨 응답:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        return result
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return {}

def test_complete_flow():
    """전체 3단계 플로우 테스트"""
    print("🚀 LLM 튜터 API 완전한 플로우 테스트")
    print("실제 데이터를 사용한 완전한 사용자 여정 시뮬레이션")

    # 테스트 데이터
    learner_id = "A070001768"
    session_id = "rt-20250918:first6:A070001768:0"
    conversation_history = []

    # 1단계: 진단테스트 요약
    print_separator("1단계: 진단테스트 결과 분석")

    step1_payload = {
        "request_type": "session_summary",
        "learnerID": learner_id,
        "session_id": session_id,
        "conversation_history": conversation_history
    }

    step1_result = send_request(step1_payload)

    if not step1_result or "feedback" not in step1_result:
        print("❌ 1단계 실패 - 테스트 중단")
        return False

    # 대화 기록 업데이트
    conversation_history = step1_result.get("conversation_history", [])
    print(f"\n✅ 1단계 완료 - 대화 기록: {len(conversation_history)}개 메시지")

    # 잠시 대기 (실제 사용자 행동 시뮬레이션)
    time.sleep(2)

    # 2단계: 유사문항 생성
    print_separator("2단계: 유사문항 생성 요청")

    step2_payload = {
        "request_type": "item_feedback",
        "learnerID": learner_id,
        "session_id": session_id,
        "message": "1번문제 유사 문항 주세요",
        "conversation_history": conversation_history
    }

    step2_result = send_request(step2_payload)

    if not step2_result or "generated_question_data" not in step2_result:
        print("❌ 2단계 실패 - 테스트 중단")
        return False

    # 생성된 문제 데이터 추출
    generated_question = step2_result["generated_question_data"]
    conversation_history = step2_result.get("conversation_history", [])
    print(f"\n✅ 2단계 완료 - 문제 생성됨: {generated_question['new_question_text'][:50]}...")

    # 잠시 대기
    time.sleep(2)

    # 3단계: 힌트 제공 (여러 번 상호작용)
    print_separator("3단계: 힌트 제공 (대화형 상호작용)")

    # 3-1: 첫 번째 힌트 요청
    step3_messages = [
        "모르겠어요",
        "힌트 주세요",
        "어떻게 시작해야 할까요?",
        "답이 뭐예요?"  # 마지막에 정답 요청 (소크라틱 방식 테스트)
    ]

    for i, message in enumerate(step3_messages, 1):
        print(f"\n--- 3-{i}: 학생 메시지 '{message}' ---")

        step3_payload = {
            "request_type": "generated_item",
            "generated_question_data": generated_question,
            "message": message,
            "conversation_history": conversation_history,
            "learnerID": learner_id,
            "original_concept": "부채꼴의 호의 길이와 넓이 사이의 관계"
        }

        step3_result = send_request(step3_payload)

        if step3_result and "feedback" in step3_result:
            conversation_history = step3_result.get("conversation_history", [])
            ai_response = step3_result["feedback"]

            # 소크라틱 방식 검증
            is_socratic = "?" in ai_response
            contains_answer = any(keyword in ai_response.lower() for keyword in ["답", "정답", "결과"])

            print(f"🤖 AI 응답: {ai_response}")
            print(f"📊 소크라틱 검증: {'✅' if is_socratic else '❌'} 질문형태")
            print(f"📊 정답 노출: {'❌' if contains_answer else '✅'} 직접 노출 안함")
        else:
            print(f"❌ 3-{i} 단계 실패")
            return False

        # 대화 간 대기
        time.sleep(1)

    print_separator("테스트 완료 - 전체 결과 요약")
    print(f"✅ 총 대화 메시지 수: {len(conversation_history)}")
    print(f"✅ 생성된 문제: {generated_question['new_question_text']}")
    print(f"✅ 정답: {generated_question['correct_answer']}")
    print(f"✅ 모든 단계 성공적으로 완료!")

    return True

def test_error_scenarios():
    """에러 시나리오 테스트"""
    print_separator("에러 시나리오 테스트")

    error_cases = [
        {
            "name": "필수 필드 누락",
            "payload": {"request_type": "session_summary"},
            "expected_status": 400
        },
        {
            "name": "잘못된 request_type",
            "payload": {
                "request_type": "invalid_type",
                "learnerID": "test",
                "session_id": "test"
            },
            "expected_status": 400
        },
        {
            "name": "존재하지 않는 세션",
            "payload": {
                "request_type": "session_summary",
                "learnerID": "INVALID_USER",
                "session_id": "INVALID_SESSION"
            },
            "expected_status": 500
        }
    ]

    for case in error_cases:
        print(f"\n🧪 테스트: {case['name']}")
        try:
            response = requests.post(API_URL, json=case["payload"], timeout=10)
            print(f"상태 코드: {response.status_code} (예상: {case['expected_status']})")

            if response.status_code == case['expected_status']:
                print("✅ 예상된 에러 정상 처리")
            else:
                print("⚠️ 예상과 다른 응답")

            result = response.json()
            print(f"응답: {json.dumps(result, ensure_ascii=False, indent=2)}")

        except Exception as e:
            print(f"❌ 요청 실패: {e}")

def test_performance():
    """성능 테스트"""
    print_separator("성능 테스트")

    test_payload = {
        "request_type": "session_summary",
        "learnerID": "A070001768",
        "session_id": "rt-20250918:first6:A070001768:0"
    }

    response_times = []
    success_count = 0

    for i in range(5):
        print(f"🚀 요청 {i+1}/5...")
        start_time = time.time()

        try:
            response = requests.post(API_URL, json=test_payload, timeout=30)
            end_time = time.time()

            response_time = end_time - start_time
            response_times.append(response_time)

            if response.status_code == 200:
                success_count += 1
                print(f"✅ 성공 - 응답시간: {response_time:.2f}초")
            else:
                print(f"❌ 실패 - 상태: {response.status_code}")

        except Exception as e:
            print(f"❌ 요청 실패: {e}")

    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        print(f"\n📊 성능 결과:")
        print(f"성공률: {success_count}/5 ({success_count/5*100:.1f}%)")
        print(f"평균 응답시간: {avg_time:.2f}초")
        print(f"최대 응답시간: {max_time:.2f}초")
        print(f"최소 응답시간: {min_time:.2f}초")

def main():
    """메인 실행 함수"""
    print("🔍 서버 연결 상태 확인...")
    try:
        health_check = requests.get("http://localhost:7071", timeout=5)
        print("✅ 서버 연결 성공")
    except:
        print("❌ 서버 연결 실패 - func start로 서버를 시작하세요")
        return

    print("\n📋 실행할 테스트를 선택하세요:")
    print("1️⃣  완전한 3단계 플로우 테스트")
    print("2️⃣  에러 시나리오 테스트")
    print("3️⃣  성능 테스트")
    print("4️⃣  모든 테스트 실행")

    choice = input("\n선택 (1-4): ").strip()

    if choice == "1":
        test_complete_flow()
    elif choice == "2":
        test_error_scenarios()
    elif choice == "3":
        test_performance()
    elif choice == "4":
        test_complete_flow()
        test_error_scenarios()
        test_performance()
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()