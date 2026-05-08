import os
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def send_oil_summary(to_email: str, avg_list: list, low_top20_list: list, visit_count: int) -> None:
    """유가 요약 정보를 이메일로 발송 (다크 패턴 경고 포함)"""

    # 1. SMTP 접속 정보 로드 (.env)
    user_email    = os.getenv("EMAIL_USER")
    user_password = os.getenv("EMAIL_PASS")
    smtp_server   = os.getenv("SMTP_SVR")
    smtp_port     = int(os.getenv("SMTP_PORT"))

    # 2. 메일 메시지 구성
    msg = MIMEMultipart()
    msg['Subject'] = f"[유가 알림] 오늘의 주유 정보 요약 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg['From']    = user_email
    msg['To']      = to_email

    # 3. 전국 평균 유가 테이블 생성
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

    # 4. 최저가 TOP5 테이블 생성 (이메일용 요약)
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

    # 😈 5. 다크 패턴 폭로 메시지 (방문 2회차 이상부터 표시)
    reveal_html = ""
    if visit_count > 1:
        reveal_html = f"""
        <div style="margin-top:40px; padding:20px; background-color:#1a1a1a; color:#00ff00; font-family: 'Courier New', Courier, monospace; border-left: 5px solid #dc2626; border-radius:8px;">
            <h3 style="color:#dc2626; margin-top:0;">⚠️ SYSTEM WARNING: DATA TRACKING DETECTED</h3>
            <p>사실 저희는 당신의 행동을 추적하고 있었습니다.</p>
            <p>당신의 식별자(<strong>{to_email}</strong>)를 분석한 결과, 이 사이트에 총 <strong>{visit_count}회</strong> 접속하신 것을 확인했습니다.</p>
            <p>사이트에 자주 방문한다는 것은 유가 정보가 시급하다는 뜻이므로, <strong>저희는 당신이 접속할 때마다 화면에 보이는 기름값을 몰래 조금씩 인상하고 있었습니다.</strong> (항공권이나 숙박 사이트에서 흔히 쓰이는 다크 패턴 상술입니다.)</p>
            <p>본 메일은 사용자 데이터가 기업의 이익을 위해 어떻게 조작되고 악용될 수 있는지 보여주기 위한 <strong>3조의 기획 프로젝트</strong>입니다. 당신의 데이터는 소중합니다!</p>
        </div>
        """

    # 6. HTML 이메일 본문
    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">

        <h2 style="text-align:center; color:#1e3a8a;">⛽ 오늘의 유가 요약 리포트</h2>
        <p style="text-align:center; color:#777; font-size:14px;">
            기준 시각 : {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </p>

        <div style="background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:20px;">
            <h3 style="color:#111827; border-left:5px solid #2563eb; padding-left:10px;">📊 전국 평균 유가</h3>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr style="background-color:#2563eb; color:white;">
                    <th style="padding:10px;">유종</th><th style="padding:10px;">평균 가격</th><th style="padding:10px;">전일 대비</th>
                </tr>
                {avg_rows}
            </table>
        </div>

        <div style="background:#ffffff; padding:20px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:20px;">
            <h3 style="color:#111827; border-left:5px solid #2563eb; padding-left:10px;">🏆 최저가 주유소 TOP 5</h3>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr style="background-color:#2563eb; color:white;">
                    <th style="padding:10px;">순위</th><th style="padding:10px;">주유소명</th><th style="padding:10px;">가격</th><th style="padding:10px;">주소</th>
                </tr>
                {top5_rows}
            </table>
        </div>

        {reveal_html}

        <p style="text-align:center; font-size:12px; color:#aaa; margin-top:20px;">
            © 2026 유가 정보 서비스 (3조 프로젝트)
        </p>

    </div>
    """

    msg.attach(MIMEText(html_content, 'html'))

    # 7. SMTP 서버 접속 및 발송
    try:
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(user_email, user_password)
            server.send_message(msg)
            print(f"메일 발송 성공 → {to_email}")
    except Exception as e:
        print(f"메일 발송 오류 : {e}")
        raise