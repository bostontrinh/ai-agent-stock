#!/usr/bin/env python
"""
AI 股票分析系统 v3 — 全A股扫描 + AI深度分析 + 报告
"""

import json, os, sys, time, glob
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="AI股票分析系统", page_icon="📈", layout="wide")

# ── 延迟导入（避免 Streamlit Cloud 启动报错） ──
def lazy_import():
    global get_history, calculate_indicators, calculate_score, capital_score
    global calc_stop_loss, calc_volatility, calc_risk_score, calc_max_drawdown, STOCK_POOL
    global analyze_stock
    from market import get_history as gh
    from indicator import calculate_indicators as ci
    from score_engine import calculate_score as cs
    from capital import calculate_capital_score as cc
    from risk_control import calc_stop_loss as sl, calc_volatility as cv, calc_risk_score as cr, calc_max_drawdown as md
    from stock_pool import STOCK_POOL as sp
    get_history, calculate_indicators, calculate_score, capital_score = gh, ci, cs, cc
    calc_stop_loss, calc_volatility, calc_risk_score, calc_max_drawdown = sl, cv, cr, md
    STOCK_POOL = sp
    try:
        from analyze_stock import analyze_stock as ast
        analyze_stock = ast
    except:
        analyze_stock = None
    return True

if not lazy_import():
    st.stop()

# ── 缓存 ──
@st.cache_data(ttl=300)
def scan_market():
    """全A股快速扫描"""
    try:
        import akshare as ak
        spot = ak.stock_zh_a_spot()
        spot = spot[(spot["最新价"] > 2) & (~spot["名称"].str.contains("ST|退市|N", na=False))].copy()
        spot["涨跌幅"] = spot["涨跌幅"].astype(float)
        spot["成交量"] = spot["成交量"].fillna(0).astype(float)
        # 按涨跌幅排序取TOP
        spot = spot.sort_values("涨跌幅", ascending=False)
        top = spot.head(50)
        return [{k:row[k] for k in ["代码","名称","最新价","涨跌幅"]} for _, row in top.iterrows()]
    except:
        # yfinance fallback
        st.info("使用 yfinance 备用源扫描...")
        import time as _t, yfinance as yf
        codes = _top300_codes()
        results = []
        for i, (code, name) in enumerate(codes):
            try:
                sym = f"{code}.{'SZ' if code.startswith(('0','3')) else 'SS'}"
                h = yf.Ticker(sym).history(period="5d")
                if not h.empty:
                    p, prev = float(h["Close"].iloc[-1]), float(h["Close"].iloc[-2])
                    results.append({"代码":code,"名称":name,"最新价":round(p,2),"涨跌幅":round((p-prev)/prev*100,2)})
                if i%5==0: _t.sleep(0.5)
            except: pass
        results.sort(key=lambda x: x["涨跌幅"], reverse=True)
        return results[:50] if results else None

# 沪深300核心成分股（yfinance 备用）
def _top300_codes():
    return [
        ("600519","贵州茅台"),("300750","宁德时代"),("000858","五粮液"),("600036","招商银行"),
        ("601318","中国平安"),("000333","美的集团"),("002594","比亚迪"),("600900","长江电力"),
        ("000001","平安银行"),("601166","兴业银行"),("600030","中信证券"),("600276","恒瑞医药"),
        ("601398","工商银行"),("601328","交通银行"),("601288","农业银行"),("600887","伊利股份"),
        ("002475","立讯精密"),("600809","山西汾酒"),("603259","药明康德"),("600031","三一重工"),
        ("300059","东方财富"),("002415","海康威视"),("000568","泸州老窖"),("688981","中芯国际"),
        ("601899","紫金矿业"),("600309","万华化学"),("000002","万科A"),("600585","海螺水泥"),
        ("002142","宁波银行"),("002352","顺丰控股"),("300760","迈瑞医疗"),("601888","中国中免"),
        ("600585","海螺水泥"),("002714","牧原股份"),("000725","京东方A"),("601688","华泰证券"),
    ]

@st.cache_data(ttl=300)
def tech_analysis(code):
    """技术面分析"""
    try:
        df = get_history(code); df = calculate_indicators(df)
        sc = calculate_score(df); cap = capital_score(df)
        risk = calc_risk_score(df); vol = calc_volatility(df)
        dd = calc_max_drawdown(df["Close"])
        l = df.iloc[-1]; price = float(l["Close"])
        stop = calc_stop_loss(price, "atr", df)
        total = sc["score"] * 0.7 + cap * 0.3
        trend = "多头" if l["MA5"] > l["MA20"] else "空头"
        macd_t = "金叉" if l["MACD"] > l["MACD_SIGNAL"] else "死叉"
        if risk["score"] >= 50 or trend == "空头": signal = "🔴 卖出"
        elif total >= 65 and risk["score"] < 40: signal = "🟢 买入"
        elif total >= 55: signal = "🟡 持有"
        else: signal = "⚪ 观望"
        return {"df": df, "price": price, "score": total, "risk": risk, "vol": vol,
                "dd": dd, "stop": stop, "trend": trend, "macd_t": macd_t, "signal": signal,
                "l": l, "ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

@st.cache_data(ttl=600)
def ai_analysis(code, name=""):
    """DeepSeek AI 分析"""
    if not analyze_stock:
        return {"ok": False, "error": "AI 模块未加载"}
    try:
        result = analyze_stock(stock_code=code)
        return {"ok": True, "score": result.get("score", 0), "signal": result.get("signal", ""),
                "reason": result.get("reason", ""), "stars": result.get("stars", ""),
                "risk": result.get("risk", ""), "support": result.get("support", 0),
                "resistance": result.get("resistance", 0)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}

# ── 图表 ──
def plot_kline(df):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="K线"))
    for ma, c in [("MA5","#f0b90b"), ("MA20","#0b9bf0")]:
        if ma in df.columns: fig.add_trace(go.Scatter(x=df.index, y=df[ma], name=ma, line=dict(color=c, width=1)))
    fig.update_layout(height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    return fig

def plot_macd(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="DIF"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_SIGNAL"], name="DEA"))
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_HIST"], name="柱",
                         marker_color=np.where(df["MACD_HIST"]>=0, "#ff4d4f", "#52c41a")))
    fig.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    return fig

# ══════════ UI ══════════
st.title("📈 AI 股票分析系统")
st.caption("全A股扫描 · 技术面分析 · DeepSeek AI 决策 · 每日报告")

tabs = st.tabs(["🔍 全市场扫描", "📊 个股分析", "📋 持仓", "📄 每日报告"])

# ═══ TAB 1: 全市场扫描 ═══
with tabs[0]:
    c = st.container()
    with c:
        if st.button("🔄 扫描全市场 5000+ A股", type="primary", use_container_width=True):
            with st.spinner("正在获取全A股实时数据..."):
                data = scan_market()
                if data is not None:
                    st.session_state["market_data"] = data
                    st.session_state["market_time"] = datetime.now().strftime("%H:%M")
                    st.rerun()

    if "market_data" in st.session_state:
        data = st.session_state["market_data"]
        st.info(f"📡 数据时间：{st.session_state.get('market_time','')} | 预筛 {len(data)} 只候选股，点击表格行可深度分析")

        # 快速精评 TOP 20
        results = []
        bar = st.progress(0, text="精评中...")
        for i, item in enumerate(data[:20]):
            r = tech_analysis(item["代码"])
            bar.progress((i+1)/20, text=f"{item['名称']}")
            if r["ok"]:
                results.append({"代码": item["代码"], "名称": item["名称"],
                    "现价": round(r["price"],2), "涨跌幅": f"{item['涨跌幅']:+.2f}%",
                    "评分": int(r["score"]), "趋势": r["trend"], "信号": r["signal"],
                    "风险": r["risk"]["level"].replace("⚠️","").replace("✅","").replace("⛔","").strip()})
        bar.empty()

        if results:
            df = pd.DataFrame(results)
            df = df.sort_values("评分", ascending=False)
            # 颜色标记
            def color_signal(v):
                if "买入" in v: return "background:#1a3a1a"
                if "卖出" in v: return "background:#3a1a1a"
                return ""
            st.dataframe(df, use_container_width=True, hide_index=True,
                column_config={"信号": st.column_config.TextColumn("信号", width="small")},
                height=min(40*len(df)+40, 600))
            st.markdown("🟢=买入 🟡=持有 ⚪=观望 🔴=卖出  |  点击个股分析标签页输入代码查看详情")
        else:
            st.warning("精评无结果，请稍后重试")

# ═══ TAB 2: 个股分析 ═══
with tabs[1]:
    q = st.text_input("股票代码（如 000001 平安银行）", value="000001", max_chars=6, key="stock_code").strip()
    col_a, col_b = st.columns([1,4])
    with col_a:
        go_btn = st.button("🔍 深度分析", type="primary", use_container_width=True)
    with col_b:
        if q and STOCK_POOL.get(q):
            st.markdown(f"**{STOCK_POOL[q]}**")

    if go_btn or "last_code" in st.session_state:
        if go_btn:
            st.session_state["last_code"] = q
        code = st.session_state["last_code"]
        with st.spinner(f"分析 {code} ..."):
            tr = tech_analysis(code)
            ai = ai_analysis(code) if tr["ok"] else {"ok": False}

        if not tr["ok"]:
            st.error(f"分析失败：{tr.get('error','')}")
            st.stop()

        r = tr
        # 头部指标
        def card(col, label, value, delta=None):
            col.markdown(f"""<div style="background:#1a1a2e;padding:12px 16px;border-radius:12px;text-align:center">
<div style="font-size:13px;color:#888">{label}</div>
<div style="font-size:24px;font-weight:700;margin:4px 0">{value}</div>
{delta if delta else ""}</div>""", unsafe_allow_html=True)

        cols = st.columns(5)
        color = "red" if r["l"]["CHANGE_PCT"] < 0 else "green"
        card(cols[0], "现价", f"{r['price']:.2f}", f"<span style='color:{color}'>{r['l']['CHANGE_PCT']:+.2f}%</span>")
        card(cols[1], "评分", f"{r['score']:.0f}")
        card(cols[2], "信号", r["signal"])
        card(cols[3], "趋势", r["trend"])
        card(cols[4], "风险", r["risk"]["level"].replace("⛔","极高").replace("⚠️","高").replace("⚡","中").replace("✅","低"))

        # 止损+波动
        c1, c2, c3 = st.columns(3)
        c1.metric("止损", f"{r['stop']['price']:.2f} ({r['stop']['pct']:.1f}%)")
        c2.metric("年化波动", f"{r['vol']['annual_vol']:.1f}%")
        c3.metric("最大回撤", f"{r['dd']['max_drawdown']:.1f}%")

        # 技术面参数
        l = r["l"]
        with st.expander("📐 技术参数详情", expanded=False):
            st.markdown(f"""
| 指标 | 值 | 信号 |
|------|-----|------|
| MA5/MA20 | {l['MA5']:.2f} / {l['MA20']:.2f} | {'多头 ✅' if l['MA5']>l['MA20'] else '空头 ❌'} |
| MACD | DIF={l['MACD']:.4f} DEA={l['MACD_SIGNAL']:.4f} | {r['macd_t']} |
| RSI(14) | {l['RSI']:.1f} | {'超买⚠️' if l['RSI']>70 else '超卖⚠️' if l['RSI']<30 else '正常✅'} |
| 布林带 | {l['BB_LOW']:.2f} ~ {l['BB_HIGH']:.2f} | 带宽={l['BB_HIGH']-l['BB_LOW']:.2f} |
| 20日区间 | {l['LOW20']:.2f} ~ {l['HIGH20']:.2f} | 振幅={(l['HIGH20']-l['LOW20'])/l['LOW20']*100:.1f}% |
""")

        # AI 分析
        if ai["ok"]:
            with st.expander("🤖 DeepSeek AI 分析", expanded=True):
                st.markdown(f"""
| 项目 | 值 |
|------|-----|
| AI评分 | {ai.get('score','?')}分 |
| 建议 | {ai.get('signal','?')} |
| 支撑位 | {ai.get('support','?')} |
| 压力位 | {ai.get('resistance','?')} |
| 理由 | {ai.get('reason','?')} |
""")

        # 图表
        st.plotly_chart(plot_kline(r["df"]), use_container_width=True)
        mc1, mc2 = st.columns(2)
        with mc1: st.plotly_chart(plot_macd(r["df"]), use_container_width=True)
        with mc2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=r["df"].index, y=r["df"]["RSI"], name="RSI", line=dict(color="#f0b90b")))
            fig.add_hline(y=70, line_dash="dash", line_color="#ff4d4f", opacity=0.5)
            fig.add_hline(y=30, line_dash="dash", line_color="#52c41a", opacity=0.5)
            fig.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # 操作建议
        st.divider()
        if "买入" in r["signal"]:
            st.success(f"**🟢 买入建议** — 评分{r['score']:.0f}，趋势{r['trend']}，可在 {r['stop']['price']:.2f} 设止损")
        elif "卖出" in r["signal"]:
            st.error(f"**🔴 卖出建议** — 跌破 {r['stop']['price']:.2f} 必须止损，不补仓")
        elif "持有" in r["signal"]:
            st.warning(f"**🟡 持有观望** — 止损设 {r['stop']['price']:.2f}")
        else:
            st.info(f"**⚪ 观望** — 不操作")

# ═══ TAB 3: 持仓 ═══
with tabs[2]:
    st.header("我的持仓")

    # 初始化持仓
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = {"600176":"中国巨石", "000021":"深科技", "002185":"华天科技", "516650":"有色金属ETF"}

    # 添加/删除
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        new_code = st.text_input("添加股票代码", key="add_code", max_chars=6, placeholder="600519").strip()
    with c2:
        if st.button("➕ 添加", use_container_width=True) and new_code and len(new_code) == 6:
            st.session_state["portfolio"][new_code] = STOCK_POOL.get(new_code, new_code)
            st.rerun()
    with c3:
        remove_code = st.selectbox("删除", [""] + list(st.session_state["portfolio"].keys()), key="remove_code")
        if remove_code and st.button("🗑 删除", use_container_width=True):
            st.session_state["portfolio"].pop(remove_code, None)
            st.rerun()

    st.caption(f"当前 {len(st.session_state['portfolio'])} 只持仓")

    with st.spinner("更新中..."):
        for code, name in st.session_state["portfolio"].items():
            r = tech_analysis(code)
            if not r["ok"]: 
                st.warning(f"{code} {name}：数据获取失败")
                continue
            sig = r["signal"]
            sig_key = sig[:2].strip() if sig else "⚪"
            bg = {"🟢":"#162312", "🟡":"#1a1a12", "🔴":"#2a1212", "⚪":"#1a1a2e"}
            border = {"🟢":"#49aa19", "🟡":"#d4b106", "🔴":"#d32029", "⚪":"#555"}.get(sig_key, "#555")
            st.markdown(f"""
<div style="background:{bg.get(sig_key, '#1a1a2e')};border-left:4px solid {border};padding:16px;border-radius:8px;margin-bottom:8px">
<div style="display:flex;justify-content:space-between"><strong>{code} {name}</strong><span>{sig}</span></div>
<div style="display:flex;gap:24px;margin-top:8px;font-size:14px;color:#ccc">
<span>💰 {r['price']:.2f}</span><span>📊 {r['score']:.0f}分</span>
<span>📈 {r['trend']}</span><span>⛔ {r['stop']['price']:.2f}</span>
<span>⚠️ {r['risk']['level'].replace('⛔','极高').replace('⚠️','高').replace('⚡','中').replace('✅','低')}</span>
</div></div>""", unsafe_allow_html=True)

    st.caption("每5分钟自动刷新")

# ═══ TAB 4: 每日报告 ═══
with tabs[3]:
    st.header("📄 每日量化报告")
    report_dir = Path(__file__).parent / "trade-signals"
    if report_dir.exists():
        files = sorted(report_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)
        if files:
            for f in files[:10]:
                mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%m-%d %H:%M")
                with st.expander(f"{f.stem} ({mtime})"):
                    st.text(f.read_text(encoding="utf-8")[:2000])
        else:
            st.info("暂无报告，系统每天 9:00/15:00 自动生成")
    else:
        st.info("报告目录不存在，系统将在首次运行后生成")

    st.divider()
    st.caption("⚠️ 以上内容仅供研究参考，不构成投资建议 | 技术分析基于历史数据，请结合实际情况决策")
