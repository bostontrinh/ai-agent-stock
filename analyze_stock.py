from market import get_history
from indicator import calculate_indicators
from build_context import build_ai_context
from ai_analysis import analyse
from chart import create_kline_chart
from report import save_html_report

import plotly.io as pio


def analyze_stock(stock_code=None, df=None):
    """
    AI股票分析

    支持：

    analyze_stock(stock_code="300750")

    或：

    analyze_stock(df=df)
    """


    # 没有传入数据，自动获取
    if df is None:

        if stock_code is None:
            raise ValueError(
                "stock_code 和 df 不能同时为空"
            )


        # 获取历史行情
        df = get_history(stock_code)


        # 技术指标计算
        df = calculate_indicators(df)



    # 默认股票代码
    if stock_code is None:
        stock_code = "Unknown"



    # =====================
    # AI分析
    # =====================

    context = build_ai_context(df)

    ai_result = analyse(context)



    # =====================
    # 生成K线
    # =====================

    fig = create_kline_chart(df)



    # =====================
    # 生成HTML图表
    # =====================

    chart_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn"
    )



    # =====================
    # 保存报告
    # =====================

    save_html_report(
        stock_code,
        ai_result,
        chart_html
    )



    # =====================
    # 返回给网页
    # =====================

    result = {

        # AI结果
        **ai_result,


        # 股票数据
        "data": df,


        # Plotly图
        "chart": fig,


        # 股票代码
        "stock_code": stock_code
    }


    return result



if __name__ == "__main__":


    stock = input(
        "请输入股票代码："
    )


    result = analyze_stock(
        stock_code=stock
    )


    print(result)