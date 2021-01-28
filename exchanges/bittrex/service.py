from os import environ
import logging
import math

from bittrex.bittrex import Bittrex, API_V1_1
from core.exceptions import (UserAdviceException, ValidationException)
from ..interface import ServiceInterface
from ..helpers import calculate_lcm

logger = logging.getLogger(__name__)


class BittrexService(ServiceInterface):
    name = 'bit'

    def __init__(self, **kwargs):
        api_key = kwargs["api_key"]
        api_secret = kwargs["api_secret"]

        if not all([api_key, api_secret]):
            raise Exception(
                f"Both api_key and api_secret are required for {name} exchange")

        self.client = Bittrex(api_key, api_secret, API_V1_1)
        self.debug_mode = environ.get("DEBUG", False)

    def get_account(self):
        return self.client.get_account()

    def buy(self, coin_name, quantity=None, pair_base="BTC", amount=None, order_type="market"):
        try:
            symbol = f"{pair_base}-{coin_name}"
            price = self.get_price(symbol)
            quantity = self.calculate_buy_qty(price, amount)

            logger.info(
                f"buy order request:{symbol}>price:{price}>quantity:{quantity} > order_type: {order_type}")

            if order_type.lower() == "market":
                order = self.client.buy_market(
                    market=symbol,
                    quantity=quantity)
            elif order_type.lower() == "market":
                order = self.client.buy_limit(
                    market=symbol,
                    quantity=quantity,
                    rate=price)

            logger.info(
                f"Bought order request:{symbol}>price:{price}>quantity:{quantity}> {order}")
            return order
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise UserAdviceException(ex)

    def sell(self, coin_name, quantity=None, pair_base="BTC", amount=None, order_type="market"):
        try:
            balance = self.get_balance(coin_name)
            if not balance:
                raise UserAdviceException(
                    f"Balance not enough to execute action in {name} exchange")

            symbol = f"{pair_base}-{coin_name}"
            price = self.get_price(symbol)
            quantity = self.calculate_sell_qty(price, amount)

            logger.info(
                f"sell order request:{symbol}>price:{price}>quantity:{quantity} > order_type: {order_type}")

            if order_type.lower() == "market":
                order = self.client.sell_market(
                    market=symbol,
                    quantity=quantity)
            elif order_type.lower() == "market":
                order = self.client.sell_limit(
                    market=symbol,
                    quantity=quantity,
                    rate=price)
            logger.info(
                f"Bought order request:{symbol}>price:{price}>quantity:{quantity}> {order}")
            return order
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise UserAdviceException(ex)

    def get_step_size(self, symbol):
        try:
            pass
        except Exception as ex:
            logger.error("Error retriving step size")
            return float(0.0)

    def get_price(self, symbol):
        try:
            price_info = self.client.get_ticker(market=symbol)
            logger.info(f"Price info: {price_info}")
            return float(price_info.get("price"))
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def calculate_sell_qty(self, price, amount, step_size=None):
        quantity = float(amount)/float(price)
        return float(quantity)

    def calculate_buy_qty(self, price, amount, step_size=None):
        quantity = float(amount)/float(price)
        return float(quantity)

    def get_balance(self, coin_name):
        pass
        try:
            balance_info = self.client.get_balance(coin_name)
            if not balance_info:
                raise UserAdviceException(
                    f"Coin not found in account in {self.name} exchange")
            if not balance_info.get("success"):
                raise Exception(balance_info.get("message"))
            result = balance_info.get("result")
            return float(result.get("Available"))
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def track_coin(self, payload):
        pass

    def get_prices(self):
        pass

    def get_symbol_info(self, coin_name, pair_base="BTC"):
        try:
            market = f"{pair_base}-{coin_name}"
            info = self.client.get_market_summary(market=market)
            logger.info(f"Symbol info: {info}")
            return info
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def get_open_orders(self, coin_name, pair_base="BTC"):
        try:
            market = f"{pair_base}-{coin_name}"
            orders = self.client.get_open_orders(market=market)
            logger.info(f"orders: {orders}")
            return orders
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def get_all_orders(self, coin_name, limit=5, pair_base="BTC"):
        try:
            market = f"{pair_base}-{coin_name}"
            orders = self.client.get_order_history(market=market, limit=limit)
            logger.debug(f"orders: {orders}")
            return orders
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)
