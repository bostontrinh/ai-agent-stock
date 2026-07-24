import os
import pickle
import time
import akshare as ak


CACHE_DIR = "data/cache"


if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


def get_history(stock_code, days=120):
    """
    AKShare获取A股历史数据（带缓存）
    """

    cache_file = f"{CACHE_DIR}/{stock_code}_ak.pkl"

    # 缓存30分钟
    if os.path.exists(cache_file):

        cache_time = os.path.getmtime(cache_file)

        if time.time() - cache_time < 1800:

            with open(cache_file, "rb") as f:
                df = pickle.load(f)

            return df.tail(days)


    # 获取数据
    if stock_code.startswith(("0", "3")):
        symbol = "sz" + stock_code
    elif stock_code.startswith("6"):
        symbol = "sh" + stock_code
    else:
        symbol = stock_code


    df = ak.stock_zh_a_daily(
        symbol=symbol,
        adjust="qfq"
    )


    if df is None or df.empty:
        return None


    # 保存缓存
    with open(cache_file, "wb") as f:
        pickle.dump(df, f)


    return df.tail(days)
