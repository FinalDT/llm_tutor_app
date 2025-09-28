#!/usr/bin/env python3
"""
실제 서비스 흐름 테스트 - 함수 직접 import 방식
사용자가 터미널에서 직접 입력하여 1→2→3 단계 전체 흐름 테스트
"""

from handlers.session_handler import SessionHandler
from handlers.feedback_handler import FeedbackHandler
from handlers.generated_item_handler import GeneratedItemHandler
from handlers.continuous_learning_handler import ContinuousLearningHandler
from handlers.session_state_manager import session_manager


def display_quick_replies(quick_replies):
    """빠른 선택지 표시 및 처리"""
    if not quick_replies:
        return "text_input", ""

    print("\n💡 빠른 선택:")
    for i, option in enumerate(quick_replies, 1):
        print(f"  {i}. {option['text']}")

    choice = input("번호 선택 (또는 직접 입력): ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(quick_replies):
        selected = quick_replies[int(choice)-1]
        print(f"✅ 선택: {selected['text']}")
        return selected['action'], selected.get('data', "")
    else:
        return "text_input", choice


def main():
    print("🚀 실제 서비스 흐름 테스트")
    print("="*60)
    print("1단계: 진단테스트 요약 → 2단계: 유사문항 생성 → 3단계: 힌트/정답 판단")
    print("="*60)

    try:
        # === 1단계: 진단테스트 요약 ===
        print("\n📊 1단계: 진단테스트 요약")
        print("-" * 40)
        learner_id = input("학습자 ID 입력: ").strip()
        session_id = input("세션 ID 입력: ").strip()

        session_handler = SessionHandler()
        result1 = session_handler.handle(learner_id, session_id, [])

        print(f"\n✅ 진단 결과:")
        print(result1['feedback'])

        # 보충이 필요한 개념 추출
        weakest_concepts = result1.get('weakest_concepts', [])
        print(f"\n📋 보충이 필요한 개념: {', '.join(weakest_concepts) if weakest_concepts else '없음'}")

        # 연속 학습 세션 시작
        continuous_handler = ContinuousLearningHandler()
        learning_session = session_manager.create_session(learner_id, session_id, weakest_concepts)

        # 진단테스트 후 선택지 표시
        print(f"\n🎯 진단테스트가 완료되었습니다! 다음 중 하나를 선택해주세요:")
        print("-" * 60)
        
        # 진단테스트 선택지 표시
        action, data = display_quick_replies(result1.get('quick_replies', []))
        
        # 선택된 액션 처리
        result = continuous_handler.handle_user_action(
            learner_id, session_id, action, None, data
        )

        print(f"\n🤖 AI: {result['feedback']}")

        # 문제 정보 표시
        if 'generated_question_data' in result:
            print(f"\n📌 정답: {result['generated_question_data']['correct_answer']}")
            print(f"📖 해설: {result['generated_question_data']['explanation']}")

        # 메인 대화 루프
        while True:
            # 빠른 선택지 표시
            action, data = display_quick_replies(result.get('quick_replies', []))

            if action == "text_input":
                user_input = data
                if user_input.lower() in ['quit', '종료', 'exit', 'q']:
                    action = "end_session"
                    user_input = ""
            else:
                user_input = ""

            # 액션 처리
            result = continuous_handler.handle_user_action(
                learner_id, session_id, action, data, user_input
            )

            if 'error' in result:
                print(f"❌ 오류: {result['error']}")
                continue

            print(f"\n🤖 AI: {result['feedback']}")

            # 새 문제 정보 표시
            if 'generated_question_data' in result:
                print(f"\n📌 정답: {result['generated_question_data']['correct_answer']}")
                print(f"📖 해설: {result['generated_question_data']['explanation']}")

            # 정답 분석 정보 표시
            if 'answer_analysis' in result:
                analysis = result['answer_analysis']
                if analysis.get('is_correct'):
                    print("🎉 정답을 인식했습니다!")
                elif analysis.get('is_partial_correct'):
                    print("🎯 부분 정답을 인식했습니다!")
                elif analysis.get('has_good_approach'):
                    print("👍 좋은 접근 방법입니다!")

            # 세션 종료 확인
            if result.get('is_session_ended'):
                break
            
            # 새로운 진단테스트 시작 확인
            if action == "new_diagnosis":
                print("\n🔄 새로운 진단테스트를 시작합니다!")
                print("=" * 60)
                
                # 새로운 학습자 정보 입력
                new_learner_id = input("새로운 학습자 ID 입력: ").strip()
                new_session_id = input("새로운 세션 ID 입력: ").strip()
                
                if new_learner_id and new_session_id:
                    # 새로운 진단테스트 실행
                    new_result1 = session_handler.handle(new_learner_id, new_session_id, [])
                    
                    print(f"\n✅ 새로운 진단 결과:")
                    print(new_result1['feedback'])
                    
                    # 새로운 보충 개념 추출
                    new_weakest_concepts = new_result1.get('weakest_concepts', [])
                    print(f"\n📋 새로운 보충이 필요한 개념: {', '.join(new_weakest_concepts) if new_weakest_concepts else '없음'}")
                    
                    # 새로운 연속 학습 세션 시작
                    new_learning_session = session_manager.create_session(new_learner_id, new_session_id, new_weakest_concepts)
                    
                    # 새로운 진단테스트 선택지 표시
                    print(f"\n🎯 새로운 진단테스트가 완료되었습니다! 다음 중 하나를 선택해주세요:")
                    print("-" * 60)
                    
                    # 새로운 진단테스트 선택지 표시
                    new_action, new_data = display_quick_replies(new_result1.get('quick_replies', []))
                    
                    # 새로운 선택된 액션 처리
                    result = continuous_handler.handle_user_action(
                        new_learner_id, new_session_id, new_action, None, new_data
                    )
                    
                    # 학습자 ID와 세션 ID 업데이트
                    learner_id = new_learner_id
                    session_id = new_session_id
                    
                    print(f"\n🤖 AI: {result['feedback']}")
                    
                    # 새 문제 정보 표시
                    if 'generated_question_data' in result:
                        print(f"\n📌 정답: {result['generated_question_data']['correct_answer']}")
                        print(f"📖 해설: {result['generated_question_data']['explanation']}")
                else:
                    print("❌ 새로운 학습자 ID와 세션 ID를 입력해주세요.")
                    continue

        # 최종 세션 요약
        if 'session_summary' in result:
            summary = result['session_summary']
            print(f"\n📊 최종 학습 통계:")
            print(f"✅ 총 문제 수: {summary.get('total_problems_solved', 0)}개")
            print(f"💡 사용한 힌트: {summary.get('total_hints_used', 0)}개")
            print(f"⏱️ 학습 시간: {summary.get('session_duration_minutes', 0)}분")

        print("\n🎓 연속 학습 세션이 완료되었습니다!")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("💡 DB 연결 상태와 입력한 learner_id, session_id를 확인해주세요.")


if __name__ == "__main__":
    main()