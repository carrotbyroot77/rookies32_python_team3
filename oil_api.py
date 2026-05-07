import os
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPINET_API_KEY")

BASE_URL = "https://www.opinet.co.kr/api"


def check_api_key():

    if not API_KEY:
        raise ValueError(
            ".env에 OPINET_API_KEY 값이 없습니다."
        )


def request_opinet(endpoint, parameters):

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

    return data.get("RESULT", {}).get("OIL", [])


def get_avg_oil_price():

    parameters = {
        "code": API_KEY,
        "out": "json"
    }

    return request_opinet(
        "avgAllPrice.do",
        parameters
    )


def get_low_top20(
    prodcd="B027",
    area=""
):

    parameters = {
        "code": API_KEY,
        "out": "json",
        "prodcd": prodcd,
        "area": area,
        "cnt": 20
    }

    return request_opinet(
        "lowTop10.do",
        parameters
    )