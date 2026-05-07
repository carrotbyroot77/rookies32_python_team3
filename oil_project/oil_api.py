import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("OPINET_API_KEY")
BASE_URL = "https://www.opinet.co.kr/api"


def check_api_key() -> None:
    """API 키 존재 여부 확인"""
    if not API_KEY:
        raise ValueError(".env에 OPINET_API_KEY 값이 없습니다.")


def request_opinet(endpoint: str, parameters: dict) -> list:
    """Opinet API 공통 요청 함수

    Args:
        endpoint   : API 엔드포인트
        parameters : 요청 파라미터 딕셔너리

    Returns:
        OIL 데이터 리스트
    """

    check_api_key()

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=parameters,
        timeout=5
    )

    response.raise_for_status()

    print("요청 URL :", response.url)
    print("상태 코드 :", response.status_code)

    data = response.json()

    # # 🚨 여기에 print 문을 추가해서 오피넷의 진짜 속마음을 터미널에 출력해 봅니다!
    # print(f"\n[{endpoint}] API 응답 데이터 확인:", data, "\n")

    return data.get("RESULT", {}).get("OIL", [])


def get_avg_oil_price() -> list:
    """전국 평균 유가 조회"""

    parameters = {
        "code" : API_KEY,
        "out"  : "json"
    }

    return request_opinet("avgAllPrice.do", parameters)


def get_low_top20(prodcd: str = "B027", area: str = "") -> list:
    """지역별 최저가 TOP20 주유소 조회

    Args:
        prodcd : 유종 코드 (기본값: 보통휘발유)
        area   : 지역 코드 (기본값: 전국)
    """

    parameters = {
        "code"   : API_KEY,
        "out"    : "json",
        "prodcd" : prodcd,
        "area"   : area,
        "cnt"    : 20
    }

    return request_opinet("lowTop10.do", parameters)


def get_price_drop_list(avg_list: list) -> list:
    """전일 대비 유가가 하락한 유종만 필터링하여 반환

    Args:
        avg_list : 전국 평균 유가 리스트

    Returns:
        DIFF 값이 음수(하락)인 유종 리스트
    """

    # filter + lambda : 강사님 func_lambda 패턴 적용
    drop_list = list(filter(
        lambda oil: float(oil.get("DIFF", 0)) < 0,
        avg_list
    ))

    return drop_list
