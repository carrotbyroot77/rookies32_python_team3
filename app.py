from flask import Flask, render_template, request
from oil_api import get_low_price_stations, get_sido_avg_prices
from news_finder import get_all_oil_news
from config import AREA_CODES, PRODUCT_CODES

app = Flask(__name__)


@app.route("/")
def index():
    area = request.args.get("area", "01")
    prodcd = request.args.get("prodcd", "B027")
    count = request.args.get("count", "10")

    stations = []
    sido_avg_prices = []
    updated_at = ""
    summary = {}
    oil_news = []
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
        error_msg = f"유가 API 조회 중 오류 발생 : {e}"

    try:
        oil_news = get_all_oil_news()
    except Exception as e:
        oil_news = []  # 뉴스 오류는 메인 기능에 영향 안 줌

    return render_template(
        "index.html",
        stations=stations,
        sido_avg_prices=sido_avg_prices,
        updated_at=updated_at,
        summary=summary,
        oil_news=oil_news,
        error_msg=error_msg,
        selected_area=area,
        selected_prodcd=prodcd,
        selected_count=count,
        area_codes=AREA_CODES,
        product_codes=PRODUCT_CODES
    )


if __name__ == "__main__":
    app.run(debug=True)
