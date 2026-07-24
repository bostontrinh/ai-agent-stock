#!/usr/bin/env python
"""
AI 股票分析系统 v2 — 全A股扫描 + 个股深度分析 + 持仓监控
部署：streamlit run app.py
"""

import json, os, sys, time
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ── 项目模块 ──────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from market import get_history
from indicator import calculate_indicators
from score_engine import calculate_score
from capital import calculate_capital_score
from risk_control import calc_stop_loss, calc_volatility, calc_risk_score, calc_max_drawdown
from stock_pool import STOCK_POOL

st.set_page_config(page_title="AI股票分析系统", page_icon="📈", layout="wide")

# ── 缓存装饰器 ──────────────────────────
@st.cache_data(ttl=600)
def scan_full_market():
    """全A股扫描（缓存10分钟）"""
    try:
        import akshare as ak
        spot = ak.stock_zh_a_spot_em()
        # 过滤
        spot = spot[(spot["最新价"] > 2) & (~spot["名称"].str.contains("ST|退市", na=False))].copy()
        # 快速预估评分
        spot["涨跌幅"] = spot["涨跌幅"].fillna(0)
        spot["换手率"] = spot["换手率"].fillna(0)
        spot["成交量"] = spot["成交量"].fillna(0).astype(float)
        spot["est"] = (
            spot["涨跌幅"].clip(-5, 10) * 0.3
            + spot["换手率"] / spot["换手率"].max() * 0.3
            + np.log1p(spot["成交量"]) / np.log1p(spot["成交量"].max()) * 0.4
        )
        top = spot.nlargest(30, "est")
        return top[["代码","名称","最新价","涨跌幅","换手率","成交量"]].to_dict("records")
    except:
        return []

@st.cache_data(ttl=600)
def full_analysis(code):
    """个股完整分析（缓存10分钟）"""
    try:
        df = get_history(code)
        df = calculate_indicators(df)
        score = calculate_score(df)
        cap = calculate_capital_score(df)
        risk = calc_risk_score(df)
        vol = calc_volatility(df)
        dd = calc_max_drawdown(df["Close"])
        latest = df.iloc[-1]
        l2 = df.iloc[-2]
        price = float(latest["Close"])
        stop = calc_stop_loss(price, "atr", df)

        # 信号
        trend = "多头" if float(latest["MA5"]) > float(latest["MA20"]) else "空头"
        macd_t = "金叉" if float(latest["MACD"]) > float(latest["MACD_SIGNAL"]) else "死叉"
        total = score["score"] * 0.7 + cap * 0.3

        if risk["score"] >= 50 or trend == "空头":
            signal = "🔴 卖出"
        elif total >= 65 and risk["score"] < 40:
            signal = "🟢 买入"
        elif total >= 55:
            signal = "🟡 持有"
        else:
            signal = "⚪ 观望"

        return {
            "df": df, "latest": latest, "prev": l2, "price": price,
            "score": total, "risk": risk, "vol": vol, "dd": dd,
            "stop": stop, "trend": trend, "macd_t": macd_t,
            "signal": signal, "code": code, "name": STOCK_POOL.get(code, ""),
            "ok": True, "reason": f"评分{total:.0f} 趋势{trend} {macd_t} 风险{risk['level']}",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def plot_kline(df):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
                                  low=df["Low"], close=df["Close"], name="K线"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA5"], name="MA5", line=dict(width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20", line=dict(width=1)))
    if "MA60" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA60"], name="MA60", line=dict(width=1, dash="dot")))
    fig.update_layout(height=500, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
    return fig


def plot_macd(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="DIF"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_SIGNAL"], name="DEA"))
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_HIST"], name="柱", marker_color=np.where(df["MACD_HIST"]>=0, "red", "green")))
    fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
    return fig


# ══════════════════════════════════════════
# UI
# ══════════════════════════════════════════

st.title("📈 AI 股票分析系统")
st.markdown("全A股扫描 · 技术面分析 · AI 评分 · 风控建议")

tab1, tab2, tab3 = st.tabs(["🔍 全市场扫描", "📊 个股深度分析", "📋 我的持仓"])

# ──────────── TAB 1: 全市场扫描 ────────────
with tab1:
    st.header("全A股扫描（TOP 30）")
    st.caption("基于实时行情数据 + 技术面预评分，每10分钟自动刷新")

    if st.button("🔄 立即扫描全市场", use_container_width=True):
        with st.spinner("正在扫描5000+只A股，请稍候..."):
            data = scan_full_market()
            if data:
                st.success(f"✅ 扫描完成，共处理 {len(data)} 只候选股票")
                # 批量做精评（只做前15只，避免太慢）
                results = []
                progress = st.progress(0)
                for i, item in enumerate(data[:15]):
                    result = full_analysis(item["代码"])
                    progress.progress((i + 1) / 15)
                    if result["ok"]:
                        results.append({
                            "代码": result["code"], "名称": result["name"],
                            "现价": result["price"],
                            "涨跌幅": f"{float(data[i]['涨跌幅']):+.2f}%",
                            "评分": f"{result['score']:.0f}",
                            "趋势": result["trend"],
                            "信号": result["signal"],
                            "风险": result["risk"]["level"],
                            "理由": result["reason"],
                        })
                progress.empty()

                if results:
                    df_show = pd.DataFrame(results)
                    st.dataframe(df_show, use_container_width=True, hide_index=True,
                                 column_config={
                                     "信号": st.column_config.TextColumn("信号", width="small"),
                                     "评分": st.column_config.TextColumn("评分", width="small"),
                                     "现价": st.column_config.NumberColumn("现价", format="%.2f"),
                                 })
                    st.markdown("**🟢 买入信号** 的股票可重点关注")
            else:
                st.error("扫描失败，请稍后重试")

    # 显示缓存数据
    cached = scan_full_market()
    if cached:
        st.info(f"📌 上次扫描时间：{datetime.now().strftime('%H:%M')}，共 {len(cached)} 只候选股，点击上方按钮刷新")

# ──────────── TAB 2: 个股深度分析 ────────────
with tab2:
    col1, col2 = st.columns([3, 1])
    with col1:
        code = st.text_input("输入股票代码", value="000001", max_chars=6).strip()
    with col2:
        name_hint = STOCK_POOL.get(code, "")
        if name_hint:
            st.markdown(f"**{name_hint}**")
        else:
            st.markdown("&nbsp;")

    if st.button("🔍 深度分析", type="primary", use_container_width=True):
        with st.spinner(f"正在分析 {code} ..."):
            result = full_analysis(code)

        if not result["ok"]:
            st.error(f"分析失败：{result.get('error', '未知错误')}")
        else:
            r = result
            # 指标卡片
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("现价", f"{r['price']:.2f}", f"{float(r['latest']['CHANGE_PCT']):+.2f}%")
            c2.metric("评分", f"{r['score']:.0f}/100")
            c3.metric("信号", r["signal"])
            c4.metric("趋势", r["trend"])
            c5.metric("风险", r["risk"]["level"])

            # 止损止盈
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("止损价", f"{r['stop']['price']:.2f} ({r['stop']['pct']:.1f}%)")
            cc2.metric("最大回撤", f"{r['dd']['max_drawdown']:.1f}%")
            cc3.metric("年化波动", f"{r['vol']['annual_vol']:.1f}%")

            # 技术面详情
            l = r["latest"]
            st.markdown(f"""
**均线**: MA5={l['MA5']:.2f} MA10={l['MA10']:.2f} MA20={l['MA20']:.2f}  
**MACD**: {r['macd_t']}  DIF={l['MACD']:.4f}  DEA={l['MACD_SIGNAL']:.4f}  
**RSI**: {l['RSI']:.1f}  （超买>70 超卖<30）  
**布林带**: 上轨={l['BB_HIGH']:.2f} 下轨={l['BB_LOW']:.2f}  
**区间**: 20日高={l['HIGH20']:.2f} 20日低={l['LOW20']:.2f}
""")

            # K线
            st.subheader("📈 K线走势")
            st.plotly_chart(plot_kline(r["df"]), use_container_width=True)

            # MACD + RSI 双栏
            mc1, mc2 = st.columns(2)
            with mc1:
                st.subheader("📉 MACD")
                st.plotly_chart(plot_macd(r["df"]), use_container_width=True)
            with mc2:
                st.subheader("📊 RSI (14)")
                rsi_fig = go.Figure()
                rsi_fig.add_trace(go.Scatter(x=r["df"].index, y=r["df"]["RSI"], name="RSI"))
                rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
                rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
                rsi_fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(rsi_fig, use_container_width=True)

            # 操作建议
            st.divider()
            st.subheader("💡 操作建议")
            if "买入" in r["signal"]:
                st.success(f"**🟢 买入信号**\n\n{r['reason']}")
            elif "卖出" in r["signal"]:
                st.error(f"**🔴 卖出信号**\n\n建议止损，跌破 {r['stop']['price']:.2f} 必须走")
            elif "持有" in r["signal"]:
                st.warning(f"**🟡 持有观望**\n\n继续持有，设好止损 {r['stop']['price']:.2f}")
            else:
                st.info(f"**⚪ 观望**\n\n不操作不补仓")

# ──────────── TAB 3: 我的持仓 ────────────
with tab3:
    st.header("我的持仓监控")
    PORTFOLIO = {"600176": "中国巨石", "000021": "深科技", "002185": "华天科技", "516650": "有色金属ETF"}

    if st.button("🔄 刷新持仓状态", use_container_width=True):
        with st.spinner("正在分析持仓..."):
            for code, name in PORTFOLIO.items():
                is_etf = code.startswith(("51", "16"))
                result = full_analysis(code)
                if result["ok"]:
                    r = result
                    bg = "#1a3a1a" if "买入" in r["signal"] else "#3a1a1a" if "卖出" in r["signal"] else "#1a1a3a"
                    st.markdown(f"""
<div style="background:{bg}; padding:16px; border-radius:12px; margin-bottom:12px">
<h4 style="margin:0">{code} {name} <span style="float:right">{r['signal']}</span></h4>
<p style="margin:4px 0">现价 <b>{r['price']:.2f}</b> &nbsp;|&nbsp; 评分 <b>{r['score']:.0f}</b> &nbsp;|&nbsp; 趋势 {r['trend']} &nbsp;|&nbsp; 风险 {r['risk']['level']}</p>
<p style="margin:4px 0">止损 <b style="color:#ff6b6b">{r['stop']['price']:.2f}</b> &nbsp;|&nbsp; MA5={r['latest']['MA5']:.2f} MA20={r['latest']['MA20']:.2f}</p>
</div>
""", unsafe_allow_html=True)
                else:
                    st.error(f"{code} {name}：数据获取失败")

    st.caption("数据每10分钟自动刷新，点击上方按钮手动刷新")

# ── 页脚 ──
st.divider()
st.caption("⚠️ 本系统仅供研究参考，不构成投资建议 | AI分析基于技术指标，请结合实际情况决策")
