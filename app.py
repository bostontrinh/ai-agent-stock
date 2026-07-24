from daily_report import save_daily_report
import streamlit as st
import plotly.graph_objects as go

from analyze_stock import analyze_stock
from history import save_history, load_history
from scanner import scan_market


st.set_page_config(
    page_title="AI股票分析系统",
    page_icon="📈",
    layout="wide"
)


st.title("📈 AI 股票分析系统")


code = st.text_input(
    "股票代码",
    value="300750"
)



# =====================
# 单股票分析
# =====================


if st.button(
    "开始分析",
    key="analysis_button"
):


    with st.spinner(
        "AI正在分析，请稍候..."
    ):


        result = analyze_stock(
            stock_code=code
        )


    save_history(
        code,
        result
    )


    st.success(
        "分析完成！"
    )


    df = result["data"]

    latest = df.iloc[-1]



    # 股票概览

    st.header(
        "📌 股票概览"
    )


    c1,c2,c3,c4,c5 = st.columns(5)


    with c1:

        st.metric(
            "最新价格",
            f"{latest['Close']:.2f}"
        )


    with c2:

        st.metric(
            "涨跌幅",
            f"{latest['CHANGE_PCT']:.2f}%"
        )


    with c3:

        st.metric(
            "AI评分",
            f"{result['score']}分"
        )


    with c4:

        st.metric(
            "建议",
            result["signal"]
        )


    with c5:

        st.metric(
            "风险",
            result["risk"]
        )



    st.divider()



    # =====================
    # K线
    # =====================


    st.header(
        "📈 K线走势"
    )


    fig = go.Figure()



    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="K线"
        )
    )



    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA5"],
            name="MA5"
        )
    )



    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA20"],
            name="MA20"
        )
    )



    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False
    )



    st.plotly_chart(
        fig,
        use_container_width=True
    )



    # =====================
    # MACD
    # =====================


    st.header(
        "📉 MACD"
    )


    macd_fig = go.Figure()


    macd_fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MACD"],
            name="DIF"
        )
    )


    macd_fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MACD_SIGNAL"],
            name="DEA"
        )
    )


    macd_fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["MACD_HIST"],
            name="柱"
        )
    )


    st.plotly_chart(
        macd_fig,
        use_container_width=True
    )
        # =====================
    # RSI
    # =====================


    st.header(
        "📈 RSI"
    )


    rsi_fig = go.Figure()


    rsi_fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            name="RSI"
        )
    )


    rsi_fig.add_hline(
        y=70,
        line_dash="dash"
    )


    rsi_fig.add_hline(
        y=30,
        line_dash="dash"
    )


    rsi_fig.update_layout(
        height=350
    )


    st.plotly_chart(
        rsi_fig,
        use_container_width=True
    )



    # =====================
    # AI综合决策
    # =====================


    st.divider()


    st.header(
        "🤖 AI综合决策"
    )


    trend = (
        "多头 ✅"
        if latest["MA5"] > latest["MA20"]
        else
        "空头 ⚠️"
    )


    macd_state = (
        "金叉 ✅"
        if latest["MACD"] > latest["MACD_SIGNAL"]
        else
        "死叉 ⚠️"
    )


    if latest["RSI"] > 70:

        rsi_state = "超买 ⚠️"

    elif latest["RSI"] < 30:

        rsi_state = "超卖 ⚠️"

    else:

        rsi_state = "正常 ✅"



    a,b,c,d = st.columns(4)



    with a:

        st.metric(
            "趋势",
            trend
        )


    with b:

        st.metric(
            "MACD",
            macd_state
        )


    with c:

        st.metric(
            "RSI",
            rsi_state
        )


    with d:

        st.metric(
            "AI评分",
            result["score"]
        )



    if (
        result["score"] >= 70
        and latest["MA5"] > latest["MA20"]
        and latest["MACD"] > latest["MACD_SIGNAL"]
    ):

        st.success(
            "🟢 多头信号"
        )

    elif result["score"] <= 40:

        st.error(
            "🔴 风险较高"
        )

    else:

        st.warning(
            "🟡 观望信号"
        )



    # =====================
    # 交易建议
    # =====================


    st.divider()


    st.header(
        "💰 交易建议"
    )


    st.write(
        f"支撑位：{result['support']}"
    )


    st.write(
        f"压力位：{result['resistance']}"
    )


    st.write(
        f"买入区：{result['buy_zone']}"
    )


    st.write(
        f"止损位：{result['stop_loss']}"
    )


    st.write(
        f"止盈位：{result['take_profit']}"
    )



    # =====================
    # 风控中心（新增）
    # =====================


    st.divider()


    st.header(
        "🛡️ 风控中心"
    )


    with st.expander(
        "📊 止损/止盈策略",
        expanded=True
    ):


        from risk_control import (
            calc_stop_loss,
            calc_take_profit,
            calc_risk_score,
            calc_volatility,
            generate_warning,
        )
        from position_sizing import (
            fixed_pct_sizing,
            kelly_criterion,
        )


        entry = st.number_input(
            "你的买入价",
            value=float(latest["Close"]),
            step=0.01,
            format="%.2f",
            key="entry_price"
        )


        current = float(latest["Close"])
        loss_pct = (current - entry) / entry * 100


        st.metric(
            "当前盈亏",
            f"{loss_pct:+.2f}%",
            delta=None
        )


        # 止损策略
        c1, c2 = st.columns(2)


        with c1:


            st.subheader("🔴 止损建议")

            stops = [
                calc_stop_loss(entry, "hard"),
                calc_stop_loss(entry, "atr", df),
                calc_stop_loss(entry, "support", df),
                calc_stop_loss(entry, "ma", df),
            ]


            for s in stops:
                st.write(
                    f"**{s['method']}**: {s['price']}元 ({s['pct']:+.2f}%)"
                )


        with c2:


            st.subheader("🟢 止盈建议")

            takes = calc_take_profit(entry, "risk_reward", abs(loss_pct) if loss_pct < 0 else 8)


            for t in takes:
                st.write(
                    f"**{t['method']}**: {t['price']}元 (+{t['pct']:.1f}%)"
                )


    with st.expander(
        "📏 仓位管理"
    ):


        capital = st.number_input(
            "总资金（元）",
            value=100000,
            step=10000,
            format="%d",
            key="total_capital"
        )


        sizing = fixed_pct_sizing(capital)


        st.info(
            f"建议买入 **{sizing['position_size']:.0f}元** "
            f"（占 {sizing['position_pct']:.1f}%）"
        )


        st.write(
            f"单笔最大亏损：{sizing['max_loss']:.0f}元 "
            f"（{sizing['max_loss_pct']:.1f}%）"
        )


        # 组合建议
        st.subheader("组合配置建议")

        from position_sizing import calculate_max_positions

        max_pos = calculate_max_positions(capital, 0.08)
        st.write(max_pos["suggestion"])

        from portfolio_manager import portfolio_position_sizing

        positions = portfolio_position_sizing(capital)
        for p in positions:
            st.write(f"  #{p['stock_no']}: {p['amount']:.0f}元 ({p['pct']:.1f}%)")


    with st.expander(
        "⚠️ 风险评分"
    ):


        risk = calc_risk_score(df)
        vol = calc_volatility(df)
        warnings = generate_warning(entry, current, df)


        c1, c2, c3 = st.columns(3)


        with c1:
            st.metric("风险等级", risk["level"])

        with c2:
            st.metric("年化波动", f"{vol['annual_vol']}%")

        with c3:
            st.metric("日均波幅", vol["avg_daily_range"])


        if warnings:
            st.subheader("预警列表")
            for w in warnings:
                emoji = {"注意": "⚡", "警告": "⚠️", "严重": "⛔"}.get(
                    w["level"], "📌"
                )
                st.write(f"{emoji} **[{w['level']}]** {w['msg']}")
                st.write(f"  建议操作：{w['action']}")


    # =====================
    # AI报告
    # =====================


    st.divider()


    st.header(
        "🤖 AI分析报告"
    )


    st.info(
        result["reason"]
    )


    st.write(
        result["analysis"]
    )



# =====================
# 历史分析记录
# =====================


st.divider()


st.header(
    "📁 历史分析记录"
)


history = load_history()



if history:


    for item in history[:10]:


        with st.expander(
            f"{item['stock_code']}  {item['time']}"
        ):


            st.write(
                f"评分：{item['score']}分"
            )


            st.write(
                f"趋势：{item['trend']}"
            )


            st.write(
                f"建议：{item['signal']}"
            )


else:


    st.write(
        "暂无历史记录"
    )



# =====================
# AI市场扫描
# =====================


st.divider()


st.header(
    "🔍 AI市场扫描"
)


st.write(
    "扫描股票池，自动生成AI选股排行榜"
)



if st.button(
    "🚀 开始扫描股票池",
    key="market_scan"
):


    try:


        with st.spinner(
            "正在扫描市场..."
        ):


            ranking = scan_market()


            report_file = save_daily_report(
                ranking
            )


        st.success(
            "扫描完成！"
        )



        if len(ranking) == 0:


            st.warning(
                "没有扫描结果"
            )


        else:


            st.subheader(
                "🏆 AI选股排行榜"
            )



            for i,item in enumerate(
                ranking,
                start=1
            ):


                if i == 1:

                    icon="🥇"

                elif i == 2:

                    icon="🥈"

                elif i == 3:

                    icon="🥉"

                else:

                    icon="⭐"



                with st.expander(
                    f"{icon} 第{i}名 {item['股票名称']} ({item['股票代码']})"
                ):


                    c1,c2,c3,c4 = st.columns(4)


                    c1.metric(
                        "程序评分",
                        item["程序评分"]
                    )


                    c2.metric(
                        "AI评分",
                        item["AI评分"]
                    )


                    c3.metric(
                        "建议",
                        item["建议"]
                    )


                    c4.metric(
                        "风险",
                        item["风险"]
                    )


                    st.write(
                        f"""
⭐ 星级：
{item['星级']}

成功率：
{item['成功率']}

均线：
{item['均线']}

MACD：
{item['MACD']}

RSI：
{item['RSI']}

成交量：
{item['成交量']}

突破：
{item['突破']}
"""
                    )


    except Exception as e:


        st.error(
            f"扫描失败：{e}"
        )