from tkinter import *
import csv
import json
import time
import math
import websocket
import threading
from datetime import datetime
from binance import Client
from binance.exceptions import BinanceAPIException

from private import api_keys


public_key, secret_key = api_keys.keyapi()

client = Client(public_key, secret_key)


class BotGUI:
    PAIRS = [
        "XMRUSDT",
        "BTCUSDT",
        "BNBUSDT"
    ]

    DIM_X = {
        # Frames:
        "setting_params_pos_x": 5,
        "result_frame_pos_x": 5,
        "control_panel_pos_x": 325,
        "actual_frame_pos_x": 600,
        "last_trade_frame_pos_x": 600,
        "order_book_pos_x": 880,
        "recent_trades_pos_x": 1190,
        "last_trans_frame_pos_x": 5,

        # Buttons:
        # ---Control Panel:---
        "auto_trade_pos_x": 5,
        "long_pos_x": 15,

        "plus_minus_set_x": 210,
        "plus_minus_set_2_x": 210,

        "trailing_pos_x": 0,
        "stop_loss_pos_x": 0,
        "next_pos_step_pos_x": 0,
        "stop_loss_val_pos_x": 300,
        "max_drawdawn_pos_x": 0,
        "max_daily_loss_pos_x": 0,
        "max_daily_loss_count_pos_x": 0,

        # Labels:
        "ticker_pos_x": 45,
        "balance_usdt_pos_x": 0,
        "actual_drawdawn_pos_x": 300,
        "actual_daily_loss_pos_x": 300,
        "actual_daily_loss_count_pos_x": 300,
        "lever_pos_x": 0,
        "percent_risk_pos_x": 0,
        "dollar_risk_pos_x": 0,
        "build_up_count_pos_x": 0,
        "one_trade_qunat_pos_x": 0,

        # Drop lists:
        "drop_pos_x": 35,
        }

    DIM_Y = {
        # Frames:
        "setting_params_pos_y": 5,
        "result_frame_pos_y": 430,
        "control_panel_pos_y": 5,
        "actual_frame_pos_y": 5,
        "last_trade_frame_pos_y": 430,
        "order_book_pos_y": 5,
        "recent_trades_pos_y": 5,
        "last_trans_frame_pos_y": 670,

        # Buttons:
        #  Control Panel:
        "auto_trade_pos_y": 120,
        "long_pos_y": 175,

        "trailing_pos_y": 205,
        "stop_loss_pos_y": 145,
        "next_pos_step_pos_y": 175,
        "stop_loss_val_pos_y": 0,
        "max_drawdawn_pos_y": 0,
        "max_daily_loss_pos_y": 50,
        "max_daily_loss_count_pos_y": 100,

        # Labels:
        "ticker_pos_y": 45,
        "balance_usdt_pos_y": 0,
        "lever_pos_y": 250,
        "actual_drawdawn_pos_y": 50,
        "actual_daily_loss_pos_y": 100,
        "actual_daily_loss_count_pos_y": 150,
        "percent_risk_pos_y": 300,
        "dollar_risk_pos_y": 30,
        "build_up_count_pos_y": 350,
        "one_trade_qunat_pos_y": 60,

        # Drop lists:
        "drop_pos_y": 3,
    }

    def __init__(self, master):
        self.master = master
        self.PAIR = None
        self.LEVERAGE = 26
        self.TRAILING_STOP = 1
        self.STOP_LOSS = 3
        self.NEXT_POS_STEP = 1
        self.MAX_DRAWDAWN = -25
        self.MAX_DAILY_LOSS = -10
        self.MAX_DAILY_LOSS_COUNT = 3
        self.ACTUAL_DRAWDAWN = 0
        self.ACTUAL_DAILY_LOSS = 0
        self.ACTUAL_DAILY_LOSS_COUNT = 0
        self.OPEN_POSITION_TYPE = "MARKET"
        self.CLOSE_POSITION_TYPE = "MARKET"
        self.PERCENT_TO_RISK = 1
        self.BUILD_UP_POSITION_COUNT = 3
        self.ONE_TRADE_QUANTITY = 0
        self.DOLLAR_TO_RISK = 0
        self.IS_POSITION_LIVE = 0
        self.ENTRY_PRICE = 0
        self.FIRST_TRADE_ENTRY_PRICE = 0
        self.ACTUAL_LEVERAGE = 0
        self.TRADED_AMOUNT = 0
        self.POSITION_START_UPDATE_TIME = 0
        self.UNREALIZED_PNL = 0
        self.TS_HIT_PNL = 0
        self.FILLED_ORDERS = 0
        self.EXTREME_PRICE = 0
        self.SETTED_STOPLOSS_PRICE = 0
        self.SETTED_TRAILING_PRICE = 0
        self.LAST_TRADE_ENTRY_PRICE = 0
        self.LAST_TRADE_AVERAGE_CLOSE_PRICE = 0
        self.LAST_TRADE_QUANTITY = 0
        self.LAST_TRADE_NET_PNL = 0
        self.LAST_TRADE_PNL = 0
        self.LAST_TRADE_FEE = 0
        self.LAST_TRADE_SIDE = None
        self.START_POSITIONS_FEE = 0
        self.NET_UNREALIZED_PNL_AMOUNT = 0
        self.orderbook_levels = 20
        self.LAST_TRADE_CLOSE_TIME = 0
        self.init_balance_usdt = 100
        self.last_trade_price = 0
        self.max_drawdawn_percent = 0
        self.NEW_LONG_ORDER = 0
        self.NEW_SHORT_ORDER = 0
        self.LIMIT_ORDER_PRICE = 0

        self.balance_usdt = None
        self.trade_permission = False
        self.autotrade = False
        self.another_trade_signal = False
        self.first_trade = False
        self.limit_order_permission = False

        # variables used during start position:
        self.SIDE = None
        self.stop_loss = None
        self.trail_stop_requirement = None
        self.stop_loss = 0
        self.trailing_stop = None
        self.quantity = None
        self.actual_price = 0
        # variables used to compare values in trailing stop and stop loss loop
        self.stop_loss_comp = None
        self.actual_extreme_comp = None
        self.extreme_activate_comp = None
        self.actual_trailing_comp = None

        # Order Book:
        self.actual_bid_price = 0
        self.actual_bid_amount = 0
        self.actual_ask_price = 0
        self.actual_ask_amount = 0

        # Dimensions:
        self.height = 1
        self.width = 3
        self.font = 2

        # --------------------------- Pre-Loading file at start program: ------------------------------
        start_time = time.time()

        self.frames()
        self.dropped_lists()
        threading.Thread(daemon=True, target=self.order_book_datastream).start()

        while True:
            if self.actual_ask_price == 0:
                time.sleep(1)
            else:
                break

        self.buttons()
        self.labels_show()
        self.loading_config_file()
        self.refresh_data()

        threading.Thread(daemon=True, target=self.start_checking_sl_tp).start()

        print(f"Time to preload GUI: {time.time() - start_time} s ")

    # ------------------------------- Loading, update and saving data -------------------------------------
    def dropped_lists(self):
        # Dropped List:
        #   Pair Selection:
        self.pair_selection = StringVar()
        self.pair_selection.set(self.PAIRS[0])
        self.drop_selected_pair = OptionMenu(self.control_panel, self.pair_selection, *self.PAIRS)
        self.PAIR = self.pair_selection.get()

        #   Pair Selection position:
        self.drop_selected_pair.place(x=self.DIM_X["drop_pos_x"], y=self.DIM_Y["drop_pos_y"])

    def labels_text(self):

        self.leverage_text = f"Leverage:\t   {self.LEVERAGE} x "
        self.trailing_stop_text = f"Trailing Stop:\t{self.TRAILING_STOP} % "
        self.stop_loss_text = f"Stop Loss:\t{self.STOP_LOSS} % "
        self.next_pos_step_text = f"Next Pos. Step:\t{self.NEXT_POS_STEP} % "
        self.stop_loss_prices_text = f"Stop Loss Prices:\n " \
            f"LONG: {round(self.ENTRY_PRICE * (1 - self.STOP_LOSS/100), 2)}, " \
            f"SHORT: {round(self.ENTRY_PRICE * (1 + self.STOP_LOSS/100), 2)} "
        self.max_drawdawn_text = f"Max Drawdawn:\t{self.MAX_DRAWDAWN} $ "
        self.max_daily_loss_text = f"Max Daily Loss:\t{self.MAX_DAILY_LOSS} $ "
        self.max_daily_loss_count_text = f"Max Daily Loss\t{self.MAX_DAILY_LOSS_COUNT} x\n" \
                                         f"Transactions:"
        self.balance_usdt_text = f"Account Balance:\t{self.balance_usdt} $ "

        self.actual_drawdawn_text = f"Actual Drawdawn:\t{self.ACTUAL_DRAWDAWN} $ "
        self.actual_daily_loss_text = f"Actual Daily Loss:\t{self.ACTUAL_DAILY_LOSS} $ "
        self.actual_daily_loss_count_text = f"Actual Daily Loss\t{self.ACTUAL_DAILY_LOSS_COUNT} x" \
                                            f"\nTransactions:"
        self.percent_to_risk_text = f"Balance to risk:\t{self.PERCENT_TO_RISK} % \n"
        self.build_up_count_text = f"Number of\t{self.BUILD_UP_POSITION_COUNT}\ntransactions:"

        self.dollar_to_risk_text = f"Dollars to risk:\t{self.DOLLAR_TO_RISK} $ \n"
        self.quantity_one_trade_text = f"One Trade Amount:\t{self.ONE_TRADE_QUANTITY}\n"
        self.actual_ticker_text = f"Ticker Value [$]\n\n{self.actual_price}"

        # ----------------------------------------- Actual Trade ----------------------------------------------
        self.is_position_live_text = f"Position Status:\t{self.IS_POSITION_LIVE} "
        self.position_live_entry_text = f"Entry Price:\t{self.ENTRY_PRICE} $"
        self.actual_leverage_text = f"Leverage:\t\t{self.ACTUAL_LEVERAGE} x "
        self.position_live_amount_text = f"Traded Amount:\t{self.TRADED_AMOUNT} "
        self.position_filled_amount_text = f"Filled Orders:\t{self.TRADED_AMOUNT} / {self.quantity}  \n" \
            f"\t\t({self.FILLED_ORDERS} / {self.BUILD_UP_POSITION_COUNT}) "
        self.position_live_start_time_text = f"Start Time: {self.POSITION_START_UPDATE_TIME} "
        self.extreme_price_text = f"Extreme Price:\t{self.EXTREME_PRICE} $"
        self.setted_stoploss_text = f"Setted Stoploss:\t{self.SETTED_STOPLOSS_PRICE} $"
        self.setted_trailing_text = f"Setted Trailing:\t{self.SETTED_TRAILING_PRICE} $"
        self.unrealized_pnl_text = f"Unrealized PNL:\t{self.UNREALIZED_PNL} %"
        self.pnl_after_reaching_ts_text = f"Potential PNL:\t{self.TS_HIT_PNL} %"
        self.fee_to_pay_text = f"Fee to pay:\t{2 * self.START_POSITIONS_FEE} $"
        self.net_unrealized_pnl_text = f"Net Unrl. PNL:\t{self.NET_UNREALIZED_PNL_AMOUNT} $"

        # ------------------------------------------- Last Trade --------------------------------------------
        self.last_trade_side_text = f"Position Side: \t{self.LAST_TRADE_SIDE}"
        self.last_trade_entry_price_text = f"Entry Price: \t{self.LAST_TRADE_ENTRY_PRICE} $"
        self.last_trade_close_price_text = f"Close Price: \t{self.LAST_TRADE_AVERAGE_CLOSE_PRICE} $"
        self.last_trade_quantity_text = f"Amount: \t\t{self.LAST_TRADE_QUANTITY}"
        self.last_trade_fee_text = f"Paid Fee: \t{self.LAST_TRADE_FEE} $"
        self.last_trade_pnl_text = f"PNL: \t\t{self.LAST_TRADE_PNL} $"
        self.last_trade_pnl_fee_text = f"Net PNL: \t\t{self.LAST_TRADE_NET_PNL} $"

        # -------------------------------------------  New Order --------------------------------------------
        self.new_long_order_text = f"New Long Transaction will start at: {self.NEW_LONG_ORDER}"
        self.new_short_order_text = f"New Short Transaction will start at: {self.NEW_SHORT_ORDER}"

    def labels_show(self):
        # ------------------------------ Text Descriptions: -----------------------------------------------
        #   Leverage:
        self.leverage_value = Label(self.setting_parameters, font=self.font, text="")
        #   Trailing Stop:
        self.trailing_stop_value = Label(self.setting_parameters, font=self.font, text="")
        #   Stop Loss:
        self.stop_loss_value = Label(self.setting_parameters, font=self.font, text="")
        self.stop_loss_prices_value = Label(self.calculated_frame, font=self.font, text="")
        #   Next Position Step:
        self.next_pos_step_value = Label(self.setting_parameters, font=self.font, text="")
        #   Max Drawdawn:
        self.max_drawdawn_value = Label(self.setting_parameters, font=self.font, text="")
        #   Max Daily Loss:
        self.max_daily_loss_value = Label(self.setting_parameters, font=self.font, text="")
        #   Max Daily Loss Transactions:
        self.max_daily_loss_count_value = Label(self.setting_parameters, justify=LEFT, font=self.font, text="")
        #   Account Balance in USD:
        self.balance_usdt_value = Label(self.calculated_frame, font=self.font, text="")
        #   Actual Drawdawn:
        self.actual_drawdawn_value = Label(self.calculated_frame, font=self.font, text="")
        #   Actual Daily Loss:
        self.actual_daily_loss_value = Label(self.calculated_frame, font=self.font, text="")
        #   Actual Daily Loss Transactions:
        self.actual_daily_loss_count_value = Label(self.calculated_frame, justify=LEFT, font=self.font, text="")
        #   Percent to risk:
        self.percent_to_risk_value = Label(self.setting_parameters, font=self.font, text="")
        #   Transaction count to build up position:
        self.build_up_count_value = Label(self.setting_parameters, justify=LEFT, font=self.font, text="")
        #   Dollars to risk:
        self.dollar_to_risk_value = Label(self.calculated_frame, font=self.font, text="")
        #   Calculated Quantity per 1 trade during build up position:
        self.quantity_one_trade_value = Label(self.calculated_frame, font=self.font, text="")
        #   Actual Ticker Price:
        self.actual_ticker_value = Label(self.control_panel, font=self.font, borderwidth=5, relief="groove", bg="white",
                                         text="")

        # ----------------------------------------- Actual Trade ----------------------------------------------
        self.is_position_live_value = Label(self.actual_status_frame, font=self.font,
                                            text="")
        self.actual_leverage_value = Label(self.actual_status_frame, font=self.font,
                                           text="")
        self.position_live_entry_value = Label(self.actual_status_frame, font=self.font,
                                               text="")
        self.position_live_amount_value = Label(self.actual_status_frame, font=self.font,
                                                text="")
        self.position_filled_amount_value = Label(self.actual_status_frame, font=self.font,
                                                  text="")
        self.position_live_start_time_value = Label(self.actual_status_frame, font=self.font,
                                                    text="")
        self.extreme_price_value = Label(self.actual_status_frame, font=self.font,
                                         text="")
        self.setted_stoploss_value = Label(self.actual_status_frame, font=self.font,
                                           text="")
        self.setted_trailing_value = Label(self.actual_status_frame, font=self.font,
                                           text="")
        self.unrealized_pnl_value = Label(self.actual_status_frame, font=self.font,
                                          text="")
        self.pnl_after_reaching_ts_value = Label(self.actual_status_frame, font=self.font,
                                                 text="")
        self.fee_to_pay_value = Label(self.actual_status_frame, font=self.font,
                                      text="")
        self.net_unrealized_pnl_value = Label(self.actual_status_frame, font=self.font,
                                              text="")

        # ------------------------------------------- Last Trade --------------------------------------------
        self.last_trade_side_value = Label(self.last_trade_status_frame, font=self.font, text="")
        self.last_trade_entry_price_value = Label(self.last_trade_status_frame, font=self.font, text="")
        self.last_trade_close_price_value = Label(self.last_trade_status_frame, font=self.font, text="")
        self.last_trade_quantity_value = Label(self.last_trade_status_frame, font=self.font, text="")
        self.last_trade_fee_value = Label(self.last_trade_status_frame, font=self.font, text="")
        self.last_trade_pnl_value = Label(self.last_trade_status_frame, font=self.font, text="")
        self.last_trade_pnl_fee_value = Label(self.last_trade_status_frame, font=self.font, borderwidth=3,
                                              relief="groove", text="")

        # ------------------------------------------- Order Book --------------------------------------------
        self.actual_bid_price_value = Label(self.orderbook_frame, font=self.font, justify=LEFT, fg="green", text="")
        self.actual_ask_price_value = Label(self.orderbook_frame, font=self.font, justify=LEFT, fg="red", text="")

        # ------------------------------------------- Recent Trades --------------------------------------------
        self.recent_trades_label_buy = Label(self.recent_trades_frame, font=self.font, justify=LEFT, fg="green",
                                             text="")
        self.recent_trades_label_sell = Label(self.recent_trades_frame, font=self.font, justify=RIGHT, fg="red",
                                              text="")

        # -------------------------------------------  New Order --------------------------------------------
        self.new_long_order_entry = Entry(self.new_order_frame, font=self.font)
        self.new_long_order_value = Label(self.new_order_frame, font=self.font, text="")
        self.new_short_order_entry = Entry(self.new_order_frame, font=self.font)
        self.new_short_order_value = Label(self.new_order_frame, font=self.font, text="")

        # ------------------------------ Text Descriptions Position: ---------------------------------------
        #   Leverage:
        self.leverage_value.place(x=self.DIM_X["lever_pos_x"],
                                  y=self.DIM_Y["lever_pos_y"])
        #   Trailing Stop:
        self.trailing_stop_value.place(x=self.DIM_X["trailing_pos_x"],
                                       y=self.DIM_Y["trailing_pos_y"])
        #   Stop Loss:
        self.stop_loss_value.place(x=self.DIM_X["stop_loss_pos_x"],
                                   y=self.DIM_Y["stop_loss_pos_y"])
        self.stop_loss_prices_value.place(x=self.DIM_X["stop_loss_val_pos_x"],
                                          y=self.DIM_Y["stop_loss_val_pos_y"])
        self.next_pos_step_value.place(x=self.DIM_X["next_pos_step_pos_x"],
                                       y=self.DIM_Y["next_pos_step_pos_y"])
        #   Max Drawdawn:
        self.max_drawdawn_value.place(x=self.DIM_X["max_drawdawn_pos_x"],
                                      y=self.DIM_Y["max_drawdawn_pos_y"])
        #   Max Daily Loss:
        self.max_daily_loss_value.place(x=self.DIM_X["max_daily_loss_pos_x"],
                                        y=self.DIM_Y["max_daily_loss_pos_y"])
        #   Max Daily Loss Transactions:
        self.max_daily_loss_count_value.place(x=self.DIM_X["max_daily_loss_count_pos_x"],
                                              y=self.DIM_Y["max_daily_loss_count_pos_y"])
        #   Account Balance in USD:
        self.balance_usdt_value.place(x=self.DIM_X["balance_usdt_pos_x"],
                                      y=self.DIM_Y["balance_usdt_pos_y"])
        #   Actual Drawdawn:
        self.actual_drawdawn_value.place(x=self.DIM_X["actual_drawdawn_pos_x"],
                                         y=self.DIM_Y["actual_drawdawn_pos_y"])
        #   Actual Daily Loss:
        self.actual_daily_loss_value.place(x=self.DIM_X["actual_daily_loss_pos_x"],
                                           y=self.DIM_Y["actual_daily_loss_pos_y"])
        #   Actual Daily Loss Transactions:
        self.actual_daily_loss_count_value.place(x=self.DIM_X["actual_daily_loss_count_pos_x"],
                                                 y=self.DIM_Y["actual_daily_loss_count_pos_y"])
        #   Percent to risk:
        self.percent_to_risk_value.place(x=self.DIM_X["percent_risk_pos_x"],
                                         y=self.DIM_Y["percent_risk_pos_y"])
        #   Transaction count to build up position:
        self.build_up_count_value.place(x=self.DIM_X["build_up_count_pos_x"],
                                        y=self.DIM_Y["build_up_count_pos_y"])
        #   Dollars to risk:
        self.dollar_to_risk_value.place(x=self.DIM_X["dollar_risk_pos_x"],
                                        y=self.DIM_Y["dollar_risk_pos_y"])
        #   Calculated Quantity per 1 trade during build up position:
        self.quantity_one_trade_value.place(x=self.DIM_X["one_trade_qunat_pos_x"],
                                            y=self.DIM_Y["one_trade_qunat_pos_y"])
        #   Actual Ticker Price:
        self.actual_ticker_value.place(x=self.DIM_X["ticker_pos_x"],
                                       y=self.DIM_Y["ticker_pos_y"])

        # ------------------------------------------- Order Book --------------------------------------------

        self.actual_ask_price_value.place(x=0, y=0)
        self.actual_bid_price_value.place(x=0, y=self.orderbook_levels * 20)

        self.recent_trades_label_buy.place(x=0, y=0)
        self.recent_trades_label_sell.place(x=210, y=0)

        # ----------------------------------------- Actual Trade ----------------------------------------------
        self.is_position_live_value.place(x=0, y=0)
        self.actual_leverage_value.place(x=0, y=25)
        self.position_live_entry_value.place(x=0, y=50)
        self.position_live_amount_value.place(x=0, y=75)
        self.position_filled_amount_value.place(x=0, y=100)

        self.setted_stoploss_value.place(x=0, y=150)
        self.extreme_price_value.place(x=0, y=175)
        self.setted_trailing_value.place(x=0, y=200)

        self.unrealized_pnl_value.place(x=0, y=225)
        self.fee_to_pay_value.place(x=0, y=250)
        self.net_unrealized_pnl_value.place(x=0, y=275)

        self.pnl_after_reaching_ts_value.place(x=0, y=325)

        self.position_live_start_time_value.place(x=0, y=365)

        # ------------------------------------------- Last Trade --------------------------------------------
        self.last_trade_side_value.place(x=0, y=0)
        self.last_trade_entry_price_value.place(x=0, y=25)
        self.last_trade_close_price_value.place(x=0, y=50)
        self.last_trade_quantity_value.place(x=0, y=75)
        self.last_trade_fee_value.place(x=0, y=100)
        self.last_trade_pnl_value.place(x=0, y=125)
        self.last_trade_pnl_fee_value.place(x=0, y=165)

        # -------------------------------------------  New Order --------------------------------------------
        self.new_long_order_entry.place(x=0, y=0)
        self.new_long_order_value.place(x=0, y=30)
        self.new_short_order_entry.place(x=0, y=60)
        self.new_short_order_value.place(x=0, y=90)

    def labels_refresh(self):
        """refreshing data on all labels in GUI"""
        # updating texts which will be displayed:
        self.labels_text()
        self.safety_check()

        # showing up new values on screen:
        self.leverage_value.config(text=self.leverage_text)
        self.trailing_stop_value.config(text=self.trailing_stop_text)
        self.stop_loss_value.config(text=self.stop_loss_text)
        self.next_pos_step_value.config(text=self.next_pos_step_text)
        self.max_drawdawn_value.config(text=self.max_drawdawn_text)
        self.max_daily_loss_value.config(text=self.max_daily_loss_text)
        self.max_daily_loss_count_value.config(text=self.max_daily_loss_count_text)
        self.balance_usdt_value.config(text=self.balance_usdt_text)
        self.actual_drawdawn_value.config(text=self.actual_drawdawn_text)
        self.actual_daily_loss_value.config(text=self.actual_daily_loss_text)
        self.actual_daily_loss_count_value.config(text=self.actual_daily_loss_count_text)
        self.percent_to_risk_value.config(text=self.percent_to_risk_text)
        self.build_up_count_value.config(text=self.build_up_count_text)
        self.dollar_to_risk_value.config(text=self.dollar_to_risk_text)
        self.quantity_one_trade_value.config(text=self.quantity_one_trade_text)
        self.actual_ticker_value.config(text=self.actual_ticker_text)

        # ----------------------------------------- Actual Trade ----------------------------------------------
        self.is_position_live_value.config(text=self.is_position_live_text)
        self.position_live_entry_value.config(text=self.position_live_entry_text)
        self.position_live_amount_value.config(text=self.position_live_amount_text)
        self.position_live_start_time_value.config(text=self.position_live_start_time_text)
        self.position_filled_amount_value.config(text=self.position_filled_amount_text)
        self.actual_leverage_value.config(text=self.actual_leverage_text)
        self.stop_loss_prices_value.config(text=self.stop_loss_prices_text)
        self.setted_stoploss_value.config(text=self.setted_stoploss_text)
        self.extreme_price_value.config(text=self.extreme_price_text)
        self.setted_trailing_value.config(text=self.setted_trailing_text)
        self.unrealized_pnl_value.config(text=self.unrealized_pnl_text)
        self.pnl_after_reaching_ts_value.config(text=self.pnl_after_reaching_ts_text)
        self.fee_to_pay_value.config(text=self.fee_to_pay_text)
        self.net_unrealized_pnl_value.config(text=self.net_unrealized_pnl_text)

        # ------------------------------------------- Last Trade --------------------------------------------
        self.last_trade_side_value.config(text=self.last_trade_side_text)
        self.last_trade_entry_price_value.config(text=self.last_trade_entry_price_text)
        self.last_trade_close_price_value.config(text=self.last_trade_close_price_text)
        self.last_trade_quantity_value.config(text=self.last_trade_quantity_text)
        self.last_trade_fee_value.config(text=self.last_trade_fee_text)
        self.last_trade_pnl_value.config(text=self.last_trade_pnl_text)
        self.last_trade_pnl_fee_value.config(text=self.last_trade_pnl_fee_text)

        # -------------------------------------------  New Order --------------------------------------------
        self.new_long_order_value.config(text=self.new_long_order_text)
        self.new_short_order_value.config(text=self.new_short_order_text)

        # saving data in file:
        self.save_all()

    def buttons(self):
        # ------------------------------------ Buttons: --------------------------------------------------
        # ------------------------------------ Control Panel: --------------------------------------------------
        #   AUTO TRADE SWITCH:
        self.button_auto_trade = Button(self.control_panel, text="Auto Trade", height=2 * self.height, width=3 * self.width,
                                        activebackground="green", bg="grey", command=self.auto_trade_switch)
        #   LONG START:
        self.button_long_start = Button(self.control_panel, text="LONG", height=2 * self.height, width=4 * self.width,
                                        bd=5, bg="green", command=lambda: self.position_start("BUY", self.autotrade))
        #   SHORT START:
        self.button_short_start = Button(self.control_panel, text="SHORT", height=2 * self.height, width=4 * self.width,
                                         bd=5, bg="red", command=lambda: self.position_start("SELL", self.autotrade))
        #   EMERGENCY STOP:
        self.button_emergency_stop = Button(self.control_panel, text="EMERGENCY STOP", height=2 * self.height,
                                            width=8 * self.width,
                                            bd=5, bg="red", command=self.emergency_stop)
        #   Recent trades start:
        self.button_recent_trades_stream = Button(self.control_panel, text="Recent\nTrades", height=2 * self.height,
                                                  width=3 * self.width, bd=5,
                                                  command=lambda: threading.Thread(daemon=True,
                                                                           target=self.recent_trades_stream).start())
        #   LOAD Pair Parameters:
        self.button_load_parameters = Button(self.control_panel, text="LOAD", height=self.height, width=2 * self.width,
                                             command=self.loading_config_file)
        #   Refresh Button:
        self.button_refresh_params = Button(self.control_panel, text="REFRESH", height=2 * self.height, width=3 * self.width,
                                            command=lambda: threading.Thread(target=self.refresh_data).start())
        self.button_market_trade = Button(self.control_panel, text="Market Trade", height=2 * self.height,
                                          width=3 * self.width, activebackground="green", bg="grey",
                                          command=lambda: self.market_order_type("market"))
        self.button_order_trade = Button(self.control_panel, text="Order Trade", height=2 * self.height,
                                         width=3 * self.width, activebackground="green", bg="grey",
                                         command=lambda: self.market_order_type("limit"))

        # ------------------------------------ Setting Parameters: --------------------------------------------------
        #   Leverage:
        self.button_leverage_accept = Button(self.setting_parameters, text="SET", height=self.height, width=2 * self.width,
                                             command=lambda: self.leverage_set("set"))
        self.button_leverage_plus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                           command=lambda: self.leverage_set("minus"))
        self.button_leverage_minus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                            command=lambda: self.leverage_set("plus"))
        #   Trailing Stop:
        self.button_trailing_plus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                           command=lambda: self.trailing_stop_set("minus"))
        self.button_trailing_minus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                            command=lambda: self.trailing_stop_set("plus"))
        #   Stop Loss:
        self.button_stop_loss_plus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                            command=lambda: self.stop_loss_set("minus"))
        self.button_stop_loss_minus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                             command=lambda: self.stop_loss_set("plus"))
        #   Next Pos Step:
        self.button_next_pos_step_plus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                               command=lambda: self.next_pos_step_set("minus"))
        self.button_next_pos_step_minus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                                command=lambda: self.next_pos_step_set("plus"))
        #   Max Drawdawn:
        self.max_drawdawn_plus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                        command=lambda: self.max_drawdawn_set("plus"))
        self.max_drawdawn_minus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                         command=lambda: self.max_drawdawn_set("minus"))
        #   Max Daily Loss:
        self.max_daily_loss_plus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                          command=lambda: self.max_daily_loss_set("plus"))
        self.max_daily_loss_minus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                           command=lambda: self.max_daily_loss_set("minus"))
        #   Max Daily Loss Transactions:
        self.max_daily_loss_count_plus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                                command=lambda: self.max_daily_loss_count_set("minus"))
        self.max_daily_loss_count_minus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                                 command=lambda: self.max_daily_loss_count_set("plus"))
        #   Percent to risk:
        self.percent_to_risk_plus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                           command=lambda: self.percent_to_risk_set("minus"))
        self.percent_to_risk_minus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                            command=lambda: self.percent_to_risk_set("plus"))
        #   Transaction count to build up position:
        self.one_trade_quantity_plus = Button(self.setting_parameters, text="-", height=self.height, width=self.width,
                                              command=lambda: self.one_trade_quantity_set("minus"))
        self.one_trade_quantity_minus = Button(self.setting_parameters, text="+", height=self.height, width=self.width,
                                               command=lambda: self.one_trade_quantity_set("plus"))

        self.drawdawn_stoploss_25 = Button(self.setting_parameters, text="SLK 25", height=1, width=5, bg="grey",
                                           activebackground="grey", command=lambda: self.max_drawdawn_set("slk"))
        self.drawdawn_stoploss_50 = Button(self.setting_parameters, text="SLK 50", height=1, width=5, bg="grey",
                                           activebackground="grey",
                                           command=lambda: self.max_drawdawn_set("slk", slk_set=-50))

        # -------------------------------------------  New Order --------------------------------------------
        self.new_long_order_load = Button(self.new_order_frame, text="LOAD", height=1, width=5,
                                          command=lambda: self.load_new_order("long"))
        self.new_short_order_load = Button(self.new_order_frame, text="LOAD", height=1, width=5,
                                           command=lambda: self.load_new_order("short"))

        # ------------------------------------ Buttons Position: ------------------------------------------
        # ------------------------------------ Control Panel: --------------------------------------------------
        #   AUTO TRADE SWITCH:
        self.button_auto_trade.place(x=self.DIM_X["auto_trade_pos_x"],
                                     y=self.DIM_Y["auto_trade_pos_y"])
        #   LONG START:
        self.button_long_start.place(x=self.DIM_X["long_pos_x"],
                                     y=self.DIM_Y["long_pos_y"])
        #   SHORT START:
        self.button_short_start.place(x=self.DIM_X["long_pos_x"] + 120,
                                      y=self.DIM_Y["long_pos_y"])
        #   EMERGENCY STOP:
        self.button_emergency_stop.place(x=self.DIM_X["long_pos_x"] + 15,
                                         y=self.DIM_Y["long_pos_y"] + 60)
        #   RECENT TRADES:
        self.button_recent_trades_stream.place(x=self.DIM_X["long_pos_x"] + 10,
                                               y=self.DIM_Y["long_pos_y"] + 120)
        #   LOAD Parameters:
        self.button_load_parameters.place(x=self.DIM_X["drop_pos_x"] + 130,
                                          y=self.DIM_Y["drop_pos_y"] + 2)
        #   Refresh Button:
        self.button_refresh_params.place(x=self.DIM_X["long_pos_x"] + 130,
                                         y=self.DIM_Y["long_pos_y"] + 123)

        self.button_market_trade.place(x=self.DIM_X["auto_trade_pos_x"] + 80,
                                       y=self.DIM_Y["auto_trade_pos_y"])
        self.button_order_trade.place(x=self.DIM_X["auto_trade_pos_x"] + 160,
                                      y=self.DIM_Y["auto_trade_pos_y"])

        # ------------------------------------ Setting Parameters: --------------------------------------------------
        #   Leverage:
        self.button_leverage_accept.place(x=self.DIM_X["plus_minus_set_2_x"] - 20 * self.width,
                                          y=self.DIM_Y["lever_pos_y"])
        self.button_leverage_plus.place(x=self.DIM_X["plus_minus_set_2_x"],
                                        y=self.DIM_Y["lever_pos_y"])
        self.button_leverage_minus.place(x=self.DIM_X["plus_minus_set_2_x"] + 11 * self.width,
                                         y=self.DIM_Y["lever_pos_y"])
        #   Trailing Stop:
        self.button_trailing_plus.place(x=self.DIM_X["plus_minus_set_x"],
                                        y=self.DIM_Y["trailing_pos_y"])
        self.button_trailing_minus.place(x=self.DIM_X["plus_minus_set_x"] + 11 * self.width,
                                         y=self.DIM_Y["trailing_pos_y"])
        #   Stop Loss:
        self.button_stop_loss_plus.place(x=self.DIM_X["plus_minus_set_2_x"],
                                         y=self.DIM_Y["stop_loss_pos_y"])
        self.button_stop_loss_minus.place(x=self.DIM_X["plus_minus_set_2_x"] + 11 * self.width,
                                          y=self.DIM_Y["stop_loss_pos_y"])
        #   Next Pos Step:
        self.button_next_pos_step_plus.place(x=self.DIM_X["plus_minus_set_2_x"],
                                             y=self.DIM_Y["next_pos_step_pos_y"])
        self.button_next_pos_step_minus.place(x=self.DIM_X["plus_minus_set_2_x"] + 11 * self.width,
                                              y=self.DIM_Y["next_pos_step_pos_y"])
        #   Max Drawdawn:
        self.max_drawdawn_plus.place(x=self.DIM_X["plus_minus_set_x"],
                                     y=self.DIM_Y["max_drawdawn_pos_y"])
        self.max_drawdawn_minus.place(x=self.DIM_X["plus_minus_set_x"] + 11 * self.width,
                                      y=self.DIM_Y["max_drawdawn_pos_y"])

        self.drawdawn_stoploss_25.place(x=self.DIM_X["max_drawdawn_pos_x"] + 5,
                                        y=self.DIM_Y["max_drawdawn_pos_y"] + 24)
        self.drawdawn_stoploss_50.place(x=self.DIM_X["max_drawdawn_pos_x"] + 80,
                                        y=self.DIM_Y["max_drawdawn_pos_y"] + 24)
        #   Max Daily Loss:
        self.max_daily_loss_plus.place(x=self.DIM_X["plus_minus_set_x"],
                                       y=self.DIM_Y["max_daily_loss_pos_y"])
        self.max_daily_loss_minus.place(x=self.DIM_X["plus_minus_set_x"] + 11 * self.width,
                                        y=self.DIM_Y["max_daily_loss_pos_y"])
        #   Max Daily Loss Transactions:
        self.max_daily_loss_count_plus.place(x=self.DIM_X["plus_minus_set_x"],
                                             y=self.DIM_Y["max_daily_loss_count_pos_y"])
        self.max_daily_loss_count_minus.place(x=self.DIM_X["plus_minus_set_x"] + 11 * self.width,
                                              y=self.DIM_Y["max_daily_loss_count_pos_y"])
        #   Percent to risk:
        self.percent_to_risk_plus.place(x=self.DIM_X["plus_minus_set_2_x"],
                                        y=self.DIM_Y["percent_risk_pos_y"])
        self.percent_to_risk_minus.place(x=self.DIM_X["plus_minus_set_2_x"] + 11 * self.width,
                                         y=self.DIM_Y["percent_risk_pos_y"])
        #   Transaction count to build up position:
        self.one_trade_quantity_plus.place(x=self.DIM_X["plus_minus_set_2_x"],
                                           y=self.DIM_Y["build_up_count_pos_y"])
        self.one_trade_quantity_minus.place(x=self.DIM_X["plus_minus_set_2_x"] + 11 * self.width,
                                            y=self.DIM_Y["build_up_count_pos_y"])

        # -------------------------------------------  New Order --------------------------------------------
        self.new_long_order_load.place(x=200, y=0)
        self.new_short_order_load.place(x=200, y=60)

    def frames(self):
        # -------------------- Frames Creation: -------------------
        self.setting_parameters = LabelFrame(self.master, bd=4, text=" Setting Parameters ", font=self.font,
                                             height=420, width=300)
        self.actual_status_frame = LabelFrame(self.master, bd=4, text=" Actual Status ", font=self.font,
                                              height=420 * self.height, width=90 * self.width)
        self.last_trade_status_frame = LabelFrame(self.master, bd=4, text=" Previous Trade ", font=self.font,
                                                  height=230 * self.height, width=90 * self.width)
        self.orderbook_frame = LabelFrame(self.master, bd=4, text=" Order Book ", font=self.font,
                                          height=self.orderbook_levels * 42, width=300)
        self.recent_trades_frame = LabelFrame(self.master, bd=4, text=" Recent Trades ", font=self.font,
                                              height=self.orderbook_levels * 42, width=500)
        self.control_panel = LabelFrame(self.master, bd=4, text=" Control Panel ", font=self.font,
                                        height=420, width=260)
        self.calculated_frame = LabelFrame(self.master, bd=4, text=" Calculated Parameters ", font=self.font,
                                           height=230, width=580)
        self.new_order_frame = LabelFrame(self.master, bd=4, text=" New Order ", font=self.font,
                                          height=230, width=580)

        # --------------------- Frames Positions -------------------
        self.setting_parameters.place(x=self.DIM_X["setting_params_pos_x"],
                                      y=self.DIM_Y["setting_params_pos_y"])
        self.actual_status_frame.place(x=self.DIM_X["actual_frame_pos_x"],
                                       y=self.DIM_Y["actual_frame_pos_y"])
        self.last_trade_status_frame.place(x=self.DIM_X["last_trade_frame_pos_x"],
                                           y=self.DIM_Y["last_trade_frame_pos_y"])
        self.orderbook_frame.place(x=self.DIM_X["order_book_pos_x"],
                                   y=self.DIM_Y["order_book_pos_y"])
        self.recent_trades_frame.place(x=self.DIM_X["recent_trades_pos_x"],
                                       y=self.DIM_Y["recent_trades_pos_y"])
        self.control_panel.place(x=self.DIM_X["control_panel_pos_x"],
                                 y=self.DIM_Y["control_panel_pos_y"])
        self.calculated_frame.place(x=self.DIM_X["result_frame_pos_x"],
                                    y=self.DIM_Y["result_frame_pos_y"])
        self.new_order_frame.place(x=self.DIM_X["last_trans_frame_pos_x"],
                                   y=self.DIM_Y["last_trans_frame_pos_y"])

    def loading_config_file(self):
        # pair is defined in dropped list selection and after LOAD Button click:
        self.PAIR = self.pair_selection.get()

        # Loading config file:
        try:
            config_file = f"{self.PAIR}_config_file.json"
            with open(config_file, "r") as dataread:
                output = json.load(dataread)
        except FileNotFoundError:
            self.save_all()

        try:
            self.LEVERAGE = output["leverage_set"]
            self.TRAILING_STOP = output["trailing_stop"]
            self.STOP_LOSS = output["stop_loss"]
            self.NEXT_POS_STEP = output["next_pos_step"]
            self.max_drawdawn_percent = output["max_drawdawn_percent"]
            self.MAX_DAILY_LOSS = output["max_daily_loss"]
            self.MAX_DAILY_LOSS_COUNT = output["max_daily_loss_count"]
            self.ACTUAL_DRAWDAWN = output["actual_drawdawn"]
            self.ACTUAL_DAILY_LOSS = output["actual_daily_loss"]
            self.ACTUAL_DAILY_LOSS_COUNT = output["actual_loss_count"]
            self.PERCENT_TO_RISK = output["percent_to_risk"]
            self.BUILD_UP_POSITION_COUNT = output["build_up_position_count"]
            self.EXTREME_PRICE = output["extreme_price"]
            self.FIRST_TRADE_ENTRY_PRICE = output["first_trade_entry_price"]
            self.LAST_TRADE_ENTRY_PRICE = output["last_trade_entry_price"]
            self.LAST_TRADE_SIDE = output["last_trade_side"]
            self.LAST_TRADE_PNL = output["last_trade_pnl"]
            self.LAST_TRADE_FEE = output["last_trade_fee"]
            self.LAST_TRADE_AVERAGE_CLOSE_PRICE = output["last_trade_close_price"]
            self.LAST_TRADE_QUANTITY = output["last_trade_quantity"]
            self.LAST_TRADE_CLOSE_TIME = output["last_trade_close_time"]
            self.init_balance_usdt = output["init_balance_usdt"]
            self.NEW_LONG_ORDER = output["new_long_order_price"]
            self.NEW_SHORT_ORDER = output["new_short_order_price"]

        except KeyError:
            print("Lack of one parameter - refresh GUI")
        except UnboundLocalError:
            print("Config file not found - creating new file with default parameters.")

        self.refresh_data()

    def refresh_data(self):
        self.balance_usdt_check()
        self.position_info_check()
        self.percent_to_risk_set()
        self.max_drawdawn_set("refresh")
        self.actual_drawdawn_save(close=False)

    def save_all(self):
        config_data = {
            "pair": self.PAIR,
            "leverage_set": self.LEVERAGE,
            "stop_loss": self.STOP_LOSS,
            "trailing_stop": self.TRAILING_STOP,
            "next_pos_step": self.NEXT_POS_STEP,
            "max_drawdawn_percent": self.max_drawdawn_percent,
            "max_daily_loss": self.MAX_DAILY_LOSS,
            "max_daily_loss_count": self.MAX_DAILY_LOSS_COUNT,
            "actual_drawdawn": self.ACTUAL_DRAWDAWN,
            "actual_daily_loss": self.ACTUAL_DAILY_LOSS,
            "actual_loss_count": self.ACTUAL_DAILY_LOSS_COUNT,
            "percent_to_risk": self.PERCENT_TO_RISK,
            "build_up_position_count": self.BUILD_UP_POSITION_COUNT,
            "extreme_price": self.EXTREME_PRICE,
            "first_trade_entry_price": self.FIRST_TRADE_ENTRY_PRICE,
            "last_trade_entry_price": self.LAST_TRADE_ENTRY_PRICE,
            "last_trade_side": self.LAST_TRADE_SIDE,
            "last_trade_fee": self.LAST_TRADE_FEE,
            "last_trade_pnl": self.LAST_TRADE_PNL,
            "last_trade_close_price": self.LAST_TRADE_AVERAGE_CLOSE_PRICE,
            "last_trade_quantity": self.LAST_TRADE_QUANTITY,
            "last_trade_close_time": self.LAST_TRADE_CLOSE_TIME,
            "init_balance_usdt": self.init_balance_usdt,
            "new_long_order_price": self.NEW_LONG_ORDER,
            "new_short_order_price": self.NEW_SHORT_ORDER,
        }

        with open(f"{self.PAIR}_config_file.json", "w") as fp:
            json.dump(config_data, fp, indent=4)

# ----------------------------------------- Setting data ------------------------------------------------

    def leverage_set(self, status: str = "None"):
        """leverage is count based on stop loss divided by safety factor"""

        if status.lower() == "set":
            # setting leverage, do not change to auto-change leverage - possible leverage change on pending position!
            try:
                response = client.futures_change_leverage(symbol=self.PAIR, leverage=self.LEVERAGE)
            except BinanceAPIException as e:
                print(f"Error Code: {e.status_code} ")
                print(e.message)

            else:
                self.LEVERAGE = int(response['leverage'])
                print(f"Leverage is changed to: {self.LEVERAGE}x on Binance server.")
                self.refresh_data()

        if status.lower() == "plus":
            if self.LEVERAGE < (1 / (self.STOP_LOSS / 100)):
                self.LEVERAGE += 1

        elif status.lower() == "minus":
            if self.LEVERAGE > 1:
                self.LEVERAGE -= 1

        self.one_trade_quantity_set()

    def trailing_stop_set(self, status: str):
        if status.lower() == "plus":
            if self.TRAILING_STOP < 100:
                self.TRAILING_STOP += 0.1

        elif status.lower() == "minus":
            if self.TRAILING_STOP > 0.1:
                self.TRAILING_STOP -= 0.1

        self.TRAILING_STOP = round(self.TRAILING_STOP, 1)
        self.next_pos_step_set(status="None")

    def stop_loss_set(self, status: str):
        if status.lower() == "plus":
            if self.STOP_LOSS < 100:
                self.STOP_LOSS += 0.1

        elif status.lower() == "minus":
            if self.STOP_LOSS > 0.1:
                self.STOP_LOSS -= 0.1

        self.STOP_LOSS = round(self.STOP_LOSS, 1)
        self.position_side_parameters()
        self.leverage_set()
        self.refresh_data()

    def next_pos_step_set(self, status: str):
        if status.lower() == "plus":
            if self.NEXT_POS_STEP < 100:
                self.NEXT_POS_STEP += 0.1

        elif status.lower() == "minus":
            if self.NEXT_POS_STEP > 0.1:
                self.NEXT_POS_STEP -= 0.1

        self.NEXT_POS_STEP = round(self.NEXT_POS_STEP, 1)
        self.position_side_parameters()
        self.labels_refresh()

    def load_new_order(self, status: str = "none"):
        if status.lower() == "long":
            try:
                float(self.new_long_order_entry.get())
            except:
                self.NEW_LONG_ORDER = 0
            else:
                self.NEW_LONG_ORDER = float(self.new_long_order_entry.get())
                self.limit_order_permission = True

        elif status.lower() == "short":
            try:
                float(self.new_short_order_entry.get())
            except:
                self.NEW_SHORT_ORDER = 0
            else:
                self.NEW_SHORT_ORDER = float(self.new_short_order_entry.get())
                self.limit_order_permission = True

        self.labels_refresh()

    def market_order_type(self, status: str = "none"):
        if status.lower() == "market":
            self.OPEN_POSITION_TYPE = "MARKET"
            self.button_market_trade.config(relief=SUNKEN, bg="green")
            self.button_order_trade.config(relief=RAISED, bg="grey")

        elif status.lower() == "limit":
            self.OPEN_POSITION_TYPE = "LIMIT"
            self.button_order_trade.config(relief=SUNKEN, bg="green")
            self.button_market_trade.config(relief=RAISED, bg="grey")

    def max_drawdawn_set(self, status: str, slk_set=-25):
        if status.lower() == "slk":
            self.max_drawdawn_percent = slk_set

        if status.lower() == "plus":
            if self.max_drawdawn_percent < -1:
                self.max_drawdawn_percent += 1

        elif status.lower() == "minus":
            if self.max_drawdawn_percent > -100:
                self.max_drawdawn_percent -= 1

        if self.max_drawdawn_percent == -25:
            self.drawdawn_stoploss_25.config(relief=SUNKEN, bg="green")
            self.drawdawn_stoploss_50.config(relief=RAISED, bg="grey")

        elif self.max_drawdawn_percent == -50:
            self.drawdawn_stoploss_25.config(relief=RAISED, bg="grey")
            self.drawdawn_stoploss_50.config(relief=SUNKEN, bg="green")

        else:
            self.drawdawn_stoploss_25.config(relief=RAISED, bg="grey")
            self.drawdawn_stoploss_50.config(relief=RAISED, bg="grey")

        self.MAX_DRAWDAWN = round(self.max_drawdawn_percent * self.init_balance_usdt / 100, 1)
        self.labels_refresh()

    def max_daily_loss_set(self, status: str):
        if status.lower() == "plus":
            if self.MAX_DAILY_LOSS < -1:
                self.MAX_DAILY_LOSS += 1

        elif status.lower() == "minus":
            self.MAX_DAILY_LOSS -= 1

        self.labels_refresh()

    def max_daily_loss_count_set(self, status: str):
        if status.lower() == "plus":
            # if self.max_daily_loss_count < 100:
            self.MAX_DAILY_LOSS_COUNT += 1

        elif status.lower() == "minus":
            if self.MAX_DAILY_LOSS_COUNT > 1:
                self.MAX_DAILY_LOSS_COUNT -= 1

        self.labels_refresh()

    def actual_drawdawn_save(self, close=False):
        if close:
            self.ACTUAL_DRAWDAWN += self.LAST_TRADE_NET_PNL
            self.ACTUAL_DRAWDAWN = round(self.ACTUAL_DRAWDAWN, 2)
        self.actual_daily_loss_save(close)

    def actual_daily_loss_save(self, close):
        now = int(round(time.time()*1000, 0))

        if now < self.LAST_TRADE_CLOSE_TIME + 24 * 60 * 60 * 1000:
            if close:
                self.ACTUAL_DAILY_LOSS += self.LAST_TRADE_NET_PNL
                self.ACTUAL_DAILY_LOSS = round(self.ACTUAL_DAILY_LOSS, 2)
        else:
            if close:
                self.ACTUAL_DAILY_LOSS = self.LAST_TRADE_NET_PNL
            else:
                self.ACTUAL_DAILY_LOSS = 0

        self.actual_daily_loss_count_save(close)

    def actual_daily_loss_count_save(self, close):
        now = int(round(time.time() * 1000, 0))
        if now < self.LAST_TRADE_CLOSE_TIME + 24 * 60 * 60 * 1000:
            if close:
                if self.LAST_TRADE_NET_PNL < 0:
                    self.ACTUAL_DAILY_LOSS_COUNT += 1
                elif self.LAST_TRADE_NET_PNL > 0:
                    self.ACTUAL_DAILY_LOSS_COUNT -= 1

        else:
            if close:
                if self.LAST_TRADE_NET_PNL < 0:
                    self.ACTUAL_DAILY_LOSS_COUNT = 1
                else:
                    self.ACTUAL_DAILY_LOSS_COUNT = -1

            else:
                self.ACTUAL_DAILY_LOSS_COUNT = 0

        self.labels_refresh()

    def percent_to_risk_set(self, status: str = "None"):
        if status.lower() == "plus":
            if self.PERCENT_TO_RISK < 100:
                self.PERCENT_TO_RISK += 1

        elif status.lower() == "minus":
            if self.PERCENT_TO_RISK > 1:
                self.PERCENT_TO_RISK -= 1

        self.DOLLAR_TO_RISK = round_number(self.balance_usdt * self.PERCENT_TO_RISK / 100, "down", 2)

        self.one_trade_quantity_set()

    def one_trade_quantity_set(self, status: str = "None"):
        self.quantity_calc()

        if status.lower() == "plus":
            if self.BUILD_UP_POSITION_COUNT < 100:
                self.BUILD_UP_POSITION_COUNT += 1

        elif status.lower() == "minus":
            if self.BUILD_UP_POSITION_COUNT > 1:
                self.BUILD_UP_POSITION_COUNT -= 1

        self.ONE_TRADE_QUANTITY = round_number(self.quantity / self.BUILD_UP_POSITION_COUNT, "down", 3)

        if self.ONE_TRADE_QUANTITY < self.minimum_quantity:
            self.one_trade_quantity_set("minus")

        self.FILLED_ORDERS = abs(int(round(self.TRADED_AMOUNT / self.ONE_TRADE_QUANTITY, 0)))

        self.labels_refresh()

    def quantity_calc(self):
        self.actual_price = float(self.actual_ask_price)

        self.quantity = round_number(((self.DOLLAR_TO_RISK * self.LEVERAGE) / self.actual_price),
                                     up_down="down", decimals=3)

        #  requirement: min 5$ of position VALUE on Binance
        self.minimum_quantity = round_number((5 / self.actual_price), up_down="up", decimals=3)

        if self.quantity < self.minimum_quantity:
            self.quantity = self.minimum_quantity

    def unrealized_pnl_check(self):
        try:
            if self.SIDE == "BUY":
                self.UNREALIZED_PNL = round_number((self.actual_price / self.ENTRY_PRICE - 1)
                                                   * self.ACTUAL_LEVERAGE * 100, "down", 1)
                self.NET_UNREALIZED_PNL_AMOUNT = round_number(((self.actual_price - self.ENTRY_PRICE)
                                                               * self.TRADED_AMOUNT + self.START_POSITIONS_FEE * 2),
                                                              "down", 5)
                self.TS_HIT_PNL = round_number((self.SETTED_TRAILING_PRICE / self.ENTRY_PRICE - 1)
                                               * self.ACTUAL_LEVERAGE * 100, "down", 1)

            elif self.SIDE == "SELL":
                self.UNREALIZED_PNL = round_number((1 - self.actual_price / self.ENTRY_PRICE)
                                                   * self.ACTUAL_LEVERAGE * 100, "down", 1)
                self.NET_UNREALIZED_PNL_AMOUNT = round_number(((self.ENTRY_PRICE - self.actual_price)
                                                               * self.TRADED_AMOUNT + self.START_POSITIONS_FEE * 2),
                                                              "down", 5)
                self.TS_HIT_PNL = round_number((1 - self.SETTED_TRAILING_PRICE / self.ENTRY_PRICE)
                                               * self.ACTUAL_LEVERAGE * 100, "down", 1)

            else:
                self.UNREALIZED_PNL = 0
                self.NET_UNREALIZED_PNL_AMOUNT = 0
                self.TS_HIT_PNL = 0

        except ZeroDivisionError:
            self.UNREALIZED_PNL = 0
            self.NET_UNREALIZED_PNL_AMOUNT = 0
            self.TS_HIT_PNL = 0

    def auto_trade_switch(self):
        if self.autotrade:
            self.button_auto_trade.config(relief=RAISED, bg="grey")
            self.autotrade = False
        else:
            self.button_auto_trade.config(relief=SUNKEN, bg="green")
            self.autotrade = True
            if self.IS_POSITION_LIVE != "inactive":
                self.position_start(self.SIDE, self.autotrade)

# ----------------------------------------Position starting functions------------------------------------
# ------------------------------------------SPRAWDZIĆ!!!!!!!!!!!!!!!!-----------------------------------

    def position_start(self, side, auto_trade=False):
        self.SIDE = side.upper()
        self.position_side_parameters()
        self.position_info_check()
        if auto_trade:
            autotrade_thread = threading.Thread(daemon=True, target=self.auto_trading).start()
        else:
            self.open_position()
            print("Manual trade started.")

    def position_side_parameters(self):
        if self.SIDE == "BUY":
            self.stop_loss = 1 - self.STOP_LOSS / 100
            self.trail_stop_requirement = 1 + self.STOP_LOSS / 100
            self.trailing_stop = 1 - self.TRAILING_STOP / 100
            self.LIMIT_ORDER_PRICE = self.NEW_LONG_ORDER

            # variables used to compare values in trailing stop and stop loss loop
            self.stop_loss_comp = '<='
            self.actual_extreme_comp = '>'
            self.extreme_activate_comp = '>='
            self.actual_trailing_comp = '<='

        elif self.SIDE == "SELL":
            self.stop_loss = 1 + self.STOP_LOSS / 100
            self.trail_stop_requirement = 1 - self.STOP_LOSS / 100
            self.trailing_stop = 1 + self.TRAILING_STOP / 100
            self.LIMIT_ORDER_PRICE = self.NEW_SHORT_ORDER

            # variables used to compare values in trailing stop and stop loss loop
            self.stop_loss_comp = '>='
            self.actual_extreme_comp = '<'
            self.extreme_activate_comp = '<='
            self.actual_trailing_comp = '>='

    def open_position(self):

        if self.trade_permission:
            if self.OPEN_POSITION_TYPE.upper() == "MARKET":
                try:
                    open_pos = client.futures_create_order(symbol=self.PAIR,
                                                           side=self.SIDE,
                                                           type=self.OPEN_POSITION_TYPE,
                                                           quantity=self.ONE_TRADE_QUANTITY)
                except BinanceAPIException as e:
                    print(e.message)
                    print(e.status_code)
                else:
                    print(f"---------- {self.SIDE} MARKET TYPE POSITION SUCCESSFULLY OPENED ----------")

            elif self.OPEN_POSITION_TYPE.upper() == "LIMIT":
                if self.limit_order_permission:
                    try:
                        open_pos = client.futures_create_order(symbol=self.PAIR,
                                                               side=self.SIDE,
                                                               type=self.OPEN_POSITION_TYPE,
                                                               price=self.LIMIT_ORDER_PRICE,
                                                               quantity=self.ONE_TRADE_QUANTITY,
                                                               timeInForce="GTC")
                    except BinanceAPIException as e:
                        print(e.message)
                        print(e.status_code)
                    else:
                        print(f"---------- {self.SIDE} LIMIT TYPE POSITION SUCCESSFULLY SETTED AT {self.LIMIT_ORDER_PRICE} ----------")
                else:
                    print("Limit order not permitted - check limit prices.")
        else:
            print("Position not opened - permission to open position not granted")

        time.sleep(0.01)
        self.refresh_data()
        self.labels_refresh()

    def close_position(self):
        if self.SIDE == "BUY":
            side = "SELL"
        elif self.SIDE == "SELL":
            side = "BUY"
        else:
            side = "NONE"

        try:
            self.CLOSED_POSITION_INFO = client.futures_create_order(symbol=self.PAIR,
                                                                    side=side,
                                                                    type=self.CLOSE_POSITION_TYPE,
                                                                    quantity=self.TRADED_AMOUNT,
                                                                    reduceOnly='true')
        except BinanceAPIException as e:
            if e.message == "ReduceOnly Order is rejected.":
                print("You have not any open position!")

            elif e.message == "Invalid side.":
                print("You have not chosen side to close position - probably you have not opened position!")

        else:
            print("------------ POSITION SUCCESSFULLY CLOSED -------------")
            self.IS_POSITION_LIVE = "inactive"

        time.sleep(0.01)
        self.last_transaction_info_check()
        self.actual_drawdawn_save(close=True)

    def emergency_stop(self):
        print("------------- EMERGENCY SWITCH ACTIVATED --------------")
        self.close_position()
        self.auto_trade_switch()

# ------------------------------------------- Checking data --------------------------------------------

    def safety_check(self):
        # block to check is every safety requirements are passed.
        # if not: position starting buttons have to be inactive.
        if self.ACTUAL_DRAWDAWN <= self.MAX_DRAWDAWN \
                or self.ACTUAL_DAILY_LOSS <= self.MAX_DAILY_LOSS \
                or self.ACTUAL_DAILY_LOSS_COUNT >= self.MAX_DAILY_LOSS_COUNT:

            self.trade_permission = False
            self.button_long_start["state"] = DISABLED
            self.button_short_start["state"] = DISABLED

        else:
            self.trade_permission = True
            self.button_long_start["state"] = NORMAL
            self.button_short_start["state"] = NORMAL

            if self.FILLED_ORDERS >= self.BUILD_UP_POSITION_COUNT:
                if self.IS_POSITION_LIVE == "LONG":
                    self.button_long_start["state"] = DISABLED

                elif self.IS_POSITION_LIVE == "SHORT":
                    self.button_short_start["state"] = DISABLED

            else:
                self.button_long_start["state"] = NORMAL
                self.button_short_start["state"] = NORMAL

    def balance_usdt_check(self):
        whole_balance = client.futures_account_balance()
        self.balance_usdt = round_number(float(whole_balance[6]['balance']), up_down="down", decimals=2)

    def position_info_check(self):
        self.position_info = client.futures_position_information(symbol=self.PAIR)
        self.ACTUAL_LEVERAGE = int(self.position_info[0]['leverage'])
        self.TRADED_AMOUNT = float(self.position_info[0]['positionAmt'])
        self.ENTRY_PRICE = round(float(self.position_info[0]['entryPrice']), 2)
        self.position_start_timestamp = int(self.position_info[0]['updateTime'])
        self.POSITION_START_UPDATE_TIME = datetime.utcfromtimestamp(self.position_start_timestamp / 1000 + 3600) \
            .strftime('%d-%m-%Y  %H:%M:%S')

        if self.first_trade:
            self.FIRST_TRADE_ENTRY_PRICE = self.ENTRY_PRICE
            # print(f"First Trade entry price:  {self.FIRST_TRADE_ENTRY_PRICE}$")

        if self.TRADED_AMOUNT == 0:
            self.IS_POSITION_LIVE = "inactive"
            self.EXTREME_PRICE = 0
            if self.OPEN_POSITION_TYPE == "LIMIT":
                self.EXTREME_PRICE = self.LIMIT_ORDER_PRICE

        elif self.TRADED_AMOUNT > 0:
            self.IS_POSITION_LIVE = "LONG"
            self.SIDE = "BUY"

        elif self.TRADED_AMOUNT < 0:
            self.IS_POSITION_LIVE = "SHORT"
            self.SIDE = "SELL"
            self.TRADED_AMOUNT *= -1

        self.unrealized_pnl_check()
        self.position_side_parameters()
        self.SETTED_STOPLOSS_PRICE = round_number(self.ENTRY_PRICE * self.stop_loss, "up", 2)

        if self.OPEN_POSITION_TYPE == "MARKET":
            self.START_POSITIONS_FEE = round_number(self.ENTRY_PRICE * self.TRADED_AMOUNT * -0.0004, "up", 5)
        else:
            self.START_POSITIONS_FEE = round_number(self.ENTRY_PRICE * self.TRADED_AMOUNT * -0.0002, "up", 5)

    def start_checking_sl_tp(self):
        # start_time = time.time()
        while True:
            # checking actual price:
            if self.SIDE == "BUY":
                self.actual_price = float(self.actual_bid_price)
            else:
                self.actual_price = float(self.actual_ask_price)

            # checking SL and TP:
            if self.IS_POSITION_LIVE != "inactive":
                self.stop_loss_check()
                if self.IS_POSITION_LIVE != "inactive":
                    self.trailing_stop_check()

            self.unrealized_pnl_check()

            # showing everything on screen:
            self.labels_text()
            self.actual_ticker_value.config(text=self.actual_ticker_text)
            self.extreme_price_value.config(text=self.extreme_price_text)
            self.setted_trailing_value.config(text=self.setted_trailing_text)
            self.unrealized_pnl_value.config(text=self.unrealized_pnl_text)
            self.net_unrealized_pnl_value.config(text=self.net_unrealized_pnl_text)
            self.pnl_after_reaching_ts_value.config(text=self.pnl_after_reaching_ts_text)
            time.sleep(0.01)
            # print(f"czas sprawdzenia: {time.time() - start_time}")

    def stop_loss_check(self):

        if eval(str(self.actual_price) + self.stop_loss_comp + str(self.SETTED_STOPLOSS_PRICE)):
            self.close_position()
            self.auto_trade_switch()
            print(f"Position {self.SIDE} closed because of Stop Loss hit at {self.LAST_TRADE_AVERAGE_CLOSE_PRICE}!")
            print(f"Net PNL report: {self.LAST_TRADE_NET_PNL}")

    def trailing_stop_check(self):
        extreme_price = self.EXTREME_PRICE

        if eval(str(self.actual_price) + self.actual_extreme_comp + str(self.EXTREME_PRICE)):
            self.EXTREME_PRICE = float(self.actual_price)

        # if eval(str(self.EXTREME_PRICE) + self.extreme_activate_comp
        #         + str(self.FIRST_TRADE_ENTRY_PRICE * self.trail_stop_requirement)):

        self.SETTED_TRAILING_PRICE = round(self.EXTREME_PRICE * self.trailing_stop, 2)

        if extreme_price != self.EXTREME_PRICE:
            print(f"Extreme Price: {self.EXTREME_PRICE}, "
                  f"Trailing Price: {self.SETTED_TRAILING_PRICE}, "
                  f"First Trade Price: {self.FIRST_TRADE_ENTRY_PRICE}, "
                  f"Last Trade Price: {self.last_trade_price}, "
                  f"Mean Entry Price: {self.ENTRY_PRICE}.")

        if eval(str(self.actual_price) + self.actual_trailing_comp + str(self.SETTED_TRAILING_PRICE)):
            self.close_position()
            self.auto_trade_switch()
            print(f"Position {self.SIDE} closed because of Trailing Stop hit "
                  f"at {self.LAST_TRADE_AVERAGE_CLOSE_PRICE} $")
            print(f"Net PNL report: {self.LAST_TRADE_NET_PNL}")

    def last_trade_check(self):
        limit = 1
        trades_history = client.futures_account_trades(symbol=self.PAIR, limit=limit)
        self.last_trade_price = float(trades_history[0]['price'])

    def last_transaction_info_check(self):
        self.LAST_TRADE_ENTRY_PRICE = self.ENTRY_PRICE
        self.LAST_TRADE_SIDE = self.SIDE
        try:
            self.LAST_TRADE_CLOSE_TIME = self.CLOSED_POSITION_INFO["updateTime"]
        except AttributeError:
            print("There is no position to close!")
        else:
            limit = 10
            trades_history = client.futures_account_trades(symbol=self.PAIR, limit=limit)

            p = price = quantity = commission = average_price = realized_pnl = 0

            limit = len(trades_history)

            for i in range(0, limit, 1):
                if trades_history[i]['time'] == self.LAST_TRADE_CLOSE_TIME:
                    p += 1
                    commission += float(trades_history[i]['commission'])
                    quantity += float(trades_history[i]['qty'])
                    price += float(trades_history[i]['price'])
                    realized_pnl += float(trades_history[i]['realizedPnl'])
                    average_price = float(price / p)

            self.last_trade_price = float(trades_history[limit - 1]['price'])
            self.LAST_TRADE_QUANTITY = round(quantity, 3)
            self.LAST_TRADE_AVERAGE_CLOSE_PRICE = round(average_price, 2)
            self.LAST_TRADE_FEE = round(- commission + self.START_POSITIONS_FEE, 5)
            self.LAST_TRADE_PNL = round(realized_pnl, 5)
            self.LAST_TRADE_NET_PNL = round(self.LAST_TRADE_PNL + self.LAST_TRADE_FEE, 5)

        self.refresh_data()

# ------------------------------------------------ Datastreams ------------------------------------------------
    def recent_trades_stream(self):
        self.recent_trades_sell_text = ""
        self.recent_trades_buy_text = ""
        socket = f"wss://fstream.binance.com/ws/{self.PAIR.lower()}@aggTrade"

        ws = websocket.WebSocketApp(socket, on_message=self.recent_trades_message, on_close=self.recent_trades_close)

        ws.run_forever(ping_interval=20)

    def recent_trades_message(self, ws, message):
        data = json.loads(message)

        is_sell = bool(data['m'])
        price = float(data['p'])
        quantity = float(data['q'])
        actual_time = int(data['T'])

        trade = [actual_time, price, quantity, is_sell]

        with open("recent_trades_v2.1.csv", 'a+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(trade)

        """    
        if quantity >= 1:
            if is_sell:
                sell_text = f"{price}\t{quantity}\t{actual_time}\n"
                buy_text = "\n"
            else:
                buy_text = f"{price}\t{quantity}\t{actual_time}\n"
                sell_text = "\n"

            self.recent_trades_sell_text = sell_text + self.recent_trades_sell_text
            self.recent_trades_buy_text = buy_text + self.recent_trades_buy_text

        self.recent_trades_label_buy.config(text=self.recent_trades_buy_text)
        self.recent_trades_label_sell.config(text=self.recent_trades_sell_text)
        """

    def recent_trades_close(self, ws):
        print("### RECENT TRADES CONNECTION TERMINATED ###")
        time.sleep(30)
        threading.Thread(daemon=True, target=self.recent_trades_stream).start()

    def order_book_datastream(self):

        depth_socket = f"wss://fstream.binance.com/ws/{self.PAIR.lower()}@depth{self.orderbook_levels}@100ms"

        ws = websocket.WebSocketApp(depth_socket, on_message=self.orderbook_message, on_close=self.orderbook_close)

        ws.run_forever(ping_interval=20)

    def orderbook_message(self, ws, message):
        data = json.loads(message)
        asks = data["a"]
        bids = data["b"]

        self.actual_bid_price = bids[0][0]

        self.actual_bid_amount = bids[0][1]

        self.actual_ask_price = asks[0][0]

        self.actual_ask_amount = asks[0][1]

        ask_orders = "Ask:\n"
        bid_orders = "Bid:\n"
        ask_sum = bid_sum = 0

        for i in range(0, len(bids), 1):
            bid_amount = round(float(bids[i][1]), 0)
            bid_sum += bid_amount
            bid_price = float(bids[i][0])
            first_price = float(bids[0][0])
            percent_slippage = round(((bid_price - first_price)/first_price) * 100, 2)
            bid_orders += f"{bid_price}\t{bid_amount}\t{bid_sum}\t{percent_slippage}%\n"

        for i in range(0, len(asks), 1):
            ask_amount = round(float(asks[i][1]), 0)
            ask_sum += ask_amount
            ask_price = float(asks[i][0])
            first_price = float(asks[0][0])
            percent_slippage = round(-((ask_price - first_price) / first_price) * 100, 2)
            ask_orders = f"{ask_price}\t{ask_amount}\t{ask_sum}\t{percent_slippage}%\n" + ask_orders

        self.actual_ask_price_value.config(text=ask_orders)
        self.actual_bid_price_value.config(text=bid_orders)

    def orderbook_close(self, ws):
        print("### ORDERBOOK DATA STREAM CONNECTION TERMINATED ###")
        time.sleep(30)
        threading.Thread(daemon=True, target=self.order_book_datastream).start()

# ------------------------------------------------ Auto Trading ------------------------------------------------
    def auto_trading(self):
        if self.IS_POSITION_LIVE == "inactive":
            if self.OPEN_POSITION_TYPE == "LIMIT":
                self.EXTREME_PRICE = self.LIMIT_ORDER_PRICE
                self.limit_reached = False
            elif self.OPEN_POSITION_TYPE == "MARKET":
                self.EXTREME_PRICE = self.actual_price

            self.first_trade = True
            self.open_position()

            while self.OPEN_POSITION_TYPE == "LIMIT":
                if self.limit_reached:
                    self.refresh_data()
                    self.labels_refresh()
                    if self.TRADED_AMOUNT != 0:
                        break

                if self.SIDE == "BUY":
                    if self.actual_price < self.LIMIT_ORDER_PRICE:
                        print("Limit price reached, Long transaction started.")
                        self.limit_reached = True

                elif self.SIDE == "SELL":
                    if self.actual_price > self.LIMIT_ORDER_PRICE:
                        print("Limit price reached, Short transaction started.")
                        self.limit_reached = True

                time.sleep(0.02)

            self.market_order_type(status="market")
            self.first_trade = False

        self.last_trade_check()

        self.FIRST_TRADE_ENTRY_PRICE = self.last_trade_price
        print(f"Auto Trading {self.SIDE} started at {self.last_trade_price}$.")

        next_trade_price = 0

        if self.SIDE == "BUY":
            next_trade_price = self.last_trade_price * (1 + self.NEXT_POS_STEP / 100)
        elif self.SIDE == "SELL":
            next_trade_price = self.last_trade_price * (1 - self.NEXT_POS_STEP / 100)

        print(f"Next position will open after reaching at least {next_trade_price}")

        while self.IS_POSITION_LIVE != "inactive":
            if not self.autotrade:
                print("Autotrade Disabled")
                break

            if self.FILLED_ORDERS < self.BUILD_UP_POSITION_COUNT:

                if self.SIDE == "BUY":
                    next_trade_price = self.last_trade_price * (1 + self.NEXT_POS_STEP / 100)

                    if self.EXTREME_PRICE >= next_trade_price:
                        self.open_position()
                        self.last_trade_check()

                        print(f"Filled {self.FILLED_ORDERS} of {self.BUILD_UP_POSITION_COUNT} "
                              f"orders at {self.last_trade_price} $")

                        next_trade_price = self.last_trade_price * (1 + self.NEXT_POS_STEP / 100)
                        print(f"Next position will open after reaching at least {round(next_trade_price, 2)}")

                elif self.SIDE == "SELL":
                    next_trade_price = self.last_trade_price * (1 - self.NEXT_POS_STEP / 100)

                    if self.EXTREME_PRICE <= next_trade_price:
                        self.open_position()
                        self.last_trade_check()

                        print(f"Filled {self.FILLED_ORDERS} of {self.BUILD_UP_POSITION_COUNT} "
                              f"orders at {self.last_trade_price} $")

                        next_trade_price = self.last_trade_price * (1 - self.NEXT_POS_STEP / 100)
                        print(f"Next position will open after reaching at least {round(next_trade_price, 2)}")

                if self.FILLED_ORDERS == self.BUILD_UP_POSITION_COUNT:
                    break

            time.sleep(0.02)


def round_number(n, up_down: str, decimals=0):
    multiplier = 10 ** decimals
    if up_down.lower() == "up":
        rounded_number = math.ceil(n * multiplier) / multiplier
    elif up_down.lower() == "down":
        rounded_number = math.floor(n * multiplier) / multiplier
    else:
        rounded_number = "up_down side is wrong - check"
        print(rounded_number)
    return rounded_number


"""

NAPRAWIĆ: 

napisać testy do kodu - w celu ćwiczenia 


Przeprowadzić refactoring kodu (refreshingi layouty, __init__, nie przypisane do init selfy przerobić - sporo roboty)


zmienić sposób sprawdzania czy jest otwarte zlecenie oczekujące na skaning co x sekund.
dodać otwarte pozycje i możliwość ich zamknięcia!
dodać TS na podstawie najniższej ceny z zadanego okresu (x godzin)


 
DODAĆ:

init_balance_usdt <--- można połączyć to z przelewem kasy na konto futures


"""

root = Tk()
root.title("Crypto Bot")
root.geometry("1800x950")

my_gui = BotGUI(root)

root.mainloop()

