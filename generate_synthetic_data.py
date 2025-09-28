"""
실제 패턴을 기반으로 파인튜닝용 합성 대화 데이터 생성
5개 개념 × 3개 수준 × 3개 시나리오 = 45개 대화
"""
import json
import logging
from services.llm_service import LLMService

def generate_synthetic_training_data():
    """실제 DB 패턴을 기반으로 합성 훈련 데이터 생성"""

    # 실제 패턴 로드
    with open("real_patterns.json", "r", encoding="utf-8") as f:
        patterns = json.load(f)

    print("📊 실제 DB 패턴 정보:")
    print(f"  데이터 출처: {patterns['extraction_summary']['data_source']}")
    print(f"  훈련용 개념: {patterns['extraction_summary']['top_concepts_for_training']}개")

    llm_service = LLMService()
    training_data = []

    # 3가지 시나리오 템플릿
    scenarios = [
        {
            "type": "hint_request",
            "student_messages": [
                "이 문제 어떻게 풀어야 해요?",
                "힌트 좀 주세요",
                "모르겠어요 도움이 필요해요",
                "어디서부터 시작해야 할지 모르겠어요"
            ]
        },
        {
            "type": "similar_problem",
            "student_messages": [
                "비슷한 문제 더 주세요",
                "연습 문제 있나요?",
                "이런 유형 더 풀어보고 싶어요",
                "다른 문제로 연습할래요"
            ]
        },
        {
            "type": "concept_confusion",
            "student_messages": [
                "이 개념이 헷갈려요",
                "왜 이렇게 되는지 모르겠어요",
                "공식을 어떻게 적용해야 하나요?",
                "이해가 안 되는 부분이 있어요"
            ]
        }
    ]

    print("\n🤖 실제 패턴 기반 합성 대화 데이터 생성 시작...")

    for concept in patterns["concepts"]:
        concept_name = concept["concept_name"]
        base_success_rate = concept["success_rate"]
        avg_personal_accuracy = concept["avg_personal_accuracy"]
        avg_global_accuracy = concept["avg_global_accuracy"]

        print(f"\n📚 {concept_name}")
        print(f"  실제 성공률: {base_success_rate*100:.1f}%")
        print(f"  개인 평균 정확도: {avg_personal_accuracy*100:.1f}%")
        print(f"  전체 평균 정확도: {avg_global_accuracy*100:.1f}%")

        # 실제 데이터 기반 3가지 수준 설정
        accuracy_levels = [
            {
                "level": "low",
                "accuracy": max(0.2, avg_personal_accuracy - 0.3),  # 실제보다 낮음
                "description": f"어려움을 느끼는 수준 (실제 평균: {avg_personal_accuracy*100:.1f}%)"
            },
            {
                "level": "medium",
                "accuracy": avg_personal_accuracy,  # 실제 평균 사용
                "description": f"평균 수준 (실제 데이터)"
            },
            {
                "level": "high",
                "accuracy": min(0.9, avg_personal_accuracy + 0.2),  # 실제보다 높음
                "description": f"우수 수준 (실제 평균: {avg_personal_accuracy*100:.1f}%)"
            }
        ]

        for accuracy_level in accuracy_levels:
            for scenario in scenarios:
                # 학생 메시지 선택
                import random
                student_message = random.choice(scenario["student_messages"])

                # 실제 데이터를 포함한 맞춤형 튜터 응답 생성
                tutor_response = generate_tutor_response_with_real_data(
                    llm_service, concept_name, accuracy_level, scenario, student_message,
                    base_success_rate, avg_global_accuracy
                )

                # Fine-tuning 형식으로 변환
                training_example = {
                    "messages": [
                        {
                            "role": "system",
                            "content": f"너는 '{concept_name}' 개념에 대해 {accuracy_level['accuracy']*100:.1f}% 정답률을 가진 학생에게 개인화된 수학 튜터링을 제공하는 AI야. 실제 데이터: 이 개념의 전체 평균 성공률은 {base_success_rate*100:.1f}%이고, 전체 학생 평균 정확도는 {avg_global_accuracy*100:.1f}%야. 학생의 수준에 맞는 소크라틱 방식으로 응답해야 해."
                        },
                        {
                            "role": "user",
                            "content": student_message
                        },
                        {
                            "role": "assistant",
                            "content": tutor_response
                        }
                    ]
                }

                training_data.append(training_example)
                print(f"  ✅ {len(training_data)}/45 - {accuracy_level['level']} × {scenario['type']}")

    # JSONL 형식으로 저장
    with open("synthetic_training_data.jsonl", "w", encoding="utf-8") as f:
        for example in training_data:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"\n🎉 실제 패턴 기반 합성 훈련 데이터 생성 완료: {len(training_data)}개")
    print("📁 파일: synthetic_training_data.jsonl")
    print("✨ 특징: 실제 DB 성공률과 정확도 데이터 반영됨")

    return training_data

def generate_tutor_response_with_real_data(llm_service, concept_name, accuracy_level, scenario, student_message, base_success_rate, avg_global_accuracy):
    """실제 DB 데이터를 포함한 GPT 맞춤형 튜터 응답 생성"""

    # 수준별 맞춤 지침
    level_guidance = {
        "low": "매우 기초적이고 단계별로 천천히 안내하세요. 기본 개념부터 확인하고 자신감을 높여주세요.",
        "medium": "적절한 수준의 힌트를 제공하되 스스로 생각할 여지를 남겨주세요.",
        "high": "간결하고 핵심적인 힌트로 자율적 사고를 유도하세요."
    }

    # 시나리오별 응답 방향
    scenario_guidance = {
        "hint_request": "직접적인 답이 아닌 다음 단계를 생각하게 하는 질문 형태로 힌트를 제공하세요.",
        "similar_problem": "비슷한 수준의 연습 문제를 제시하거나 연습 방향을 제안하세요.",
        "concept_confusion": "개념을 쉽게 설명하고 이해를 돕는 질문을 제시하세요."
    }

    # 실제 데이터 기반 개인화 정보
    if accuracy_level["accuracy"] < avg_global_accuracy:
        performance_context = "전체 평균보다 어려움을 느끼는 학생"
    elif accuracy_level["accuracy"] > avg_global_accuracy:
        performance_context = "전체 평균보다 우수한 학생"
    else:
        performance_context = "전체 평균 수준의 학생"

    system_prompt = f"""너는 실제 학습 데이터를 기반으로 개인화된 수학 튜터링을 제공하는 전문 AI야.

실제 데이터 정보:
- 개념: {concept_name}
- 이 학생 정답률: {accuracy_level['accuracy']*100:.1f}%
- 이 개념의 전체 평균 성공률: {base_success_rate*100:.1f}%
- 전체 학생 평균 정확도: {avg_global_accuracy*100:.1f}%
- 학생 특성: {performance_context}
- 요청 유형: {scenario['type']}

개인화 지침:
- 수준별 접근: {level_guidance[accuracy_level['level']]}
- 응답 방향: {scenario_guidance[scenario['type']]}

반드시 소크라틱 방식으로 학생이 스스로 생각할 수 있도록 질문 형태로 응답하고, 실제 데이터를 반영한 개인화된 피드백을 제공하세요."""

    user_prompt = f"학생 메시지: '{student_message}'\n\n위 실제 데이터와 상황에 맞는 개인화된 튜터 응답을 생성해주세요."

    try:
        response = llm_service.call_llm(system_prompt, user_prompt, [])
        return response
    except Exception as e:
        logging.error(f"실제 데이터 기반 튜터 응답 생성 실패: {e}")
        # 백업 응답
        return f"{concept_name}에 대해 어떤 부분이 가장 어렵게 느껴지나요? 현재 {accuracy_level['accuracy']*100:.1f}% 수준이니까 차근차근 접근해보자!"

def generate_tutor_response(llm_service, concept_name, accuracy_level, scenario, student_message, base_success_rate):
    """기존 호환성을 위한 함수 (deprecated)"""
    return generate_tutor_response_with_real_data(llm_service, concept_name, accuracy_level, scenario, student_message, base_success_rate, 0.5)

if __name__ == "__main__":
    generate_synthetic_training_data()