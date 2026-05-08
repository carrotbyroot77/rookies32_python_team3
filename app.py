import threading
import schedule
import time
import copy

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os

from oil_api import (
    get_avg_oil_price,
    get_low_top20,
    get_price_drop_list,
    get_nearby_list,
    get_sido_avg_prices,
    get_low_price_stations
)
from news_finder import get_all_oil_news
from email_service import send_oil_summary, send_scheduled_report
from algorithm import get_transit_recommendation
from config import AREAS, PRODUCTS, AREA_CODES, PRODUCT_CODES

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "oil_project_secret")

SEND_TIME = "12:03"

visit_tracker = {}


def apply_fake_inflation(oil_list, visit_count):
    if visit_count <= 1:
        return oil_list

    oil_list       = copy.deepcopy(oil_list)
    inflation_rate = (visit_count - 1) * 30.0

    for oil in oil_list:
        try:
            raw_price      = oil.get("PRICE", "0")
            original_price = float(str(raw_price).replace(',', ''))
            fake_price     = original_price + inflation_rate
            oil["PRICE"]   = f"{int(fake_price):,}"
        except (ValueError, TypeError, AttributeError):
            pass

    return oil_list


# ── 스케줄러 ──
def send_daily_report():
    print("📧 유가 리포트 자동 발송 시작...")
    try:
        send_scheduled_report()
    except Exception as e:
        print(f"❌ 자동 발송 오류: {e}")


def run_scheduler():
    schedule.every().day.at(SEND_TIME).do(send_daily_report)
    print(f"⏰ 매일 {SEND_TIME}에 유가 리포트를 자동 발송합니다.")
    while True:
        schedule.run_pending()
        time.sleep(30)


scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


# ── 라우트 ──
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if email:
            session["user_email"] = email
            return redirect(url_for("index"))
    session.clear()
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    user_email = session.get("user_email")
    if not user_email:
        return redirect(url_for("login"))

    visit_tracker[user_email] = visit_tracker.get(user_email, 0) + 1
    visit_count = visit_tracker[user_email]

    area   = request.args.get("area", "")
    prodcd = request.args.get("prodcd", "B027")
    count  = request.args.get("count", "10")

    stations        = []
    sido_avg_prices = []
    updated_at      = ""
    summary         = {}
    oil_news        = []
    avg_list        = []
    low_top20_list  = []
    drop_list       = []
    transit_info    = {}
    error_msg       = None

    try:
        oil_data        = get_low_price_stations(area=area if area else "01", prodcd=prodcd, cnt=count)
        stations        = oil_data["stations"]
        updated_at      = oil_data["updated_at"]
        summary         = oil_data["summary"]
        sido_avg_prices = get_sido_avg_prices(prodcd=prodcd)

        avg_list       = get_avg_oil_price()
        low_top20_list = get_low_top20(prodcd=prodcd, area=area)

        avg_list       = apply_fake_inflation(avg_list, visit_count)
        low_top20_list = apply_fake_inflation(low_top20_list, visit_count)

        drop_list    = get_price_drop_list(avg_list)
        transit_info = get_transit_recommendation(avg_list)

    except Exception as e:
        error_msg = f"유가 API 조회 중 오류 발생: {e}"

    try:
        oil_news = get_all_oil_news()
    except Exception:
        oil_news = []

    return render_template(
        "index.html",
        stations        = stations,
        sido_avg_prices = sido_avg_prices,
        updated_at      = updated_at,
        summary         = summary,
        oil_news        = oil_news,
        selected_area   = area,
        selected_prodcd = prodcd,
        selected_count  = count,
        area_codes      = AREA_CODES,
        product_codes   = PRODUCT_CODES,
        avg_list        = avg_list,
        low_top20_list  = low_top20_list,
        drop_list       = drop_list,
        transit_info    = transit_info,
        areas           = AREAS,
        prod_list       = PRODUCTS,
        update_time     = datetime.now().strftime("%Y-%m-%d %H:%M"),
        user_email      = user_email,
        error_msg       = error_msg,
    )


@app.route("/send-email", methods=["POST"])
def send_email():
    user_email = session.get("user_email")
    if not user_email:
        return jsonify({"success": False, "message": "로그인이 필요합니다."})

    visit_count = visit_tracker.get(user_email, 1)

    try:
        avg_list       = apply_fake_inflation(get_avg_oil_price(), visit_count)
        low_top20_list = apply_fake_inflation(get_low_top20(), visit_count)
        news_list      = get_all_oil_news()
        send_oil_summary(user_email, avg_list, low_top20_list, visit_count, news_list)
        return jsonify({"success": True, "message": f"{user_email} 으로 리포트 발송 완료!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"발송 실패: {e}"})


@app.route("/nearby", methods=["POST"])
def nearby():
    body   = request.json
    lat    = body.get('lat')
    lon    = body.get('lon')
    radius = body.get('radius', 2000)
    prodcd = body.get('prodcd', 'B027')
    sort   = body.get('sort', 1)
    return jsonify(get_nearby_list(lat, lon, radius, prodcd, sort))


@app.route("/send-report")
def manual_send():
    send_daily_report()
    return "✅ 자동발송 테스트 완료!", 200


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)