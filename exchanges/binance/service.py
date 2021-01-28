from os import environ
import logging
import math
from decimal import Decimal
from core.database import db_client

from binance.client import Client
from binance.exceptions import (
    BinanceRequestException, BinanceAPIException, BinanceWithdrawException)

from core.exceptions import (UserAdviceException, ValidationException)
from ..interface import ServiceInterface
from ..helpers import calculate_lcm

logger = logging.getLogger(__name__)


class BinanceService(ServiceInterface):
    name = 'bin'

    def __init__(self, **kwargs):
        api_key = kwargs["api_key"]
        api_secret = kwargs["api_secret"]

        if not all([api_key, api_secret]):
            raise Exception(
                f"Both api_key and api_secret are required for {name} exchange")

        self.client = Client(api_key, api_secret)
        self.debug_mode = environ.get("DEBUG", False)

    def get_account(self):
        return self.client.get_account()

    def buy(self, coin_name, quantity=None, pair_base="BTC", amount=None, order_type="market"):
        try:
            symbol = f"{coin_name}{pair_base}".upper()
            precision = self.get_precision(symbol)
            current_price = self.get_price(symbol, precision)
            step_size = self.get_step_size(symbol)

            quantity = self.calculate_buy_qty(
                price=current_price, amount=amount, step_size=step_size)

            logger.info(
                f"step_size>{step_size}>price>{current_price} > Amount > {amount} > precision: {precision} > qty: {quantity}")

            side = Client.SIDE_BUY
            time_in_force = None
            if order_type == "limit":
                order_type = Client.ORDER_TYPE_LIMIT
                time_in_force = "GTC"
            else:
                order_type = Client.ORDER_TYPE_MARKET

            if order_type == Client.ORDER_TYPE_LIMIT:
                logger.info(
                    f"{side} order request:{symbol}>type:{order_type}>quantity:{quantity} > {amount}")
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity,
                    timeInForce=time_in_force,
                    price=amount)
            else:
                logger.info(
                    f"{side} order request:{symbol}>type:{order_type}>quantity:{quantity} > {current_price}")
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity)
            return order
        except (BinanceAPIException, BinanceRequestException) as ex:
            logger.error(ex, exc_info=True)
            raise UserAdviceException(ex)

    def sell(self, coin_name, quantity=None, pair_base="BTC", amount=None, order_type="market"):
        try:
            balance = self.get_balance(coin_name)
            if not balance:
                raise UserAdviceException(
                    f"Balance not enough to execute action in {name} exchange")

            symbol = f"{coin_name}{pair_base}".upper()
            precision = self.get_precision(symbol)

            current_price = self.get_price(symbol, precision)
            step_size = self.get_step_size(symbol)
            quantity = self.calculate_sell_qty(
                price=current_price, amount=amount, step_size=step_size)

            side = Client.SIDE_SELL
            time_in_force = None
            if order_type == "limit":
                order_type = Client.ORDER_TYPE_LIMIT
                time_in_force = "GTC"
            else:
                order_type = Client.ORDER_TYPE_MARKET

            logger.info(
                f"{side} order request:{symbol}>type:{order_type}>quantity:{quantity} >> current_price: {current_price}")

            if order_type == Client.ORDER_TYPE_LIMIT:
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity,
                    timeInForce=time_in_force,
                    price=amount)
            else:
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity)
            return order
        except (BinanceAPIException, BinanceRequestException) as ex:
            logger.error(ex, exc_info=True)
            raise UserAdviceException(ex)

    def get_precision(self, symbol):
        try:
            step = db_client.stepsizes.find_one({"symbol": symbol})
            if step:
                return step["baseAssetPrecision"]
            return 8
        except Exception as ex:
            logger.error("Error retriving step size")
            return 8

    def get_step_size(self, symbol):
        try:
            step = db_client.stepsizes.find_one({"symbol": symbol})
            if step:
                return float(step["lot_size"]["stepSize"])
            return float(0.0)
        except Exception as ex:
            logger.error("Error retriving step size")
            return float(0.0)

    def get_min_notional(self, symbol):
        try:
            step = db_client.stepsizes.find_one({"symbol": symbol})
            if step:
                return float(step["min_notional"]["minNotional"])
            return float(0.0)
        except Exception as ex:
            logger.error("Error retriving step size")
            return float(0.0)

    def get_price(self, symbol, precision=8):
        try:
            price_info = self.client.get_symbol_ticker(symbol=symbol)
            return round(Decimal(price_info.get("price")), precision)
        except (BinanceAPIException, BinanceRequestException) as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def calculate_sell_qty(self, price, amount, step_size):
        quantity = float(amount)/float(price)
        step_precision_decimal = str(step_size).split(".")[1]
        step_precision = len(step_precision_decimal) if int(
            step_precision_decimal) > 0 else 0

        abs_quantity = round(quantity, step_precision)
        print(f"price:{price}: amount:{amount} :quantity::::{quantity}: abs_quantity: {abs_quantity}:::step_precision:{step_precision}")
        return abs_quantity

    def calculate_buy_qty(self, price, amount, step_size):
        quantity = float(amount)/float(price)
        step_precision_decimal = str(step_size).split(".")[1]
        step_precision = len(step_precision_decimal) if int(
            step_precision_decimal) > 0 else 0

        abs_quantity = round(quantity, step_precision)
        print(f"price:{price}: amount:{amount} :quantity::::{quantity}: abs_quantity: {abs_quantity}:::step_precision:{step_precision}")
        return abs_quantity

    def get_balance(self, coin_name):
        """Query coin balance in exchange account

        Args:
            coin_name (string): Name of coin

        Raises:
            Exception: Raise exception if coin is not found

        Returns:
            float: Coin balance.

        """
        try:
            balance_info = self.client.get_asset_balance(coin_name)
            if not balance_info:
                raise UserAdviceException(
                    f"Coin not found in account in {self.name} exchange")
            return balance_info.get("free")
        except (BinanceAPIException, BinanceRequestException) as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def track_coin(self, payload):
        pass

    def get_prices(self):
        """Returns a list of symbols and their prices

        API: https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client.get_symbol_ticker
        Return Example:
            [
                {
                    "symbol": "LTCBTC",
                    "price": "4.00000200"
                },
                {
                    "symbol": "ETHBTC",
                    "price": "0.07946600"
                }
            ]
        """
        return self.client.get_symbol_ticker()

    def get_symbol_info(self, coin_name=None, pair_base="BTC", symbol=None):
        """
        Reference:
            https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client.get_symbol_info
        """
        try:
            if not symbol:
                if not coin_name and pair_base:
                    raise Exception(
                        "Both coin name and base is required where symbol not specified")
                symbol = f"{coin_name}{pair_base}".upper()
            info = self.client.get_symbol_info(symbol=symbol)
            return info
        except (BinanceAPIException, BinanceRequestException) as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def get_open_orders(self, coin_name, pair_base="BTC"):
        try:
            symbol = f"{coin_name}{pair_base}".upper()
            orders = self.client.get_open_orders(symbol=symbol)
            logger.debug(f"orders: {orders}")
            return orders
        except (BinanceAPIException, BinanceRequestException) as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def get_all_orders(self, coin_name, limit=5, pair_base="BTC"):
        try:
            symbol = f"{coin_name}{pair_base}".upper()
            orders = self.client.get_all_orders(symbol=symbol, limit=limit)
            logger.debug(f"orders: {orders}")
            return orders
        except (BinanceAPIException, BinanceRequestException) as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)
