import json
import os
from binance.exceptions import BinanceAPIException
import load_save_params


def leverage_set(client, pair, stop_loss, status: str = "None"):
    """leverage is count based on stop loss divided by safety factor"""

    leverage = int(load_save_params.load_parameter(pair, "leverage"))

    if status.lower() == "set":
        # setting leverage, do not change to auto-change leverage - possible leverage change on pending position!
        try:
            response = client.futures_change_leverage(symbol=pair.lower(), leverage=leverage)
        except BinanceAPIException as e:
            print(f"Error Code: {e.status_code} ")
            print(e.message)

        else:
            leverage = int(response['leverage'])
            print(f"Leverage changed to: {leverage}x on Binance server.")

    if status.lower() == "plus":
        if leverage < (1 / (stop_loss / 100)):
            leverage += 1

    elif status.lower() == "minus":
        if leverage > 1:
            leverage -= 1

    load_save_params.save_parameter(pair=pair, kwarg="leverage", value=leverage)


# ----tests----
leverage_set(client=None, pair="xmrusdt", stop_loss=5, status="plus")
leverage_set(client=None, pair="xmrusdt", stop_loss=5, status="plus")
