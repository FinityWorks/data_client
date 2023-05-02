from fastapi import FastAPI, WebSocket
from fin_tools.aggregations import BarMaker
from fin_tools.clients import Binance
from fin_tools.formatting import df_to_dict

app = FastAPI()


@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        binance = Binance()
        df = await binance.pull_data()
        await binance.close()

        df = BarMaker.create_imbalance_bars(df, "tick_dir", 5).rename(
            {"tick_dir_imbal_bar_id": "x"}
        )
        vals = df_to_dict(df, sort="x")

        await websocket.send_json(
            {
                "bars": {
                    **vals,
                    "type": "candlestick",
                    "name": "Candlestick Chart",
                },
                "layout": {
                    "title": "Bars",
                    "xaxis": {"title": "Index", "tick_vals": vals["x"]},
                    "yaxis": {
                        "title": "Price",
                    },
                },
            }
        )
        # await websocket.send_json(x)
