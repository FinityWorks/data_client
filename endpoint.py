import time

from fastapi import FastAPI, WebSocket
from fin_tools.aggregations import BarMaker
from fin_tools.clients import Binance
from fin_tools.formatting import df_to_dict

app = FastAPI()


barmaker = BarMaker(bar_length_limit=50, imbal_limit=10)


@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        binance = Binance()
        df = await binance.pull_data()
        await binance.close()

        barmaker.update_bars(df)
        vals = df_to_dict(barmaker.bars, "tick_dir_imbal_bar_id")

        await websocket.send_json(
            {
                "bars": {
                    **vals,
                    "type": "candlestick",
                    "name": "Candlestick Chart",
                },
                "layout": {
                    "title": "Bars",
                    "xaxis": {"title": "Index", "tick_vals": vals["tick_dir_imbal_bar_id"]},
                    "yaxis": {
                        "title": "Price",
                    },
                },
            }
        )
        time.sleep(1)
