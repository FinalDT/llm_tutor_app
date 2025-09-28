#!/usr/bin/env python3
"""
LLM 튜터 앱 API 테스트 스크립트
"""

import requests
import json
import time

# API 엔드포인트
API_URL = "http://localhost:7071/api/tutor_api"

def test_session_summary():
    """1단계: 진단테스트 요약 테스트"""
    print("🧪 1단계: 진단테스트 요약 테스트")
    print("=" * 50)
    
    payload = {
        "request_type": "session_summary",
        "learnerID": "A070001768",
        "session_id": "rt-20250918:first6:A070001768:0"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.json()
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def test_item_feedback():
    """2단계: 유사문항 생성 테스트"""
    print("\n🧪 2단계: 유사문항 생성 테스트")
    print("=" * 50)
    
    payload = {
        "request_type": "item_feedback",
        "learnerID": "A070001768",
        "session_id": "rt-20250918:first6:A070001768:0",
        "message": "1번문제 유사 문항 주세요",
        "conversation_history": [
            {
                "role": "user",
                "content": "피드백 요청"
            },
            {
                "role": "assistant",
                "content": "진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.\n\n전체 6 문제 중에서 2 문제를 맞혔네. 정말 잘했어! 👍\n\n이번 테스트에서는 아쉽게도 1, 2, 4, 5 번 문제를 틀렸더라. 데이터를 분석해보니, 주로 \"부채꼴의 호의 길이와 넓이 사이의 관계, 다각형의 내각의 크기의 합, 원뿔의 겉넓이, 각기둥의 겉넓이\" 개념들이 조금 헷갈리는 것 같아.\n\n우리 같이 \"부채꼴의 호의 길이와 넓이 사이의 관계\"에 대한 학습을 시작해볼까?"
            }
        ]
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.json()
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def test_generated_item_hint():
    """3단계: 힌트 제공 테스트"""
    print("\n🧪 3단계: 힌트 제공 테스트")
    print("=" * 50)
    
    payload = {
        "request_type": "generated_item",
        "generated_question_data": {
            "new_question_text": "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요. 정사각형의 한 변의 길이는 4cm입니다.",
            "correct_answer": "72 cm²",
            "explanation": "각기둥의 겉넓이는 밑면의 넓이와 옆면의 넓이를 모두 더하여 구합니다."
        },
        "message": "모르겠어요",
        "conversation_history": [
            {
                "role": "user",
                "content": "피드백 요청"
            },
            {
                "role": "assistant",
                "content": "진단 테스트 결과..."
            },
            {
                "role": "user",
                "content": "1번문제 유사 문항 주세요"
            },
            {
                "role": "assistant",
                "content": "좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까? 아래 문제를 풀어봐.\n\n높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요. 정사각형의 한 변의 길이는 4cm입니다."
            }
        ]
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.json()
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def check_server():
    """서버 연결 상태 확인"""
    try:
        response = requests.get("http://localhost:7071", timeout=5)
        print("✅ Azure Functions 서버가 실행 중입니다.")
        return True
    except:
        print("❌ Azure Functions 서버에 연결할 수 없습니다.")
        print("다음 명령어로 서버를 시작하세요: func start")
        return False

def main():
    """메인 테스트 함수 - 사용자 선택 방식"""
    print("🚀 LLM 튜터 앱 API 테스트")
    print("=" * 60)
    
    # 서버 연결 확인
    if not check_server():
        return
    
    while True:
        print("\n📋 테스트할 기능을 선택하세요:")
        print("1️⃣  진단테스트 요약 (session_summary)")
        print("2️⃣  유사문항 생성 (item_feedback)")
        print("3️⃣  힌트 제공 (generated_item)")
        print("4️⃣  실제 사용환경 대화형 힌트 (NEW!)")
        print("5️⃣  모든 기능 테스트")
        print("0️⃣  종료")
        
        choice = input("\n선택 (1-5, 0): ").strip()
        
        if choice == "1":
            test_session_summary()
        elif choice == "2":
            test_item_feedback()
        elif choice == "3":
            test_generated_item_hint()
        elif choice == "4":
            print("💡 실제 사용환경 대화형 힌트 테스트는 다음 명령어로 실행하세요:")
            print("python test_real_interactive_hint.py")
        elif choice == "5":
            print("\n🔄 모든 기능 테스트 시작...")
            test_session_summary()
            test_item_feedback()
            test_generated_item_hint()
            print("\n🎉 모든 테스트가 완료되었습니다!")
        elif choice == "0":
            print("👋 테스트를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-5 또는 0을 입력하세요.")
        
        # 다음 테스트를 위한 대기
        if choice != "0":
            input("\n⏸️  Enter를 눌러 계속하세요...")

if __name__ == "__main__":
    main()
