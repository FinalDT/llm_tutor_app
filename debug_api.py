#!/usr/bin/env python3
"""
API 디버깅 스크립트 - 400 오류 원인 분석
"""

import requests
import json

# API 엔드포인트
API_URL = "http://localhost:7071/api/tutor_api"

def test_basic_request():
    """기본 요청 테스트"""
    print("🔍 기본 요청 테스트")
    print("=" * 50)
    
    payload = {
        "request_type": "generated_item",
        "generated_question_data": {
            "new_question_text": "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요.",
            "correct_answer": "96 cm²",
            "explanation": "각기둥의 겉넓이는 밑면의 넓이와 옆면의 넓이를 모두 더하여 구합니다."
        },
        "message": "힌트 주세요",
        "conversation_history": [
            {
                "role": "user",
                "content": "피드백 요청"
            },
            {
                "role": "assistant",
                "content": "진단 테스트 결과..."
            }
        ]
    }
    
    print("📤 요청 데이터:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        print(f"\n📊 상태 코드: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 성공!")
            print(f"응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print("❌ 오류 발생!")
            print(f"응답 텍스트: {response.text}")
            
            # 오류 응답을 JSON으로 파싱 시도
            try:
                error_data = response.json()
                print(f"오류 JSON: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print("오류 응답이 JSON 형식이 아닙니다.")
                
    except Exception as e:
        print(f"❌ 연결 오류: {e}")

def test_minimal_request():
    """최소 요청 테스트"""
    print("\n🔍 최소 요청 테스트")
    print("=" * 50)
    
    payload = {
        "request_type": "generated_item",
        "generated_question_data": {
            "new_question_text": "테스트 문제",
            "correct_answer": "테스트 정답",
            "explanation": "테스트 해설"
        },
        "message": "테스트",
        "conversation_history": []
    }
    
    print("📤 요청 데이터:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        print(f"\n📊 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 성공!")
            print(f"응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print("❌ 오류 발생!")
            print(f"응답 텍스트: {response.text}")
                
    except Exception as e:
        print(f"❌ 연결 오류: {e}")

def test_other_request_types():
    """다른 request_type 테스트"""
    print("\n🔍 다른 request_type 테스트")
    print("=" * 50)
    
    request_types = ["session_summary", "item_feedback"]
    
    for request_type in request_types:
        print(f"\n📝 테스트: {request_type}")
        print("-" * 30)
        
        if request_type == "session_summary":
            payload = {
                "request_type": request_type,
                "learnerID": "A070001768",
                "session_id": "rt-20250918:first6:A070001768:0"
            }
        elif request_type == "item_feedback":
            payload = {
                "request_type": request_type,
                "learnerID": "A070001768",
                "session_id": "rt-20250918:first6:A070001768:0",
                "message": "1번문제 유사 문항 주세요",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "피드백 요청"
                    }
                ]
            }
        
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            print(f"상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
            else:
                print(f"❌ 오류: {response.text}")
                
        except Exception as e:
            print(f"❌ 연결 오류: {e}")

def main():
    """메인 디버깅 함수"""
    print("🚀 API 디버깅 시작")
    print("=" * 60)
    
    # 서버 연결 확인
    try:
        response = requests.get("http://localhost:7071", timeout=5)
        print("✅ Azure Functions 서버가 실행 중입니다.")
    except:
        print("❌ Azure Functions 서버에 연결할 수 없습니다.")
        return
    
    # 각 테스트 실행
    test_basic_request()
    test_minimal_request()
    test_other_request_types()
    
    print("\n🎯 디버깅 완료!")

if __name__ == "__main__":
    main()
