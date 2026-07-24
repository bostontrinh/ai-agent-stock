from plotly.subplots import make_subplots
import plotly.graph_objects as go


def create_kline_chart(df):

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.18, 0.17, 0.15]
    )

    # ======================
    # K线
    # ======================
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="K线",
            increasing_line_color="red",
            decreasing_line_color="green"
        ),
        row=1,
        col=1
    )

    # ======================
    # MA5
    # ======================
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA5"],
            mode="lines",
            name="MA5"
        ),
        row=1,
        col=1
    )

    # ======================
    # MA10
    # ======================
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA10"],
            mode="lines",
            name="MA10"
        ),
        row=1,
        col=1
    )

    # ======================
    # MA20
    # ======================
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA20"],
            mode="lines",
            name="MA20"
        ),
        row=1,
        col=1
    )

    # ======================
    # MA60
    # ======================
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA60"],
            mode="lines",
            name="MA60"
        ),
        row=1,
        col=1
    )

    # ======================
    # 成交量
    # ======================
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="成交量"
        ),
        row=2,
        col=1
    )

    # ======================
    # MACD
    # ======================
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MACD"],
            mode="lines",
            name="MACD"
        ),
        row=3,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MACD_SIGNAL"],
            mode="lines",
            name="Signal"
        ),
        row=3,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["MACD_HIST"],
            name="MACD柱"
        ),
        row=3,
        col=1
    )

    # ======================
    # RSI
    # ======================
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            mode="lines",
            name="RSI"
        ),
        row=4,
        col=1
    )

    # RSI 超买线
    fig.add_hline(
        y=70,
        line_dash="dash",
        row=4,
        col=1
    )

    # RSI 超卖线
    fig.add_hline(
        y=30,
        line_dash="dash",
        row=4,
        col=1
    )

    fig.update_layout(
        title="📈 AI股票技术分析图",
        height=1350,
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    fig.update_yaxes(title_text="价格", row=1, col=1)
    fig.update_yaxes(title_text="成交量", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="RSI", row=4, col=1)

    return fig