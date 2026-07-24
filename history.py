import json
import os
from datetime import datetime


FILE = "data/history.json"



def save_history(stock_code, result):

    os.makedirs(
        "data",
        exist_ok=True
    )


    history = []


    if os.path.exists(FILE):

        with open(
            FILE,
            "r",
            encoding="utf-8"
        ) as f:

            history = json.load(f)



    item = {

        "stock_code": stock_code,

        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "score": result.get(
            "score",
            0
        ),

        "signal": result.get(
            "signal",
            ""
        ),

        "trend": result.get(
            "trend",
            ""
        )

    }


    history.insert(
        0,
        item
    )


    with open(
        FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=2
        )



def load_history():

    if not os.path.exists(FILE):

        return []


    with open(
        FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)