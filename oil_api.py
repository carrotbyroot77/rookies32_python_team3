import os
import requests

from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OPINET_KEY = os.getenv("OPINET_KEY")

BASE_URL = "https://www.opinet.co.kr/api"

BRAND_MAP = {
    "SKE": "SK에너지",
    "GSC": "GS칼텍스",
    "HDO": "현대오일뱅크",
    "SOL": "S-OIL",
    "RTO": "알뜰주유소",
    "RTX": "자가상표",
    "NHO": "농협",
    "ETC": "기타"
}


def get_brand_name(code):
    return BRAND_MAP.get(code, code)


def get_low_price_stations(area="01", prodcd="B027", cnt="10"):
    if not OPINET_KEY:
        raise ValueError(".env 파일에 OPINET_KEY가 없습니다.")

    url = f"{BASE_URL}/lowTop10.do"

    params = {
        "certkey": OPINET_KEY,
        "out": "json",
        "prodcd": prodcd,
        "area": area,
        "cnt": cnt
    }

    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()

    data = response.json()
    oil_list = data.get("RESULT", {}).get("OIL", [])

    result = []

    for oil in oil_list:
        price = int(oil.get("PRICE", 0))

        result.append({
            "name": oil.get("OS_NM", "이름 없음"),
            "brand": get_brand_name(oil.get("POLL_DIV_CD", "")),
            "price": price,
            "price_text": f"{price:,}원",
            "address": oil.get("NEW_ADR", "주소 없음"),
            "uni_id": oil.get("UNI_ID", "")
        })

    prices = [s["price"] for s in result]

    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
    else:
        avg_price = min_price = max_price = 0

    return {
        "updated_at": datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"),
        "stations": result,
        "summary": {
            "count": len(result),
            "avg_price": f"{avg_price:,.0f}원",
            "min_price": f"{min_price:,}원",
            "max_price": f"{max_price:,}원"
        }
    }


def get_sido_avg_prices(prodcd="B027"):
    if not OPINET_KEY:
        raise ValueError(".env 파일에 OPINET_KEY가 없습니다.")

    url = f"{BASE_URL}/avgSidoPrice.do"

    params = {
        "code": OPINET_KEY,
        "out": "json"
    }

    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()

    data = response.json()
    oil_list = data.get("RESULT", {}).get("OIL", [])

    result = []

    for oil in oil_list:
        if oil.get("PRODCD") == prodcd:
            price = float(oil.get("PRICE", 0))
            diff = float(oil.get("DIFF", 0))

            result.append({
                "sido": oil.get("SIDONM", ""),
                "price": price,
                "price_text": f"{price:,.2f}원",
                "diff": diff,
                "diff_text": f"{diff:+.2f}원"
            })

    return result
