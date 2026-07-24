import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


def calculate_indicators(df):
    df = df.copy()

    # 兼容 yfinance 多层列名
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # =========================
    # 兼容 yfinance / AKShare 字段
    # =========================
    if "Close" in df.columns:
        close = df["Close"]

    elif "close" in df.columns:
        close = df["close"]

        df["Close"] = df["close"]
        df["Open"] = df["open"]
        df["High"] = df["high"]
        df["Low"] = df["low"]
        df["Volume"] = df["volume"]

    else:
        raise ValueError("找不到价格字段")


    # =========================
    # 均线
    # =========================
    df["MA5"] = SMAIndicator(
        close,
        window=5
    ).sma_indicator()

    df["MA10"] = SMAIndicator(
        close,
        window=10
    ).sma_indicator()

    df["MA20"] = SMAIndicator(
        close,
        window=20
    ).sma_indicator()

    df["MA60"] = SMAIndicator(
        close,
        window=60
    ).sma_indicator()


    # =========================
    # MACD
    # =========================
    macd = MACD(close)

    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()
    df["MACD_HIST"] = macd.macd_diff()


    # =========================
    # RSI
    # =========================
    df["RSI"] = RSIIndicator(
        close
    ).rsi()


    # =========================
    # 布林带
    # =========================
    bb = BollingerBands(
        close
    )

    df["BB_HIGH"] = bb.bollinger_hband()
    df["BB_LOW"] = bb.bollinger_lband()


    # =========================
    # 涨跌幅
    # =========================
    df["CHANGE_PCT"] = (
        df["Close"].pct_change() * 100
    )


    # =========================
    # 成交量均线
    # =========================
    df["VOL_MA5"] = (
        df["Volume"]
        .rolling(5)
        .mean()
    )


    # =========================
    # 20日高低点
    # =========================
    df["HIGH20"] = (
        df["High"]
        .rolling(20)
        .max()
    )

    df["LOW20"] = (
        df["Low"]
        .rolling(20)
        .min()
    )


    # =========================
    # 支撑压力
    # =========================
    df["SUPPORT"] = (
        df["Low"]
        .rolling(20)
        .min()
    )

    df["RESISTANCE"] = (
        df["High"]
        .rolling(20)
        .max()
    )


    return df