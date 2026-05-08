import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OPINET_KEY = os.getenv("OPINET_KEY") or os.getenv("OPINET_API_KEY")
BASE_URL   = "https://www.opinet.co.kr/api"

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


def check_api_key():
    if not OPINET_KEY:
        raise ValueError(".env 파일에 OPINET_KEY가 없습니다.")


def get_brand_name(code):
    return BRAND_MAP.get(code, code)


# ── 내 코드: 지역별 최저가 주유소 ──
def get_low_price_stations(area="01", prodcd="B027", cnt="10"):
    check_api_key()
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
    oil_list = response.json().get("RESULT", {}).get("OIL", [])

    result = []
    for oil in oil_list:
        price = int(str(oil.get("PRICE", 0)).replace(",", ""))
        result.append({
            "name":        oil.get("OS_NM", "이름 없음"),
            "brand":       get_brand_name(oil.get("POLL_DIV_CD", "")),
            "price":       price,
            "price_text":  f"{price:,}원",
            "address":     oil.get("NEW_ADR", "주소 없음"),
            "uni_id":      oil.get("UNI_ID", ""),
            "OS_NM":       oil.get("OS_NM", ""),
            "PRICE":       f"{price:,}",
            "POLL_DIV_CD": oil.get("POLL_DIV_CD", ""),
            "NEW_ADR":     oil.get("NEW_ADR", ""),
            "VAN_ADR":     oil.get("VAN_ADR", ""),
        })

    prices    = [s["price"] for s in result]
    avg_price = sum(prices) / len(prices) if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0

    return {
        "updated_at": datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"),
        "stations": result,
        "summary": {
            "count":     len(result),
            "avg_price": f"{avg_price:,.0f}원",
            "min_price": f"{min_price:,}원",
            "max_price": f"{max_price:,}원"
        }
    }


# ── 내 코드: 시도별 평균 유가 (전국 제외) ──
def get_sido_avg_prices(prodcd="B027"):
    check_api_key()
    url = f"{BASE_URL}/avgSidoPrice.do"
    params = {"code": OPINET_KEY, "out": "json"}
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    oil_list = response.json().get("RESULT", {}).get("OIL", [])

    result = []
    for oil in oil_list:
        if oil.get("PRODCD") == prodcd:
            sido = oil.get("SIDONM", "")

            if sido == "전국":  # 전국 행 제외 (DIFF 값 오류)
                continue

            price = float(oil.get("PRICE", 0))
            diff  = float(oil.get("DIFF", 0))
            result.append({
                "sido":       sido,
                "price":      price,
                "price_text": f"{price:,.2f}원",
                "diff":       diff,
                "diff_text":  f"{diff:+.2f}원"
            })
    return result


# ── 팀원 코드: 전국 평균 유가 ──
def get_avg_oil_price():
    check_api_key()
    url = f"{BASE_URL}/avgAllPrice.do"
    params = {"code": OPINET_KEY, "out": "json"}
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    return response.json().get("RESULT", {}).get("OIL", [])


# ── 팀원 코드: 전국 최저가 TOP20 ──
def get_low_top20(prodcd="B027", area=""):
    check_api_key()
    url = f"{BASE_URL}/lowTop10.do"
    params = {
        "code":   OPINET_KEY,
        "out":    "json",
        "prodcd": prodcd,
        "area":   area,
        "cnt":    20
    }
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    return response.json().get("RESULT", {}).get("OIL", [])


# ── 팀원 코드: 가격 하락 유종 필터 ──
def get_price_drop_list(avg_list):
    return list(filter(
        lambda oil: float(oil.get("DIFF", 0)) < 0,
        avg_list
    ))