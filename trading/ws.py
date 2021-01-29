from binance.websockets import BinanceSocketManager
from binance.client import Client
import asyncio
from twisted.internet import reactor
import time

from exchanges.adapter import Exchange
import logging

logger = logging.getLogger(__name__)


class BinaceWebsocket:
    def __init__(self, api_key, api_secret):
        client = Client(api_key, api_secret)
        self.api_key = api_key
        self.api_secret = api_secret
        self.bm = BinanceSocketManager(client)
        self.conn_key = None
        self.purchased = False
        self.sold = False

    def get_trading_range(self):
        buy_range_min = self.buy_price - \
            (self.buy_price*self.allowable_percent)
        buy_range_max = self.buy_price + \
            (self.buy_price*self.allowable_percent)

        sell_range_min = self.sell_price - \
            (self.sell_price*self.allowable_percent)
        sell_range_max = self.sell_price + \
            (self.sell_price*self.allowable_percent)
        return (float(buy_range_min), float(buy_range_max), float(sell_range_min), float(sell_range_max))

    def process_results(self, msg):
        try:
            logger.info("message type: {}".format(msg['e']))
            logger.info(msg)

            ask_price = msg["a"]
            bid_price = msg["b"]
            buy_range_min, buy_range_max, sell_range_min, sell_range_max = self.get_trading_range()
            if not self.purchased and (buy_range_min <= float(ask_price) <= buy_range_max):
                exchange_obj = Exchange(name=self.exchange,
                                        api_key=self.api_key, api_secret=self.api_secret)
                order = exchange_obj.buy(
                    coin_name=self.coin_name, amount=buy_range_min, pair_base=self.base_coin, order_type="market")

                if order:
                    self.purchased = True
            if not self.sold and self.purchased and (sell_range_min <= float(bid_price) <= sell_range_max):

                exchange_obj = Exchange(name=self.exchange,
                                        api_key=self.api_key, api_secret=self.api_secret)
                order = exchange_obj.sell(
                    coin_name=self.coin_name, amount=buy_range_min, pair_base=self.base_coin, order_type="market")
                if order:
                    self.sold = True

            if self.purchased and self.sold:
                self.close()
        except Exception as ex:
            logger.error(ex, exc_info=True)
            logger.warn(
                f"Forced to close requests. Shutting down websocket")
            self.close()

    def close(self):
        time.sleep(3)
        logger.info(f"Closing connection key: {self.conn_key}")
        self.bm.stop_socket(self.conn_key)
        self.bm.close()
        logger.info("Close listener")

    async def listener(self, exchange, coin_name, base_coin, buy_price, sell_price, allowable_percent):
        logger.info(
            f"Running listener for coin_name: {coin_name}/{base_coin}")
        self.exchange = exchange
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.coin_name = coin_name
        self.base_coin = base_coin
        self.allowable_percent = allowable_percent
        self.symbol = f"{coin_name}{base_coin}"
        self.conn_key = self.bm.start_symbol_ticker_socket(
            self.symbol, self.process_results)

        self.bm.start()
        await asyncio.sleep(1)
