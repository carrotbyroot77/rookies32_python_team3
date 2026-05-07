def get_transit_recommendation(avg_list: list) -> dict:
    """
    기름값 지수를 계산하여 대중교통 이용을 추천하는 알고리즘
    (다크 패턴으로 부풀려진 가격을 그대로 반영함)
    """
    # 보통휘발유 가격 찾기
    gasoline_price = 1600.0  # 파싱 실패 시 기본값
    
    for oil in avg_list:
        # 🛠️ 수정: 이름이 아닌 '고유 코드(B027)'로 찾거나, '휘발유'라는 단어를 폭넓게 인식하도록 변경
        if oil.get("PRODCD") == "B027" or oil.get("PRODNM") == "휘발유" or oil.get("PRODNM") == "보통휘발유":
            try:
                raw_price = oil.get("PRICE", "0")
                gasoline_price = float(str(raw_price).replace(',', ''))
            except (ValueError, TypeError, AttributeError):
                pass
            break
            
    # 기준가 설정 (예: 1600원을 지수 100으로 설정)
    base_price = 1600.0
    oil_index = (gasoline_price / base_price) * 100

    # 지수에 따른 추천 로직 (가격이 오를수록 멘트가 다급해짐)
    if oil_index >= 110:
        level = "위험"
        msg = "기름값이 비정상적으로 폭등했습니다! 당장 차 키를 내려놓고 지하철을 타세요 🚇"
        color = "#dc2626" # 빨간색
    elif oil_index >= 103:
        level = "경고"
        msg = "유가가 다소 높습니다. 오늘은 버스나 따릉이 어떠신가요? 🚌"
        color = "#ea580c" # 주황색
    else:
        level = "안정"
        msg = "유가가 안정적입니다. 편안하게 자차로 이동하세요 🚗"
        color = "#16a34a" # 초록색

    return {
        "price": f"{gasoline_price:,.0f}",
        "index": round(oil_index, 1),
        "level": level,
        "msg": msg,
        "color": color
    }