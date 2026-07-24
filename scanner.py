from capital import calculate_capital_score
from market import get_history
from indicator import calculate_indicators
from score_engine import calculate_score
from stock_pool import STOCK_POOL
from analyze_stock import analyze_stock



def scan_market():

    result = []


    print("\n开始第一轮量化筛选...\n")



    # =====================
    # 第一轮：技术 + 资金
    # =====================

    for code, name in STOCK_POOL.items():


        print(
            f"量化分析 {code} {name}"
        )


        try:


            df = get_history(
                code
            )


            df = calculate_indicators(
                df
            )


            score = calculate_score(
                df
            )


            capital_score = calculate_capital_score(
                df
            )


            latest = df.iloc[-1]



            total_score = (
                score["score"] * 0.7
                +
                capital_score * 0.3
            )



            result.append(
                {

                    "代码":
                        code,


                    "名称":
                        name,


                    "df":
                        df,


                    "程序评分":
                        score["score"],


                    "资金评分":
                        capital_score,


                    "综合分":
                        round(
                            total_score,
                            2
                        ),


                    "detail":
                        score["detail"],


                    "latest":
                        latest

                }
            )


        except Exception as e:


            print(
                f"{code}失败:{e}"
            )



    # 综合排序

    result.sort(
        key=lambda x:x["综合分"],
        reverse=True
    )



    # 前10进入AI

    top10 = result[:10]



    print(
        "\n进入AI深度分析...\n"
    )



    final = []



    # =====================
    # AI分析
    # =====================

    for item in top10:


        try:


            ai = analyze_stock(
                stock_code=item["代码"],
                df=item["df"]
            )



            latest = item["latest"]



            ai_score = int(
                ai.get(
                    "score",
                    0
                )
            )



            final_score = (
                item["综合分"] * 0.6
                +
                ai_score * 0.4
            )



            final.append(
                {

                    "排名分":
                        round(
                            final_score,
                            2
                        ),


                    "程序评分":
                        item["程序评分"],


                    "资金评分":
                        item["资金评分"],


                    "AI评分":
                        ai_score,


                    "股票代码":
                        item["代码"],


                    "股票名称":
                        item["名称"],


                    "星级":
                        ai.get(
                            "stars",
                            ""
                        ),


                    "建议":
                        ai.get(
                            "signal",
                            ""
                        ),


                    "风险":
                        ai.get(
                            "risk",
                            ""
                        ),


                    "成功率":
                        ai.get(
                            "probability",
                            ""
                        ),


                    "均线":
                        (
                            "多头"
                            if latest["MA5"] > latest["MA20"]
                            else
                            "空头"
                        ),


                    "MACD":
                        (
                            "金叉"
                            if latest["MACD"] > latest["MACD_SIGNAL"]
                            else
                            "死叉"
                        ),


                    "RSI":
                        float(
                            round(
                                latest["RSI"],
                                2
                            )
                        ),


                    "成交量":
                        (
                            "放量"
                            if latest["volume"] > latest["VOL_MA5"]
                            else
                            "缩量"
                        ),


                    "突破":
                        (
                            "突破"
                            if latest["Close"] > latest["HIGH20"]
                            else
                            "未突破"
                        )

                }
            )


        except Exception as e:


            print(
                f"AI分析失败 {item['代码']}:{e}"
            )



    # 最终排名

    final.sort(
        key=lambda x:x["排名分"],
        reverse=True
    )


    return final