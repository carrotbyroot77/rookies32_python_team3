# rookies32_python_team3

## 📦 사용 라이브러리 / API

### Python 외부 라이브러리

| 도구 | 버전 | 기능 |
| :---: | :---: | :--- |
| [Flask](https://flask.palletsprojects.com/) | 3.1.3 | 웹 서버 / 라우팅 / 템플릿 렌더링 / 세션 관리 |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | 1.2.2 | `.env` 파일에서 API 키·이메일 비번 로드 |
| [requests](https://requests.readthedocs.io/) | 2.33.1 | Opinet API HTTP 요청 |
| [feedparser](https://pypi.org/project/feedparser/) | 6.0.12 | SBS·연합뉴스TV RSS 피드 파싱 |
| [schedule](https://schedule.readthedocs.io/) | 1.2.2 | 매일 정해진 시각에 유가 리포트 자동 발송 |
| [pyproj](https://pyproj4.github.io/pyproj/) | 3.7.2 | WGS84 ↔ KATEC 좌표계 변환 (지도 ↔ Opinet) |

<br>
<br>

### Python 내장 모듈

| 도구 | 기능 |
| :---: | :--- |
| `smtplib` | Gmail SMTP 서버로 이메일 송신 |
| `email.mime` | HTML 이메일 본문 / 헤더 구성 |
| `datetime` | 갱신 시각·메일 제목 타임스탬프 표시 |
| `threading` | 스케줄러를 백그라운드 스레드로 실행 |
| `copy` | 다크 패턴 가격 인상 시 원본 보호용 deepcopy |

<br>
<br>

### 외부 API / 서비스

| 도구 | 기능 |
| :---: | :--- |
| [Opinet API](https://www.opinet.co.kr/user/custapi/openApiInfo.do) | 전국 평균 유가 / 시도별 평균 / 최저가 TOP20 / 반경 내 주유소 조회 |
| [Kakao Maps JS SDK](https://apis.map.kakao.com/) | 지도 렌더링 / 마커 표시 / 주소→좌표 변환(Geocoder) |
| Gmail SMTP (`smtp.gmail.com:587`) | 유가 리포트 이메일 발송 |
| SBS 뉴스 RSS | 유가 관련 최신 뉴스 수집 |
| 연합뉴스TV 경제 RSS | 유가 관련 최신 뉴스 수집 |
