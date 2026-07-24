from trade_signal import calculate_signals
from score_engine import calculate_score                           
def build_ai_context(df):
    latest = df.iloc[-1]
    signals = calculate_signals(df)
    score = calculate_score(df)
    context = f"""
你是一名专业A股量化分析师，请严格依据下面的数据分析。

==============================
【最新行情】
==============================
收盘价：{latest['Close']:.2f}
开盘价：{latest['Open']:.2f}
最高价：{latest['High']:.2f}
最低价：{latest['Low']:.2f}

涨跌幅：{latest['CHANGE_PCT']:.2f}%

成交量：{latest['Volume']:,}
5日均量：{latest['VOL_MA5']:.0f}

==============================
【均线】
==============================
MA5：{latest['MA5']:.2f}
MA10：{latest['MA10']:.2f}
MA20：{latest['MA20']:.2f}
MA60：{latest['MA60']:.2f}

==============================
【MACD】
==============================
MACD：{latest['MACD']:.4f}
Signal：{latest['MACD_SIGNAL']:.4f}
Histogram：{latest['MACD_HIST']:.4f}

==============================
【RSI】
==============================
RSI：{latest['RSI']:.2f}

==============================
【布林带】
==============================
上轨：{latest['BB_HIGH']:.2f}
下轨：{latest['BB_LOW']:.2f}

==============================
【20日区间】
==============================
20日最高：{latest['HIGH20']:.2f}
20日最低：{latest['LOW20']:.2f}

==============================
【关键位置】
==============================
支撑位：{latest['SUPPORT']:.2f}
压力位：{latest['RESISTANCE']:.2f}
==============================
【程序评分】
==============================

综合评分：{score['score']}

趋势得分：{score['detail']['trend']}

动量得分：{score['detail']['momentum']}

成交量得分：{score['detail']['volume']}

突破得分：{score['detail']['breakout']}

风险控制得分：{score['detail']['risk']}

==============================
【程序识别信号】
==============================

均线：
{signals['ma_trend']}

MACD：
{signals['macd']}

RSI：
{signals['rsi']}

成交量：
{signals['volume']}

突破情况：
{signals['breakout']}

请严格依据以上数据和程序识别信号输出JSON。
"""

    return context
