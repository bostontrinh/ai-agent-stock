def calculate_capital_score(df):

    score = 50


    latest = df.iloc[-1]


    # 成交量放大

    if latest["volume"] > latest["VOL_MA5"]:

        score += 15

    else:

        score -= 5



    # 换手率

    if "turnover" in df.columns:


        turnover = latest["turnover"]


        if turnover > 5:

            score += 10


        elif turnover < 1:

            score -= 5



    # 涨跌趋势

    if latest["CHANGE_PCT"] > 0:

        score += 10

    else:

        score -= 5



    # 限制范围

    if score > 100:

        score = 100


    if score < 0:

        score = 0


    return score