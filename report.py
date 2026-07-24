import os


def save_html_report(stock_code, result, chart_html):
    """
    生成股票分析报告 HTML 文件并保存到 reports 目录。

    参数:
        stock_code (str): 股票代码，用于文件名和报告标题。
        result (dict): 包含分析结果的字典，键包括：
            - score: 综合评分
            - stars: 评级
            - trend: 趋势
            - signal: 建议
            - risk: 风险
            - buy_zone: 买入区
            - support: 支撑位
            - resistance: 压力位
            - stop_loss: 止损
            - take_profit: 止盈
            - reason: AI 结论
            - analysis (可选): 详细分析文本
        chart_html (str): K 线图的 HTML 代码，直接嵌入报告。

    返回:
        str: 生成的 HTML 文件路径。
    """
    # 确保 reports 目录存在
    os.makedirs("reports", exist_ok=True)

    # 构建完整的 HTML 内容
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{stock_code} AI分析报告</title>

<style>

body{{
font-family:Arial;
background:#f5f5f5;
margin:40px;
}}

.container{{
background:white;
padding:30px;
border-radius:12px;
box-shadow:0 0 10px #ddd;
}}

table{{
width:100%;
border-collapse:collapse;
}}

td{{
padding:10px;
border-bottom:1px solid #eee;
}}

h1,h2{{
color:#333;
}}

.analysis{{
background:#fafafa;
padding:20px;
margin-top:20px;
border-left:5px solid #3b82f6;
}}

</style>

</head>

<body>

<div class="container">

<h1>AI股票分析报告</h1>

<h2>{stock_code}</h2>

<table>

<tr>
<td>综合评分</td>
<td>{result.get("score","N/A")}</td>
</tr>

<tr>
<td>评级</td>
<td>{result.get("stars","N/A")}</td>
</tr>

<tr>
<td>趋势</td>
<td>{result.get("trend","N/A")}</td>
</tr>

<tr>
<td>建议</td>
<td>{result.get("signal","N/A")}</td>
</tr>

<tr>
<td>风险</td>
<td>{result.get("risk","N/A")}</td>
</tr>

<tr>
<td>买入区</td>
<td>{result.get("buy_zone","N/A")}</td>
</tr>

<tr>
<td>支撑位</td>
<td>{result.get("support","N/A")}</td>
</tr>

<tr>
<td>压力位</td>
<td>{result.get("resistance","N/A")}</td>
</tr>

<tr>
<td>止损</td>
<td>{result.get("stop_loss","N/A")}</td>
</tr>

<tr>
<td>止盈</td>
<td>{result.get("take_profit","N/A")}</td>
</tr>

</table>

<div class="analysis">

<h2>AI结论</h2>

<p>{result.get("reason","N/A")}</p>

<h2>详细分析</h2>

<p>{result.get("analysis","")}</p>

</div>

<h2>K线图</h2>

{chart_html}

</div>

</body>

</html>
"""

    # 生成文件名
    filename = f"reports/{stock_code}.html"

    # 写入 HTML 文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    # 输出提示信息
    print(f"\n报告已生成：{filename}")
    
    # 返回文件路径
    return filename
