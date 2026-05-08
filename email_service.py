import os
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS") or os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASS")
OPINET_KEY     = os.getenv("OPINET_KEY") or os.getenv("OPINET_API_KEY")
BASE_URL       = "https://www.opinet.co.kr/api"

MY_X = os.getenv("MY_LOCATION_X", "311669.9")
MY_Y = os.getenv("MY_LOCATION_Y", "551556.4")

BRAND_NAME_MAP = {
    "SKE": "SK에너지",
    "GSC": "GS칼텍스",
    "SOL": "S-OIL",
    "HDO": "현대오일뱅크",
    "ETC": "알뜰/비브랜드",
    "RTO": "자영 알뜰주유소"
}


def get_nearby_stations():
    """반경 5km 내 주변 주유소 조회"""
    url = f"{BASE_URL}/aroundAll.do"
    params = {
        "code":   OPINET_KEY,
        "out":    "json",
        "x":      MY_X,
        "y":      MY_Y,
        "radius": 5000,
        "sort":   2,
        "prodcd": "B027"
    }
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
    stations = response.json().get("RESULT", {}).get("OIL", [])
    for s in stations:
        s["DISTANCE"] = float(s["DISTANCE"])
        s["PRICE"]    = int(str(s["PRICE"]).replace(",", ""))
    return stations


def calculate_brand_stats(stations):
    """브랜드별 평균 가격 계산"""
    brand_stat = {}
    for s in stations:
        code  = s["POLL_DIV_CD"]
        price = s["PRICE"]
        if code not in brand_stat:
            brand_stat[code] = [0, 0]
        brand_stat[code][0] += price
        brand_stat[code][1] += 1

    result = []
    for code, (total, count) in brand_stat.items():
        name = BRAND_NAME_MAP.get(code, code)
        result.append({"name": name, "code": code, "avg": total / count})
    return result


def send_scheduled_report() -> None:
    """스케줄러 자동발송 - dd.py 스타일 텍스트 메일"""

    # 1. 전국 평균 가격
    avg_response = requests.get(f"{BASE_URL}/avgAllPrice.do", params={"code": OPINET_KEY, "out": "json"}, timeout=5)
    avg_list     = avg_response.json().get("RESULT", {}).get("OIL", [])

    national_text = ""
    for item in avg_list:
        name     = item['PRODNM']
        price    = item['PRICE']
        diff     = item['DIFF']
        diff_str = f"+{diff}" if float(diff) > 0 else str(diff)
        national_text += f"[{name}] 현재가: {price}원 (변동: {diff_str})\n"

    # 2. 주변 주유소
    stations = get_nearby_stations()

    if not stations:
        print("❌ 주변 주유소 데이터 없음")
        return

    cheapest    = min(stations, key=lambda s: s["PRICE"])
    nearest     = min(stations, key=lambda s: s["DISTANCE"])
    brand_stats = calculate_brand_stats(stations)

    brand_text = ""
    for b in brand_stats:
        brand_text += f"{b['name']}({b['code']}) 평균: {b['avg']:,.2f}원\n"

    # 3. 텍스트 본문 구성
    content = f"""
⛽ 오늘의 유가 리포트

📊 [전국 평균 가격]
{national_text}
----------------------------------------
⛽ [반경 5km 내 최저가 주유소]
이름: {cheapest['OS_NM']}
거리: {cheapest['DISTANCE'] / 1000:.2f}km
가격: {cheapest['PRICE']:,}원

📍 [가장 가까운 주유소]
이름: {nearest['OS_NM']}
거리: {nearest['DISTANCE'] / 1000:.2f}km
가격: {nearest['PRICE']:,}원

----------------------------------------
🏷️ [내 주변 브랜드별 평균 가격]
{brand_text}
"""

    msg           = MIMEText(content)
    msg["Subject"] = "⛽ 오늘의 유가 리포트"
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = EMAIL_ADDRESS

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
        print("✅ 유가 리포트 자동발송 완료!")
        print(content)


def send_oil_summary(to_email: str, avg_list: list, low_top20_list: list, visit_count: int, news_list: list = []) -> None:
    """즉시발송 버튼 - HTML 이메일 (전국평균 + TOP5 + 뉴스 + 다크패턴)"""

    # 1. 전국 평균 유가 테이블
    avg_rows = "".join([
        f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #eee;">{oil.get('PRODNM', '')}</td>
            <td style="padding:10px; border-bottom:1px solid #eee; color:#dc2626; font-weight:bold;">{oil.get('PRICE', '')}원</td>
            <td style="padding:10px; border-bottom:1px solid #eee;">{oil.get('DIFF', '')}</td>
        </tr>
        """
        for oil in avg_list
    ])

    # 2. 최저가 TOP5 테이블
    top5_rows = "".join([
        f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #eee;">{idx + 1}</td>
            <td style="padding:10px; border-bottom:1px solid #eee;">{oil.get('OS_NM', '')}</td>
            <td style="padding:10px; border-bottom:1px solid #eee; color:#dc2626; font-weight:bold;">{oil.get('PRICE', '')}원</td>
            <td style="padding:10px; border-bottom:1px solid #eee;">{oil.get('NEW_ADR') or oil.get('VAN_ADR', '')}</td>
        </tr>
        """
        for idx, oil in enumerate(low_top20_list[:5])
    ])

    # 3. 뉴스 섹션
    news_html = ""
    if news_list:
        news_items = "".join([
            f"""
            <div style="padding:12px 0; border-bottom:1px solid #eee;">
                <a href="{news.get('link', '')}" style="font-weight:bold; color:#1e3a8a; text-decoration:none; font-size:15px;">
                    {news.get('title', '')}
                </a>
                <p style="margin:5px 0 0; font-size:12px; color:#6b7280;">
                    [{news.get('credit', '')}] {news.get('published', '')}
                </p>
                <p style="margin:5px 0 0; font-size:13px; color:#555;">
                    {news.get('summary', '')[:100]}...
                </p>
            </div>
            """
            for news in news_list[:5]
        ])
        news_html = f"""
        <div style="background:#fff; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:20px;">
            <h3 style="color:#111827; border-left:5px solid #2563eb; padding-left:10px;">📰 유가 관련 최신 뉴스</h3>
            {news_items}
        </div>
        """

    # 4. 다크패턴 폭로 메시지 (2회차 이상)
    reveal_html = ""
    if visit_count > 1:
        reveal_html = f"""
        <div style="margin-top:40px; padding:20px; background-color:#1a1a1a; color:#00ff00;
                    font-family:'Courier New',Courier,monospace; border-left:5px solid #dc2626; border-radius:8px;">
            <h3 style="color:#dc2626; margin-top:0;">⚠️ SYSTEM WARNING: DATA TRACKING DETECTED</h3>
            <p>사실 저희는 당신의 행동을 추적하고 있었습니다.</p>
            <p>당신의 식별자(<strong>{to_email}</strong>)를 분석한 결과,
               이 사이트에 총 <strong>{visit_count}회</strong> 접속하신 것을 확인했습니다.</p>
            <p>사이트에 자주 방문할수록 화면에 보이는 기름값을 몰래 조금씩 인상하고 있었습니다.
               (항공권이나 숙박 사이트에서 흔히 쓰이는 다크 패턴 상술입니다.)</p>
            <p>본 메일은 사용자 데이터가 기업의 이익을 위해 어떻게 조작될 수 있는지 보여주기 위한
               <strong>팀 프로젝트</strong>입니다. 당신의 데이터는 소중합니다!</p>
        </div>
        """

    # 5. HTML 이메일 본문
    html_content = f"""
    <div style="font-family:Arial,sans-serif; background-color:#f4f6f9; padding:20px;">
        <h2 style="text-align:center; color:#1e3a8a;">⛽ 오늘의 유가 요약 리포트</h2>
        <p style="text-align:center; color:#777; font-size:14px;">기준 시각 : {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

        <div style="background:#fff; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:20px;">
            <h3 style="color:#111827; border-left:5px solid #2563eb; padding-left:10px;">📊 전국 평균 유가</h3>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr style="background-color:#2563eb; color:white;">
                    <th style="padding:10px;">유종</th>
                    <th style="padding:10px;">평균 가격</th>
                    <th style="padding:10px;">전일 대비</th>
                </tr>
                {avg_rows}
            </table>
        </div>

        <div style="background:#fff; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:20px;">
            <h3 style="color:#111827; border-left:5px solid #2563eb; padding-left:10px;">🏆 최저가 주유소 TOP 5</h3>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr style="background-color:#2563eb; color:white;">
                    <th style="padding:10px;">순위</th>
                    <th style="padding:10px;">주유소명</th>
                    <th style="padding:10px;">가격</th>
                    <th style="padding:10px;">주소</th>
                </tr>
                {top5_rows}
            </table>
        </div>

        {news_html}

        {reveal_html}

        <p style="text-align:center; font-size:12px; color:#aaa; margin-top:20px;">
            © 2026 유가 정보 서비스 (팀 프로젝트)
        </p>
    </div>
    """

    msg = MIMEMultipart()
    msg["Subject"] = f"⛽ 오늘의 유가 리포트 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = to_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        print(f"✅ 메일 발송 성공 → {to_email}")