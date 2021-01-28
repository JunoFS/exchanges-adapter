from os import environ
import logging
import math

from kucoin.client import Market, Trade, User
from core.exceptions import (UserAdviceException, ValidationException)
from ..interface import ServiceInterface
from ..helpers import calculate_lcm

logger = logging.getLogger(__name__)


class KucoinService(ServiceInterface):
    name = 'ku'

    def __init__(self, **kwargs):
        self.api_key = kwargs["api_key"]
        self.api_secret = kwargs["api_secret"]
        self.passphrase = kwargs.get("passphrase")

        if not all([self.api_key, self.api_secret]):
            raise Exception(
                f"Both api_key and api_secret are required for {name} exchange")
        self.debug_mode = environ.get("DEBUG", False)

    def get_account(self):
        client = User(self.api_key, self.api_secret,
                      passphrase="chimera", is_sandbox=self.debug_mode)
        return client

    def buy(self, coin_name, quantity=None, pair_base="BTC", amount=None, order_type="market"):
        try:
            client = Trade(key=self.api_key, secret=self.api_secret, passphrase='chimera',
                           is_sandbox=self.debug_mode)
            symbol = f"{pair_base}-{coin_name}"
            precision = self.get_precision(coin_name)
            current_price = self.get_price(symbol)
            step_size = self.get_step_size(symbol)
            quantity = self.calculate_buy_qty(
                price=current_price, amount=amount, step_size=step_size)

            price = self.round_value(current_price, precision)
            quantity = self.round_value(quantity, precision)

            logger.info(
                f"symbol:{symbol}>price:{price}>qty:{quantity} > market: {order_type}")
            order_id = None
            if order_type.lower() == "market":
                order_id = client.create_market_order(
                    symbol, 'buy', size=quantity)
            elif order_type.lower() == "limit":
                order_id = client.create_limit_order(
                    symbol, 'buy', quantity, amount)

            logger.info(
                f"Bought order request:{symbol}>type:{order_type}>quantity:{quantity}")
            return order_id
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise UserAdviceException(ex)

    def get_precision(self, coin_name):
        try:
            info = self.get_symbol_info(coin_name)
            return int(info.get("precision"))
        except:
            return 8

    def round_value(self, value, precision):
        return round(float(value), precision)

    def sell(self, coin_name, quantity=None, pair_base="BTC", amount=None, order_type="market"):
        try:
            client = Trade(key=self.api_key, secret=self.api_secret, passphrase='chimera',
                           is_sandbox=self.debug_mode)
            symbol = f"BTC-{coin_name}"
            price = self.get_price(symbol)
            balance = self.get_balance(coin_name)

            quantity = self.calculate_sell_qty(price, amount)

            precision = self.get_precision(coin_name)
            price = self.round_value(price, precision)
            quantity = self.round_value(quantity, precision)

            logger.info(
                f"symbol:{symbol}>price:{price}>qty:{quantity} > market: {order_type}")

            if order_type.lower() == "market":
                order_id = client.create_market_order(
                    symbol, 'sell', size=quantity)
            elif order_type.lower() == "limit":
                order_id = client.create_limit_order(
                    symbol, 'sell', quantity, amount)
            logger.info(
                f"sold order request:{symbol}>type:{order_type}>quantity:{quantity}")
            return order_id
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise UserAdviceException(ex)

    def get_step_size(self, symbol):
        pass

    def get_price(self, symbol):
        try:
            client = Market(key=self.api_key,
                            secret=self.api_secret, is_sandbox=self.debug_mode)
            price_info = client.get_ticker(symbol=symbol)
            logger.info(f"price info: {price_info}")
            return float(price_info.get("price"))
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def calculate_sell_qty(self, price, amount, step_size=None):
        quantity = float(amount)/float(price)
        return quantity

    def calculate_buy_qty(self, price, amount, step_size=None):
        quantity = float(amount)/float(price)
        return quantity

    def get_balance(self, coin_name):
        try:
            user_account = self.get_account()
            balances = user_account.get_account_list(
                currency=coin_name, account_type="trade")
            logger.info(f"Balances: {balances}")
            if not balances.get("data"):
                raise UserAdviceException(
                    f"{coin_name} not found in account. I could not retrieve account balance.")
            balance_info = balances.get("data")[0]
            if not balance_info:
                raise UserAdviceException(
                    f"Coin not found in account in {self.name} exchange")
            return balance_info.get("available")
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def track_coin(self, payload):
        pass

    def get_prices(self):
        try:
            client = Market(key=self.api_key,
                            secret=self.api_secret, is_sandbox=self.debug_mode)
            prices = client.get_all_tickers()
            return [{"price": item.get("buy"), "symbol": item.get("symbol")} for item in prices.get("ticker")]
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)
        return self.client.get_all_tickers()

    def get_symbol_info(self, coin_name, pair_base="BTC"):
        try:
            client = Market(key=self.api_key,
                            secret=self.api_secret, is_sandbox=self.debug_mode)
            info = client.get_currency_detail(currency=coin_name)
            logger.info(f"currency info: {coin_name} > {self.name}")
            return info
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise Exception(ex)

    def get_open_orders(self, coin_name, pair_base="BTC"):
        pass

    def get_all_orders(self, coin_name, limit=5, pair_base="BTC"):
        pass
