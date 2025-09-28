"""
파인튜닝된 모델 연결 테스트
"""
import json
from services.llm_service import LLMService

def test_finetuned_model():
    """파인튜닝된 모델 테스트"""
    print("🚀 파인튜닝된 모델 연결 테스트 시작...")

    try:
        llm_service = LLMService()

        # 테스트 케이스: 근호 개념의 힌트 요청
        system_prompt = "너는 '근호를 포함한 식의 혼합 계산' 개념에 대해 50% 정답률을 가진 학생에게 개인화된 수학 튜터링을 제공하는 AI야. 학생의 수준에 맞는 소크라틱 방식으로 응답해야 해."
        user_prompt = "힌트 좀 주세요"

        print("📤 요청 전송 중...")
        print(f"System: {system_prompt}")
        print(f"User: {user_prompt}")
        print()

        response = llm_service.call_llm(system_prompt, user_prompt, [])

        print("✅ 파인튜닝 모델 응답:")
        print(f"📨 {response}")
        print()

        # 소크라틱 방식 확인
        if "?" in response:
            print("✅ 소크라틱 방식 확인: 질문 형태로 응답함")
        else:
            print("⚠️ 주의: 질문 형태가 아닐 수 있음")

        print("🎉 파인튜닝 모델 연결 성공!")
        return True

    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_finetuned_model()