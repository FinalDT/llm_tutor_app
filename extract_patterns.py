"""
DB에서 실제 학습 패턴을 추출하여 파인튜닝용 데이터 생성을 위한 스크립트
"""
import json
import logging
from decimal import Decimal
from database.db_service import DatabaseService

def extract_real_patterns():
    """DB에서 실제 학습 패턴 추출"""
    db_service = DatabaseService()

    try:
        # 1. 개념별 기본 통계 (상위 10개)
        concept_stats_query = """
        SELECT TOP 10 concept_name,
               COUNT(*) as attempts,
               AVG(CAST(is_correct AS FLOAT)) as success_rate,
               AVG(tag_accuracy) as avg_personal_accuracy,
               AVG(global_accuracy) as avg_global_accuracy,
               COUNT(DISTINCT learnerID) as unique_students
        FROM gold.vw_personal_item_enriched
        GROUP BY concept_name
        ORDER BY attempts DESC;
        """

        with db_service.get_connection() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(concept_stats_query)
            concept_rows = cursor.fetchall()

        concepts = []
        for row in concept_rows:
            concepts.append({
                "concept_name": str(row[0]),
                "attempts": int(row[1]),
                "success_rate": round(float(row[2]), 3),
                "avg_personal_accuracy": round(float(row[3]), 3),
                "avg_global_accuracy": round(float(row[4]), 3) if row[4] else 0.0,
                "unique_students": int(row[5])
            })

        # 2. 수준별 분포 (상위 5개 개념만)
        top_5_concepts = [c["concept_name"] for c in concepts[:5]]
        concept_list = "'" + "', '".join(top_5_concepts).replace("'", "''") + "'"

        skill_levels_query = f"""
        SELECT concept_name,
               CASE WHEN tag_accuracy < 0.4 THEN 'low'
                    WHEN tag_accuracy < 0.7 THEN 'medium'
                    ELSE 'high' END as level,
               COUNT(*) as count
        FROM gold.vw_personal_item_enriched
        WHERE concept_name IN ({concept_list})
        GROUP BY concept_name,
                 CASE WHEN tag_accuracy < 0.4 THEN 'low'
                      WHEN tag_accuracy < 0.7 THEN 'medium'
                      ELSE 'high' END;
        """

        with db_service.get_connection() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(skill_levels_query)
            level_rows = cursor.fetchall()

        skill_levels = {}
        for row in level_rows:
            concept = str(row[0])
            if concept not in skill_levels:
                skill_levels[concept] = {}
            skill_levels[concept][str(row[1])] = int(row[2])

        # 3. 실수 패턴 (틀린 문제만)
        mistakes_query = f"""
        SELECT concept_name,
               ROUND(AVG(tag_accuracy), 3) as avg_accuracy_when_wrong,
               COUNT(*) as mistake_count
        FROM gold.vw_personal_item_enriched
        WHERE is_correct = 0 AND concept_name IN ({concept_list})
        GROUP BY concept_name
        ORDER BY mistake_count DESC;
        """

        with db_service.get_connection() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(mistakes_query)
            mistake_rows = cursor.fetchall()

        common_mistakes = []
        for row in mistake_rows:
            common_mistakes.append({
                "concept_name": str(row[0]),
                "avg_accuracy_when_wrong": round(float(row[1]), 3) if row[1] else 0.0,
                "mistake_count": int(row[2])
            })

        # 4. 결과 저장
        patterns = {
            "extraction_summary": {
                "total_concepts_analyzed": len(concepts),
                "top_concepts_for_training": len(top_5_concepts),
                "total_mistake_patterns": len(common_mistakes),
                "data_source": "실제 DB 쿼리 결과"
            },
            "concepts": concepts[:5],  # 상위 5개만 저장
            "skill_levels": skill_levels,
            "common_mistakes": common_mistakes
        }

        with open("real_patterns.json", "w", encoding="utf-8") as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)

        print("✅ real_patterns.json 생성 완료 (실제 DB 데이터 기반)")
        print(f"📊 분석된 개념: {len(concepts)}개")
        print(f"🎯 훈련용 선택된 개념: {len(top_5_concepts)}개")
        print(f"📈 실수 패턴: {len(common_mistakes)}개")

        # 선택된 상위 5개 개념 출력
        print("\n🔥 실제 DB에서 선택된 상위 5개 개념:")
        for i, concept in enumerate(concepts[:5], 1):
            print(f"{i}. {concept['concept_name']} (시도: {concept['attempts']}회, 성공률: {concept['success_rate']*100:.1f}%)")

        # 수준별 분포 출력
        print("\n📊 수준별 학생 분포:")
        for concept, levels in skill_levels.items():
            print(f"  {concept}:")
            for level, count in levels.items():
                print(f"    {level}: {count}명")

        return patterns

    except Exception as e:
        logging.error(f"패턴 추출 실패: {e}")
        print(f"❌ 오류 발생: {e}")
        raise

if __name__ == "__main__":
    extract_real_patterns()