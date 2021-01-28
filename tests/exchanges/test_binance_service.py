from exchanges.binance.service import BinanceService
import unittest
import logging
from dotenv import load_dotenv

from os import environ

load_dotenv()


logger = logging.getLogger(__name__)


class TestBinanceService(unittest.TestCase):

    def setUp(self):
        self.service = BinanceService(api_key=environ.get("BINANCE_API_KEY"),
                                      api_secret=environ.get("BINANCE_API_SECRET"))
        return super().setUp()

    def test_buy(self):
        coin_name = "NEO"
        amount = 10
        buy_percentage = 0.20
        order = self.service.buy(coin_name, amount, buy_percentage)
        logger.debug(f"sell order: {order}")
        self.assertIsNotNone(order)

    def test_sell(self):
        coin_name = "NEO"
        buy_percentage = 0.20
        order = self.service.sell(coin_name, buy_percentage)
        logger.debug(f"sell order: {order}")
        self.assertIsNotNone(order)

    def test_get_balance(self):
        coin_name = "NEO"
        balance = self.service.get_balance(coin_name)
        logger.debug(f"balance: {balance}")
        self.assertIsNotNone(balance)

    def test_get_open_orders(self):
        coin_name = "NEO"
        orders = self.service.get_open_orders(coin_name)
        logger.debug(f"orders: {orders}")
        self.assertIsNotNone(orders)

    def test_get_all_orders(self):
        coin_name = "NEO"
        orders = self.service.get_all_orders(coin_name)
        logger.debug(f"orders: {orders}")
        self.assertIsNotNone(orders)


if __name__ == '__main__':
    unittest.main()
