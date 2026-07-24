"""A股历史行情数据获取 — akshare/sina/yfinance 多源"""
import os, pickle, time
import pandas as pd
import numpy as np

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _akshare_etf(code: str) -> pd.DataFrame:
    """ETF 数据 — Sina 接口"""
    import akshare as ak
    sym = ("sh" if code.startswith("5") else "sz") + code
    df = ak.fund_etf_hist_sina(symbol=sym)
    if df.empty: raise ValueError("no ETF data")
    df["date"] = pd.to_datetime(df["date"])
    df = df.rename(columns={"open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"})
    df["CHANGE_PCT"] = df["Close"].pct_change() * 100
    return df.set_index("date")

def _akshare_stock(code: str) -> pd.DataFrame:
    """个股 — akshare"""
    import akshare as ak
    sym = ("sz" if code.startswith(("0","3")) else "sh") + code
    return ak.stock_zh_a_daily(symbol=sym, adjust="qfq")

def _yf_fallback(code: str) -> pd.DataFrame:
    """yfinance 海外备用"""
    import yfinance as yf
    if code.startswith("51"): sym = code + ".SS"
    elif code.startswith(("0","3")): sym = code + ".SZ"
    else: sym = code + ".SS"
    df = yf.Ticker(sym).history(period="6mo")
    if df.empty: raise ValueError("no yf data")
    df.index = pd.to_datetime(df.index.date)
    df = df.rename(columns={"Open":"开盘","High":"最高","Low":"最低","Close":"收盘","Volume":"成交量"})
    for c in ["开盘","收盘","最高","最低","成交量"]: df[c] = df[c].astype(float)
    df["CHANGE_PCT"] = df["收盘"].pct_change() * 100
    return df.rename(columns={"开盘":"Open","收盘":"Close","最高":"High","最低":"Low","成交量":"Volume"})

def get_history(stock_code, days=120):
    """获取历史数据，多源自动切换"""
    cache_file = f"{CACHE_DIR}/{stock_code}_v2.pkl"
    if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) < 1800:
        with open(cache_file, "rb") as f: return pickle.load(f).tail(days)

    df = None
    try:
        if stock_code.startswith("51"): df = _akshare_etf(stock_code)
        else: df = _akshare_stock(stock_code)
    except:
        pass

    if df is None or df.empty:
        try: df = _yf_fallback(stock_code)
        except Exception as e: raise RuntimeError(f"无法获取 {stock_code} 数据: {e}")

    with open(cache_file, "wb") as f: pickle.dump(df, f)
    return df.tail(days)
