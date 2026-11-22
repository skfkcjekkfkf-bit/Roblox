# 핸드오프: Roblox 시장조사 후속 작업

## 목표
공개 데이터의 반복 관측으로 Roblox에서 만들 만한 게임 유형을 찾습니다. 아직 아이디어를 최종 확정하지 않습니다. Python이 데이터 집계·통계·시계열 비교를 수행하고, LLM은 수집 설계와 해석을 맡습니다.

## 현재 저장물
- research/data/games.csv: 게임 150개, 트래커 장르 6개별 25개. 단일 시점 공개 지표.
- research/data/daily_history.csv: 149개 게임의 일별 플레이어 기록 8,809행. 날짜 범위 2026-08-25–2026-11-21.
- research/data/analysis_summary.json: 분석 결과.
- research/scripts/collect_analyze.py: 최초 수집과 분석.
- research/scripts/fill_history.py: 역사 자료 누락분 재요청.
- research/scripts/analyze_dataset.py: 저장 CSV 재현 분석.

## 주의사항
1. 표본은 트래커 API가 장르 필터별 반환한 25개이지 Roblox 전체 무작위 표본이 아닙니다.
2. 트래커 장르 레이블은 검증된 게임플레이 메커닉 분류가 아닙니다. 이름만으로 메커닉을 단정하지 마세요.
3. 142개 월수익 수치는 제3자 모델 추정치이며 실제 매출·순이익이 아닙니다. 표본 내 검증된 실제 손익은 0건입니다.
4. 129/147이 관측 기간 내 최고 일평균보다 낮았다는 결과는 실패 판정이 아닙니다.
5. 일별 플레이어 수는 차트 순위가 아닙니다. 유명했던 기간이나 차트 체류 일수로 바꾸어 말하지 마세요.
6. 업데이트 이력·개발비·광고비·경험별 실제 수입은 충분히 확보하지 못했습니다.
7. 상관관계는 원인을 증명하지 않습니다. 표본 편향과 기록 길이·시간대 차이를 보고하세요.

## 다음 담당자의 순서
1. README.md와 research/REPORT.md를 읽고 기존 결과를 재사용합니다.
2. 차트 순위의 날짜별 보관 자료를 확인할 수 있는지 출처·커버리지·이용 조건을 확인합니다. 자료가 있을 때만 차트 일수와 연속 차트일수를 계산합니다.
3. 공식 Roblox 게임 설명을 확인해 플레이 메커닉을 코드북으로 분류합니다. 애매하면 Unknown으로 둡니다.
4. 신작/성숙한 게임, 현재 동접 구간, 기록 길이를 구분해 유사 게임 그룹을 만듭니다. 성공작만 고르지 않습니다.
5. Python으로 그룹별 중앙값과 시계열 지표를 분석하고 CSV·코드·결과를 함께 갱신합니다.
6. 근거가 충분할 때만 최대 3개 아이디어를 제안합니다. 참고작, 부진/하락 사례, 혼자 만들 MVP 난이도, 수익화 조건, 첫 검증 가설을 적습니다.
7. 실제 게임별 수익이 없으면 DevEx 환율로 수익을 계산하지 않습니다. 추정은 모델·가정·범위를 따로 표시합니다.

## 출처
- Roblox Games API: https://create.roblox.com/docs/cloud/reference/domains/games
- RoWatcher API/CSV: https://rowatcher.com/developers
- RoWatcher 데이터 설명: https://rowatcher.com/data-sources
- Roblox DevEx: https://en.help.roblox.com/en-us/articles/203314100-Developer-Exchange-DevEx-Overview-How-to-Submit-Requirements
