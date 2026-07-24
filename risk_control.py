"""
风险控制模块
==========
功能：止损/止盈/最大回撤预警/波动率评估
"""

import pandas as pd
import numpy as np


def calc_stop_loss(entry_price: float, method: str = "atr", df: pd.DataFrame = None) -> dict:
    """
    计算止损价（多种策略）

    参数:
        entry_price: 买入价
        method: atr | fixed_pct | support | ma | chandelier
        df: 历史数据（ATR/支撑位需要）

    返回:
        {"price": 止损价, "pct": 止损百分比, "method": 策略名}
    """
    if method == "fixed_pct":
        # 固定比例止损（默认 -8%）
        pct = 0.08
        return {
            "price": round(entry_price * (1 - pct), 2),
            "pct": -pct * 100,
            "method": "固定比例止损"
        }

    if method == "hard":
        # 硬止损 -10%（适合波动大的个股）
        pct = 0.10
        return {
            "price": round(entry_price * (1 - pct), 2),
            "pct": -pct * 100,
            "method": "硬止损"
        }

    if df is None:
        return calc_stop_loss(entry_price, "fixed_pct")

    if method == "atr":
        # ATR 追踪止损（适应波动率）
        atr = df["ATR"].iloc[-1] if "ATR" in df.columns else df["Close"].std() * 0.05
        multiplier = 2.0  # 2倍ATR
        stop = entry_price - atr * multiplier
        pct = (stop - entry_price) / entry_price
        return {
            "price": round(stop, 2),
            "pct": round(pct * 100, 2),
            "method": f"ATR({multiplier}倍)追踪止损",
            "atr": round(atr, 2)
        }

    if method == "ma":
        # 均线止损（跌破MA20/MA60）
        for ma_col in ["MA20", "MA60", "MA30"]:
            if ma_col in df.columns:
                ma_val = df[ma_col].iloc[-1]
                stop = ma_val
                pct = (stop - entry_price) / entry_price
                return {
                    "price": round(stop, 2),
                    "pct": round(pct * 100, 2),
                    "method": f"{ma_col}均线止损"
                }
        return calc_stop_loss(entry_price, "fixed_pct", df)

    if method == "support":
        # 近期支撑位止损（最低价附近）
        recent_low = df["Low"].tail(20).min()
        stop = recent_low * 0.98  # 支撑位下方2%
        pct = (stop - entry_price) / entry_price
        return {
            "price": round(stop, 2),
            "pct": round(pct * 100, 2),
            "method": "支撑位止损",
            "support": round(recent_low, 2)
        }

    # 默认
    return calc_stop_loss(entry_price, "fixed_pct", df)


def calc_take_profit(entry_price: float, method: str = "risk_reward", risk_pct: float = 8.0) -> dict:
    """
    计算止盈价

    参数:
        entry_price: 买入价
        method: risk_reward | fixed_pct | resistance
        risk_pct: 止损百分比（用于计算盈亏比）

    返回:
        {"price": 止盈价, "pct": 止盈百分比, "method": 策略名}
    """
    if method == "risk_reward":
        # 盈亏比 2:1 / 3:1
        ratios = [2, 3]
        results = []
        for r in ratios:
            profit_pct = risk_pct * r
            results.append({
                "price": round(entry_price * (1 + profit_pct / 100), 2),
                "pct": round(profit_pct, 2),
                "method": f"盈亏比{r}:1",
                "ratio": r
            })
        return results

    if method == "fixed_pct":
        # 固定比例止盈
        pct = 15
        return [{
            "price": round(entry_price * (1 + pct / 100), 2),
            "pct": pct,
            "method": f"固定{pct}%止盈"
        }]

    # 默认
    return calc_take_profit(entry_price, "risk_reward", risk_pct)


def calc_max_drawdown(price_series: pd.Series) -> dict:
    """
    计算最大回撤
    """
    peak = price_series.expanding().max()
    drawdown = (price_series - peak) / peak
    max_dd = drawdown.min()
    max_dd_idx = drawdown.idxmin()

    return {
        "max_drawdown": round(max_dd * 100, 2),
        "max_drawdown_date": str(max_dd_idx) if hasattr(max_dd_idx, "strftime") else str(max_dd_idx),
        "current_drawdown": round(drawdown.iloc[-1] * 100, 2)
    }


def calc_volatility(df: pd.DataFrame) -> dict:
    """
    波动率评估
    """
    returns = df["Close"].pct_change().dropna()

    daily_vol = returns.std()
    annual_vol = daily_vol * np.sqrt(252)

    # 波动率分级
    if annual_vol < 0.20:
        level = "低"
    elif annual_vol < 0.35:
        level = "中"
    elif annual_vol < 0.50:
        level = "高"
    else:
        level = "极高"

    return {
        "daily_vol": round(daily_vol * 100, 2),
        "annual_vol": round(annual_vol * 100, 2),
        "level": level,
        "avg_daily_range": round((df["High"] - df["Low"]).mean(), 2)
    }


def calc_risk_score(df: pd.DataFrame) -> dict:
    """
    综合风险评估（0-100分，越高越危险）

    因子：
    - 波动率（30%）
    - 最大回撤（25%）
    - 趋势强度（25%）
    - 成交量异常（20%）
    """
    latest = df.iloc[-1]
    vol = calc_volatility(df)
    dd = calc_max_drawdown(df["Close"])

    score = 0

    # 波动率评分
    if vol["level"] == "极高":
        score += 30
    elif vol["level"] == "高":
        score += 22
    elif vol["level"] == "中":
        score += 12
    else:
        score += 5

    # 回撤评分
    if dd["max_drawdown"] < -30:
        score += 25
    elif dd["max_drawdown"] < -20:
        score += 18
    elif dd["max_drawdown"] < -10:
        score += 10
    else:
        score += 4

    # 趋势评分（均线空头排列加分）
    if "MA5" in df.columns and "MA20" in df.columns:
        if latest["MA5"] < latest["MA20"]:
            score += 15
        if "MA60" in df.columns and latest["MA20"] < latest["MA60"]:
            score += 10

    # 成交量异常
    if "VOL_MA5" in df.columns:
        if latest["Volume"] > latest["VOL_MA5"] * 2 and latest["Close"] < latest["Open"]:
            score += 20  # 放量下跌

    # 分级
    if score >= 70:
        level = "极高风险 ⛔"
    elif score >= 50:
        level = "高风险 ⚠️"
    elif score >= 30:
        level = "中等风险 ⚡"
    else:
        level = "低风险 ✅"

    return {
        "score": score,
        "level": level,
        "details": {
            "波动率": vol["level"],
            "最大回撤": f"{dd['max_drawdown']}%",
            "当前回撤": f"{dd['current_drawdown']}%",
            "年化波动": f"{vol['annual_vol']}%"
        }
    }


def generate_warning(entry_price: float, current_price: float, df: pd.DataFrame) -> list:
    """
    生成风险预警列表
    """
    warnings = []
    loss_pct = (current_price - entry_price) / entry_price * 100

    # 亏损预警
    if loss_pct <= -5:
        warnings.append({
            "level": "注意",
            "msg": f"当前亏损 {loss_pct:.1f}%，接近止损线",
            "action": "关注"
        })
    if loss_pct <= -8:
        warnings.append({
            "level": "警告",
            "msg": f"亏损已达 {loss_pct:.1f}%，建议执行止损",
            "action": "考虑止损"
        })
    if loss_pct <= -15:
        warnings.append({
            "level": "严重",
            "msg": f"亏损 {loss_pct:.1f}%，已超过硬止损线",
            "action": "必须止损"
        })

    # 波动率预警
    vol = calc_volatility(df)
    if vol["level"] in ("高", "极高"):
        warnings.append({
            "level": "注意",
            "msg": f"波动率{vol['level']}（年化{vol['annual_vol']}%），不适合重仓",
            "action": "降低仓位"
        })

    return warnings
