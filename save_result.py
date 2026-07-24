import pandas as pd


def save_to_excel(results):
    """
    保存分析结果到 Excel
    """

    df = pd.DataFrame(results)

    df = df[
        [
            "code",
            "name",
            "score",
            "signal",
            "trend",
            "risk",
            "support",
            "resistance",
            "stop_loss",
            "take_profit",
            "holding_days",
            "reason",
        ]
    ]

    df.to_excel("stock_report.xlsx", index=False)

    print("✅ 已保存：stock_report.xlsx")