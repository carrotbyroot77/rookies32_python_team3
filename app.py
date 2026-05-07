from flask import Flask, render_template, request
from oil_api import get_low_price_stations, get_sido_avg_prices

app = Flask(__name__)

AREA_CODES = {
    "01": "서울",
    "02": "경기",
    "03": "강원",
    "04": "충북",
    "05": "충남",
    "06": "전북",
    "07": "전남",
    "08": "경북",
    "09": "경남",
    "10": "부산",
    "11": "대구",
    "12": "인천",
    "13": "광주",
    "14": "대전",
    "15": "울산",
    "16": "세종",
    "17": "제주"
}

PRODUCT_CODES = {
    "B027": "휘발유",
    "D047": "경유",
    "B034": "고급휘발유",
    "K015": "LPG"
}


@app.route("/")
def index():
    area = request.args.get("area", "05")
    prodcd = request.args.get("prodcd", "B027")
    count = request.args.get("count", "10")

    stations = []
    sido_avg_prices = []
    updated_at = ""
    summary = {}
    error_msg = None

    try:
        oil_data = get_low_price_stations(
            area=area,
            prodcd=prodcd,
            cnt=count
        )

        stations = oil_data["stations"]
        updated_at = oil_data["updated_at"]
        summary = oil_data["summary"]

        sido_avg_prices = get_sido_avg_prices(prodcd=prodcd)

    except Exception as e:
        error_msg = f"API 조회 중 오류 발생 : {e}"

    return render_template(
        "index.html",
        stations=stations,
        sido_avg_prices=sido_avg_prices,
        updated_at=updated_at,
        summary=summary,
        error_msg=error_msg,
        selected_area=area,
        selected_prodcd=prodcd,
        selected_count=count,
        area_codes=AREA_CODES,
        product_codes=PRODUCT_CODES
    )


if __name__ == "__main__":
    app.run(debug=True)