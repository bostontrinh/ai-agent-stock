"""A股历史行情数据获取（AKShare + yfinance 双源）"""
import os, pickle, time
import pandas as pd
import numpy as np

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)
AKSHARE_OK = True

def _akshare_daily(symbol: str) -> pd.DataFrame:
    """AKShare 获取（国内IP专用）"""
    import akshare as ak
    return ak.stock_zh_a_daily(symbol=symbol, adjust="qfq")

def _yf_daily(code: str) -> pd.DataFrame:
    """yfinance 获取（海外IP备用）"""
    import yfinance as yf
    # ETF: 51xxxx -> .SS
    if code.startswith("51"):
        ticker = yf.Ticker(code + ".SS")
    elif code.startswith(("0","3")):
        ticker = yf.Ticker(code + ".SZ")
    else:
        ticker = yf.Ticker(code + ".SS")
    df = ticker.history(period="6mo")
    if df.empty:
        raise ValueError("no data")
    df.index = pd.to_datetime(df.index.date)
    df = df.rename(columns={"Open":"开盘","High":"最高","Low":"最低","Close":"收盘","Volume":"成交量"})
    df["开盘"] = df["开盘"].astype(float); df["收盘"] = df["收盘"].astype(float)
    df["最高"] = df["最高"].astype(float); df["最低"] = df["最低"].astype(float)
    df["成交量"] = df["成交量"].astype(float)
    df["涨跌幅"] = df["收盘"].pct_change() * 100
    df["换手率"] = 0.0
    df = df.rename(columns={"开盘":"Open","收盘":"Close","最高":"High","最低":"Low","成交量":"Volume"})
    return df

def get_history(stock_code, days=120):
    """获取历史数据，AKShare 优先 → yfinance 备用"""
    cache_file = f"{CACHE_DIR}/{stock_code}_hist.pkl"
    # 缓存 30 分钟
    if os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < 1800:
            with open(cache_file, "rb") as f:
                return pickle.load(f).tail(days)
    # 获取
    df = None
    err = ""
    try:
        sym = ("sz" if stock_code.startswith(("0","3")) else "sh") + stock_code
        df = _akshare_daily(sym)
    except Exception as e:
        err = str(e)[:100]
    if df is None or df.empty:
        try:
            df = _yf_daily(stock_code)
        except Exception as e2:
            err += f" | yf: {e2}"
    if df is None or df.empty:
        raise RuntimeError(f"无法获取 {stock_code} 数据: {err}")
    # 缓存
    with open(cache_file, "wb") as f:
        pickle.dump(df, f)
    return df.tail(days)
