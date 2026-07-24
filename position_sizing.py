"""
仓位管理模块
==========
功能：凯利公式/固定比例/风险平价仓位计算
"""

import math


def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> dict:
    """
    凯利公式计算最优仓位

    参数:
        win_rate: 胜率（0-1）
        avg_win: 平均盈利率（如0.15表示15%）
        avg_loss: 平均亏损率（如0.08表示8%）

    返回:
        {"fraction": 建议仓位比例, "half_kelly": 半凯利(更保守)}
    """
    if avg_loss == 0:
        return {"fraction": 0, "half_kelly": 0, "error": "平均亏损不能为0"}

    b = avg_win / avg_loss  # 盈亏比
    p = win_rate
    q = 1 - p

    f = (b * p - q) / b  # 凯利公式

    # 限制范围
    f = max(0, min(f, 0.5))  # 最大50%

    return {
        "fraction": round(f, 4),
        "half_kelly": round(f * 0.5, 4),
        "quarter_kelly": round(f * 0.25, 4),
        "win_rate": round(win_rate * 100, 1),
        "profit_ratio": round(avg_win * 100, 1),
        "loss_ratio": round(avg_loss * 100, 1),
    }


def fixed_pct_sizing(total_capital: float, risk_per_trade: float = 0.02,
                     stop_loss_pct: float = 0.08) -> dict:
    """
    固定比例仓位计算

    参数:
        total_capital: 总资金
        risk_per_trade: 单笔风险比例（默认2%）
        stop_loss_pct: 止损比例（默认8%）

    返回:
        {"position_size": 买入金额, "position_pct": 仓位比例,
         "max_loss": 最大亏损, "shares": 股数(按股价)}
    """
    max_loss = total_capital * risk_per_trade            # 单笔最大亏损金额
    position_size = max_loss / stop_loss_pct             # 可买入金额
    position_pct = position_size / total_capital         # 仓位比例

    return {
        "position_size": round(position_size, 2),
        "position_pct": round(position_pct * 100, 2),
        "max_loss": round(max_loss, 2),
        "max_loss_pct": risk_per_trade * 100,
    }


def volatility_sizing(total_capital: float, annual_vol: float,
                      target_risk: float = 0.15) -> dict:
    """
    风险平价仓位（波动率越低仓位越高）

    参数:
        total_capital: 总资金
        annual_vol: 年化波动率（如0.35表示35%）
        target_risk: 目标风险水平（默认15%）
    """
    if annual_vol == 0:
        return {"position_pct": 0, "error": "波动率不能为0"}

    # 波动率越低 → 仓位越高
    position_pct = target_risk / annual_vol
    position_pct = min(position_pct, 0.95)  # 最大95%

    return {
        "position_pct": round(position_pct * 100, 2),
        "position_size": round(total_capital * position_pct, 2),
        "annual_vol": round(annual_vol * 100, 2),
        "target_risk": round(target_risk * 100, 1),
    }


def portfolio_position_sizing(total_capital: float, stock_count: int = 5,
                              max_single: float = 0.25) -> list:
    """
    组合仓位分配

    参数:
        total_capital: 总资金
        stock_count: 持仓股票数
        max_single: 单只上限
    """
    if stock_count <= 0:
        return []

    equal_pct = 1 / stock_count  # 等权分配
    if equal_pct > max_single:
        equal_pct = max_single

    result = []
    remaining = total_capital

    for i in range(stock_count):
        if i == stock_count - 1:
            # 最后一只拿剩余
            amount = remaining
        else:
            amount = total_capital * equal_pct

        result.append({
            "stock_no": i + 1,
            "amount": round(amount, 2),
            "pct": round(amount / total_capital * 100, 2),
        })
        remaining -= amount

    return result


def calculate_max_positions(total_capital: float, avg_stop_pct: float,
                            max_total_risk: float = 0.06) -> dict:
    """
    根据总风险预算计算最大持仓数量

    参数:
        total_capital: 总资金
        avg_stop_pct: 平均止损比例
        max_total_risk: 总风险预算（默认6%）
    """
    if avg_stop_pct <= 0:
        return {"max_positions": 0}

    # 单笔风险 = 平均止损 × 单只仓位
    # 假设单只仓位20%
    single_risk = avg_stop_pct * 0.20
    max_pos = max_total_risk / single_risk

    return {
        "max_positions": math.floor(max_pos),
        "single_risk_pct": round(single_risk * 100, 2),
        "total_risk_budget": max_total_risk * 100,
        "suggestion": f"建议同时持有不超过{math.floor(max_pos)}只股票"
    }
