# FirstBloodWins
<br/>

V 0.3
- Issue : 검색 당 한 계정의 최근 20 개의 전적을 불러오는데 걸리는 시간이 대략 17 sec 정도 걸림
- Solve : httpx 를 사용하여 동시에 여러 API 들을 불러옴 <br/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;17 sec -> 11 sec 으로 대략 6초 단축

V 0.2
- Issue : 프로 경기 관련 데이터 중 First Blood 관련 데이터 수집이 현재로선 불가능하므로 일반 랭크 게임 데이터로 대체

V 0.1
- Initial Goal : 프로 경기들의 경기 내역을 모아 각 리그의 팀별 First Blood 확률 계산
- ERD 및 명세서 추후 업데이트 예정

사용 기술 스택 : Python, FastAPI, MongoDB
