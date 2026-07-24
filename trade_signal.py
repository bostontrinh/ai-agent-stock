import pandas as pd


def calculate_signals(df):
    """
    根据技术指标计算交易信号
    """

    latest = df.iloc[-1]

    signals = {}

    # ======================
    # MA排列
    # ======================
    if latest["MA5"] > latest["MA10"] > latest["MA20"] > latest["MA60"]:
        signals["ma_trend"] = "多头排列"

    elif latest["MA5"] < latest["MA10"] < latest["MA20"] < latest["MA60"]:
        signals["ma_trend"] = "空头排列"

    else:
        signals["ma_trend"] = "均线交织"

    # ======================
    # MACD
    # ======================
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        signals["macd"] = "金叉"

    else:
        signals["macd"] = "死叉"

    # ======================
    # RSI
    # ======================
    if latest["RSI"] >= 70:
        signals["rsi"] = "超买"

    elif latest["RSI"] <= 30:
        signals["rsi"] = "超卖"

    else:
        signals["rsi"] = "正常"

    # ======================
    # 成交量
    # ======================
    if latest["Volume"] > latest["VOL_MA5"]:
        signals["volume"] = "放量"

    else:
        signals["volume"] = "缩量"

    # ======================
    # 是否突破20日高点
    # ======================
    if latest["Close"] >= latest["HIGH20"]:
        signals["breakout"] = "突破20日新高"

    elif latest["Close"] <= latest["LOW20"]:
        signals["breakout"] = "跌破20日新低"

    else:
        signals["breakout"] = "区间运行"

    return signals