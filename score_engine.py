def calculate_score(df):
    """
    多因子评分引擎 V3（渐进式评分）
    总分100分
    """

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    detail = {
        "trend": 0,
        "momentum": 0,
        "volume": 0,
        "breakout": 0,
        "risk": 0,
    }

    # =====================
    # 趋势（40分）
    # =====================

    # 收盘价相对 MA5
    if latest["Close"] > latest["MA5"]:
        detail["trend"] += 10
    else:
        detail["trend"] += 4

    # MA5 vs MA10
    if latest["MA5"] > latest["MA10"]:
        detail["trend"] += 10
    else:
        detail["trend"] += 4

    # MA10 vs MA20
    if latest["MA10"] > latest["MA20"]:
        detail["trend"] += 10
    else:
        detail["trend"] += 4

    # MA20 趋势
    if latest["MA20"] > prev["MA20"]:
        detail["trend"] += 10
    else:
        detail["trend"] += 4

    # =====================
    # 动量（25分）
    # =====================

    # MACD
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        detail["momentum"] += 10
    else:
        detail["momentum"] += 5

    # MACD柱体
    if latest["MACD_HIST"] > prev["MACD_HIST"]:
        detail["momentum"] += 5
    else:
        detail["momentum"] += 2

    # RSI
    rsi = latest["RSI"]

    if 55 <= rsi <= 70:
        detail["momentum"] += 10
    elif 40 <= rsi < 55:
        detail["momentum"] += 8
    elif 30 <= rsi < 40:
        detail["momentum"] += 6
    elif 20 <= rsi < 30:
        detail["momentum"] += 4
    else:
        detail["momentum"] += 2

    # =====================
    # 成交量（15分）
    # =====================

    ratio = latest["Volume"] / latest["VOL_MA5"]

    if ratio >= 1.3:
        detail["volume"] += 15
    elif ratio >= 1.1:
        detail["volume"] += 12
    elif ratio >= 0.9:
        detail["volume"] += 8
    elif ratio >= 0.7:
        detail["volume"] += 5
    else:
        detail["volume"] += 2

    # =====================
    # 突破（10分）
    # =====================

    distance = (latest["HIGH20"] - latest["Close"]) / latest["HIGH20"]

    if distance <= 0:
        detail["breakout"] += 10
    elif distance <= 0.02:
        detail["breakout"] += 8
    elif distance <= 0.05:
        detail["breakout"] += 6
    elif distance <= 0.10:
        detail["breakout"] += 4
    else:
        detail["breakout"] += 2

    # =====================
    # 风险（10分）
    # =====================

    detail["risk"] = 10

    if latest["RSI"] > 80:
        detail["risk"] -= 2

    if latest["Close"] < latest["MA20"]:
        detail["risk"] -= 3

    if latest["MACD"] < latest["MACD_SIGNAL"]:
        detail["risk"] -= 3

    if latest["Close"] < latest["MA60"]:
        detail["risk"] -= 2

    detail["risk"] = max(detail["risk"], 0)

    # =====================
    # 总分
    # =====================

    score = sum(detail.values())
    score = max(0, min(score, 100))

    return {
        "score": score,
        "detail": detail
    }
