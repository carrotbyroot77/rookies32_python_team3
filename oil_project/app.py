from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import os

from oil_api import get_avg_oil_price, get_low_top20, get_price_drop_list, get_nearby_list
from email_service import send_oil_summary
from news_api import get_oil_news
from config import AREAS, PRODUCTS
from algorithm import get_transit_recommendation  # 새로 추가된 알고리즘 모듈

app = Flask(__name__)
# 세션을 사용하기 위한 시크릿 키 설정 (로컬용)
app.secret_key = "team3_dark_pattern_secret"

# 😈 다크 패턴: 방문 횟수 추적을 위한 로컬 딕셔너리
visit_tracker = {}

def apply_fake_inflation(oil_list, visit_count):
    """방문 횟수에 따라 기름값을 몰래 인상하는 함수"""
    if visit_count <= 1:
        return oil_list
    
    # 1회 방문이 늘어날 때마다 리터당 30원씩 몰래 인상
    inflation_rate = (visit_count - 1) * 30.0

    for oil in oil_list:
        try:
            # 🛠️ 수정된 부분: API에서 숫자가 오든 문자가 오든 안전하게 문자열로 변환 후 처리
            raw_price = oil.get("PRICE", "0")
            original_price = float(str(raw_price).replace(',', ''))
            
            fake_price = original_price + inflation_rate
            # 깔끔하게 콤마가 포함된 정수 형태의 문자열로 덮어쓰기
            oil["PRICE"] = f"{int(fake_price):,}" 
        except (ValueError, TypeError, AttributeError):
            pass # 변환할 수 없는 가격 정보면 패스
            
    return oil_list

@app.route("/login", methods=["GET", "POST"])
def login():
    """최초 접속 시 이메일을 강제로 입력받는 페이지"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if email:
            session["user_email"] = email
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/", methods=["GET"])
def index():
    """메인 페이지 : 로그인 확인 및 다크 패턴 적용"""
    user_email = session.get("user_email")
    if not user_email:
        # 이메일이 없으면 강제로 로그인 페이지로 튕겨냄
        return redirect(url_for("login"))

    # 방문 횟수 카운트 증가
    if user_email in visit_tracker:
        visit_tracker[user_email] += 1
    else:
        visit_tracker[user_email] = 1
        
    visit_count = visit_tracker[user_email]

    try:
        prodcd = request.args.get("prodcd", "B027")
        area   = request.args.get("area", "")

        # 실제 Opinet API 호출
        avg_list       = get_avg_oil_price()
        low_top20_list = get_low_top20(prodcd, area)

        # 😈 다크 패턴 적용: 방문 횟수가 2회 이상이면 가격 부풀리기 실행!
        avg_list = apply_fake_inflation(avg_list, visit_count)
        low_top20_list = apply_fake_inflation(low_top20_list, visit_count)

        # 🚀 세희님 파트: 부풀려진 평균 유가로 대중교통 추천 지수 계산
        transit_info = get_transit_recommendation(avg_list)

        drop_list = get_price_drop_list(avg_list)
        news_list = get_oil_news()
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        return render_template(
            "index.html",
            avg_list        = avg_list,
            low_top20_list  = low_top20_list,
            drop_list       = drop_list,
            news_list       = news_list,
            selected_prodcd = prodcd,
            selected_area   = area,
            areas           = AREAS,
            prod_list       = PRODUCTS,
            update_time     = update_time,
            user_email      = user_email,
            transit_info    = transit_info
        )

    except Exception as e:
        return f"에러 발생 : {e}"

@app.route("/send-email", methods=["POST"])
def send_email():
    """이메일 발송 라우트"""
    user_email = session.get("user_email")
    if not user_email:
        return jsonify({ "success": False, "message": "로그인이 필요합니다." })

    visit_count = visit_tracker.get(user_email, 1)

    try:
        # 이메일 발송용 데이터 (다크 패턴으로 부풀려진 데이터 전송)
        avg_list       = apply_fake_inflation(get_avg_oil_price(), visit_count)
        low_top20_list = apply_fake_inflation(get_low_top20(), visit_count)

        # email_service에 visit_count를 넘겨주어 경고 메시지를 띄움
        send_oil_summary(user_email, avg_list, low_top20_list, visit_count)

        return jsonify({ "success": True, "message": f"{user_email} 으로 리포트 발송 완료!" })

    except Exception as e:
        return jsonify({ "success": False, "message": f"발송 실패 : {e}" })

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("login"))

@app.route("/nearby", methods=["POST"])
def nearby():
    body = request.json
    lat = body.get('lat')
    lon = body.get('lon')
    radius = body.get('radius', 2000)
    prodcd = body.get('prodcd', 'B027')
    sort = body.get('sort', 1)
    
    response = get_nearby_list(lat, lon, radius, prodcd, sort)
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)