# Roblox 게임 시장조사

이 저장소는 Roblox 게임 후보 발굴을 위해 수집한 공개 자료와 Python 분석을 보관합니다. 확인 사실·계산치·추정치를 구분합니다.

## 먼저 읽기
- [시장조사 보고서](research/REPORT.md)
- [다음 작업 핸드오프](research/HANDOFF.md)

## 자료 및 코드
- [게임별 공개 지표](research/data/games.csv)
- [일별 플레이어 기록](research/data/daily_history.csv)
- [분석 요약 JSON](research/data/analysis_summary.json)
- [수집 코드](research/scripts/collect_analyze.py)
- [기록 보완 코드](research/scripts/fill_history.py)
- [재현 분석 코드](research/scripts/analyze_dataset.py)

## 한계
표본은 RoWatcher 장르 필터별 게임 25개이며 Roblox 전체의 무작위 표본이 아닙니다. 149개 게임의 일별 기록은 차트 순위 체류 기간이나 실제 손익을 뜻하지 않습니다. 142개 수익 필드는 제3자 모델 추정치입니다.
