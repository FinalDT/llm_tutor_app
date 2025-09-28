#!/usr/bin/env python3
"""
개별 단계별 테스트 예제
각 API 엔드포인트를 독립적으로 테스트
"""

import requests
import json
from typing import Dict, Any

API_URL = "http://localhost:7071/api/tutor_api"

class TutorAPITester:
    """튜터 API 테스터 클래스"""

    def __init__(self):
        self.api_url = API_URL
        self.timeout = 30

    def send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """API 요청 전송"""
        try:
            print(f"📤 요청:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))

            response = requests.post(self.api_url, json=payload, timeout=self.timeout)
            print(f"\n📊 상태 코드: {response.status_code}")

            result = response.json()
            print(f"📨 응답:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

            return result
        except Exception as e:
            print(f"❌ 오류: {e}")
            return {}

    def test_session_summary(self):
        """1단계: 진단테스트 요약 테스트"""
        print("\n" + "="*50)
        print("🎯 1단계: 진단테스트 요약 테스트")
        print("="*50)

        test_cases = [
            {
                "name": "기본 케이스",
                "payload": {
                    "request_type": "session_summary",
                    "learnerID": "A070001768",
                    "session_id": "rt-20250918:first6:A070001768:0"
                }
            },
            {
                "name": "대화 기록 포함",
                "payload": {
                    "request_type": "session_summary",
                    "learnerID": "A070001768",
                    "session_id": "rt-20250918:first6:A070001768:0",
                    "conversation_history": [
                        {"role": "user", "content": "안녕하세요"}
                    ]
                }
            }
        ]

        for case in test_cases:
            print(f"\n🧪 테스트: {case['name']}")
            result = self.send_request(case["payload"])

            if result and "feedback" in result:
                print("✅ 성공: 피드백 생성됨")
                print(f"📝 피드백 길이: {len(result['feedback'])} 문자")
            else:
                print("❌ 실패: 피드백 생성 안됨")

    def test_item_feedback(self):
        """2단계: 유사문항 생성 테스트"""
        print("\n" + "="*50)
        print("🎯 2단계: 유사문항 생성 테스트")
        print("="*50)

        # 실제 1단계 결과를 시뮬레이션
        conversation_history = [
            {
                "role": "user",
                "content": "피드백 요청"
            },
            {
                "role": "assistant",
                "content": "진단 테스트 푸느라 수고 많았어! 결과를 알려줄게.\n\n전체 6 문제 중에서 2 문제를 맞혔네. 정말 잘했어! 👍\n\n이번 테스트에서는 아쉽게도 1, 2, 4, 5 번 문제를 틀렸더라. 데이터를 분석해보니, 주로 \"부채꼴의 호의 길이와 넓이 사이의 관계, 다각형의 내각의 크기의 합, 원뿔의 겉넓이, 각기둥의 겉넓이\" 개념들이 조금 헷갈리는 것 같아.\n\n우리 같이 \"부채꼴의 호의 길이와 넓이 사이의 관계\"에 대한 학습을 시작해볼까?"
            }
        ]

        test_cases = [
            {
                "name": "1번 문제 유사문항",
                "message": "1번문제 유사 문항 주세요"
            },
            {
                "name": "구체적 개념 요청",
                "message": "부채꼴 관련 문제 더 주세요"
            },
            {
                "name": "다른 문제 요청",
                "message": "4번문제 비슷한 거 연습하고 싶어요"
            }
        ]

        for case in test_cases:
            print(f"\n🧪 테스트: {case['name']}")

            payload = {
                "request_type": "item_feedback",
                "learnerID": "A070001768",
                "session_id": "rt-20250918:first6:A070001768:0",
                "message": case["message"],
                "conversation_history": conversation_history
            }

            result = self.send_request(payload)

            if result and "generated_question_data" in result:
                question_data = result["generated_question_data"]
                print("✅ 성공: 문제 생성됨")
                print(f"📝 문제: {question_data['new_question_text'][:100]}...")
                print(f"📝 정답: {question_data['correct_answer']}")

                # 답과 해설 일치성 검증
                if question_data['correct_answer'] in question_data['explanation']:
                    print("✅ 답-해설 일치성: 정상")
                else:
                    print("⚠️ 답-해설 일치성: 검토 필요")

            else:
                print("❌ 실패: 문제 생성 안됨")

    def test_generated_item_hint(self):
        """3단계: 힌트 제공 테스트"""
        print("\n" + "="*50)
        print("🎯 3단계: 힌트 제공 테스트")
        print("="*50)

        # 2단계에서 생성된 문제 데이터 시뮬레이션
        generated_question = {
            "new_question_text": "높이가 5cm, 밑면이 정사각형인 각기둥의 겉넓이를 구하세요. 정사각형의 한 변의 길이는 4cm입니다.",
            "correct_answer": "72 cm²",
            "explanation": "각기둥의 겉넓이는 밑면의 넓이와 옆면의 넓이를 모두 더하여 구합니다. 밑면은 정사각형이므로 4×4=16cm², 위아래 합쳐서 32cm². 옆면은 직사각형 4개로 4×5×4=80cm². 따라서 32+80=112cm²가 아니라... 계산을 다시 해보면 밑면 2개: 4×4×2=32cm², 옆면 4개: 4×5×4=80cm². 하지만 이 경우 답이 맞지 않으니 다시 계산하면 밑면넓이 4×4=16, 옆면넓이 4×5=20이 4개라서 16×2+20×4=32+80=112가 되어야 하는데 정답이 72라면 계산 과정을 재검토해야 합니다. 올바른 계산은 밑면 2개: 16×2=32, 옆면 4개: 4×5×4=80이 아니라 4×(4×5)=80이므로 32+40=72cm²입니다."
        }

        conversation_history = [
            {"role": "user", "content": "피드백 요청"},
            {"role": "assistant", "content": "진단 결과..."},
            {"role": "user", "content": "1번문제 유사 문항 주세요"},
            {
                "role": "assistant",
                "content": f"좋아! '각기둥의 겉넓이' 개념을 더 연습해볼까? 아래 문제를 풀어봐.\n\n{generated_question['new_question_text']}"
            }
        ]

        test_messages = [
            {
                "name": "기본 힌트 요청",
                "message": "모르겠어요"
            },
            {
                "name": "구체적 힌트 요청",
                "message": "힌트 주세요"
            },
            {
                "name": "접근 방법 질문",
                "message": "어떻게 시작해야 할까요?"
            },
            {
                "name": "공식 질문",
                "message": "공식이 뭐예요?"
            },
            {
                "name": "정답 요청 (소크라틱 테스트)",
                "message": "답이 뭐예요?"
            },
            {
                "name": "부분 답안 제시",
                "message": "밑면넓이는 16인데 그 다음은?"
            }
        ]

        for case in test_messages:
            print(f"\n🧪 테스트: {case['name']}")

            payload = {
                "request_type": "generated_item",
                "generated_question_data": generated_question,
                "message": case["message"],
                "conversation_history": conversation_history,
                "learnerID": "A070001768",
                "original_concept": "각기둥의 겉넓이"
            }

            result = self.send_request(payload)

            if result and "feedback" in result:
                feedback = result["feedback"]
                print("✅ 성공: 힌트 제공됨")

                # 소크라틱 방식 검증
                is_question = "?" in feedback
                has_direct_answer = any(keyword in feedback for keyword in ["72", "답은", "정답은"])

                print(f"📊 소크라틱 검증:")
                print(f"  - 질문 형태: {'✅' if is_question else '❌'}")
                print(f"  - 직접 정답 노출: {'❌' if has_direct_answer else '✅'}")
                print(f"📝 힌트 내용: {feedback}")

            else:
                print("❌ 실패: 힌트 생성 안됨")

    def test_edge_cases(self):
        """엣지 케이스 테스트"""
        print("\n" + "="*50)
        print("🎯 엣지 케이스 테스트")
        print("="*50)

        edge_cases = [
            {
                "name": "빈 메시지",
                "payload": {
                    "request_type": "item_feedback",
                    "learnerID": "A070001768",
                    "session_id": "rt-20250918:first6:A070001768:0",
                    "message": "",
                    "conversation_history": []
                }
            },
            {
                "name": "매우 긴 메시지",
                "payload": {
                    "request_type": "item_feedback",
                    "learnerID": "A070001768",
                    "session_id": "rt-20250918:first6:A070001768:0",
                    "message": "이것은 매우 긴 메시지입니다. " * 100,
                    "conversation_history": []
                }
            },
            {
                "name": "특수 문자 포함",
                "payload": {
                    "request_type": "item_feedback",
                    "learnerID": "A070001768",
                    "session_id": "rt-20250918:first6:A070001768:0",
                    "message": "1번문제 ~!@#$%^&*()_+ 유사문항 ♠♣♥♦",
                    "conversation_history": []
                }
            }
        ]

        for case in edge_cases:
            print(f"\n🧪 테스트: {case['name']}")
            result = self.send_request(case["payload"])

            if result:
                if "error" in result:
                    print(f"⚠️ 에러 응답: {result['error']}")
                elif "feedback" in result:
                    print("✅ 정상 처리됨")
                else:
                    print("❓ 예상과 다른 응답")

def main():
    """메인 실행 함수"""
    tester = TutorAPITester()

    print("🚀 개별 단계별 API 테스트")
    print("각 API 엔드포인트를 독립적으로 테스트합니다.")

    print("\n📋 실행할 테스트를 선택하세요:")
    print("1️⃣  진단테스트 요약 (1단계)")
    print("2️⃣  유사문항 생성 (2단계)")
    print("3️⃣  힌트 제공 (3단계)")
    print("4️⃣  엣지 케이스 테스트")
    print("5️⃣  모든 테스트 실행")

    choice = input("\n선택 (1-5): ").strip()

    if choice == "1":
        tester.test_session_summary()
    elif choice == "2":
        tester.test_item_feedback()
    elif choice == "3":
        tester.test_generated_item_hint()
    elif choice == "4":
        tester.test_edge_cases()
    elif choice == "5":
        tester.test_session_summary()
        tester.test_item_feedback()
        tester.test_generated_item_hint()
        tester.test_edge_cases()
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()