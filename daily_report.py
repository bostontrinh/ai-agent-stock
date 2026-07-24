from datetime import datetime
import os



def save_daily_report(results):


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    os.makedirs(
        "reports",
        exist_ok=True
    )


    filename = (
        f"reports/daily_{today}.html"
    )



    html = f"""
<html>

<head>

<meta charset="UTF-8">

<title>
AI每日股票报告
</title>

</head>


<body>


<h1>
📈 AI每日股票报告
</h1>


<h3>
日期：
{today}
</h3>


<hr>


<h2>
🏆 今日推荐股票
</h2>

"""



    for i,item in enumerate(
        results[:5],
        start=1
    ):


        html += f"""

<h3>
第{i}名：
{item['股票名称']}
({item['股票代码']})
</h3>


<p>
综合评分：
{item['排名分']}
</p>


<p>
程序评分：
{item['程序评分']}
</p>


<p>
资金评分：
{item['资金评分']}
</p>


<p>
AI评分：
{item['AI评分']}
</p>


<p>
建议：
{item['建议']}
</p>


<p>
风险：
{item['风险']}
</p>


<hr>

"""



    html += """

</body>

</html>

"""



    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            html
        )



    print(
        f"日报生成：{filename}"
    )


    return filename