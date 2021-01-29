from .binance.service import BinanceService
from .kucoin.service import KucoinService
from .bittrex.service import BittrexService


class ExchangeAdapter(object):
    def __init__(self, obj, **adapted_methods):
        """We set the adapted methods in the object's dict"""
        self.obj = obj
        self.__dict__.update(adapted_methods)
        self.provider = None

    def __getattr__(self, attr):
        """All non-adapted calls are passed to the object"""
        return getattr(self.obj, attr)

    def original_dict(self):
        """Print original object dict"""
        return self.obj.__dict__


class Exchange():
    def __init__(self, name, **kwargs):
        """Initiate adapter service

        Args:
            name (string): Name of service
            **kwargs (object): Initialization data e.g object of access tokens
        """
        self.name = name
        self.provider = None
        self.set_adapter(**kwargs)

    def set_adapter(self, **kwargs):
        if self.name == 'binance':
            self.provider = BinanceService(**kwargs)
            scope = ExchangeAdapter(self.provider)
            return scope
        if self.name == 'bittrex':
            self.provider = BittrexService(**kwargs)
            scope = ExchangeAdapter(self.provider)
            return scope
        if self.name == 'kucoin':
            self.provider = KucoinService(**kwargs)
            scope = ExchangeAdapter(self.provider)
            return scope

    def get_account(self):
        scope = ExchangeAdapter(
            self.provider, run=self.provider.get_account)
        return scope.get_account()

    def buy(self, coin_name, amount, quantity=None, pair_base="BTC", order_type="market"):
        scope = ExchangeAdapter(
            self.provider, run=self.provider.buy)
        return scope.buy(coin_name=coin_name, amount=amount, quantity=quantity, pair_base=pair_base, order_type=order_type)

    def sell(self, coin_name, quantity=None, pair_base="BTC", amount=None, order_type="market"):
        scope = ExchangeAdapter(
            self.provider, run=self.provider.sell)
        return scope.sell(coin_name=coin_name, quantity=quantity, pair_base=pair_base, amount=amount, order_type=order_type)

    def get_open_orders(self, coin_name, pair_base="BTC"):
        scope = ExchangeAdapter(
            self.provider, run=self.provider.get_open_orders)
        return scope.get_open_orders(coin_name, pair_base)

    def get_all_orders(self, coin_name, limit=5, pair_base="BTC"):
        scope = ExchangeAdapter(
            self.provider, run=self.provider.get_all_orders)
        return scope.get_all_orders(coin_name, limit=5, pair_base="BTC")

    def get_prices(self):
        scope = ExchangeAdapter(
            self.provider, run=self.provider.get_prices)
        return scope.get_prices()

    def get_symbol_info(self, coin_name=None, pair_base="BTC", symbol=None):
        scope = ExchangeAdapter(
            self.provider, run=self.provider.get_symbol_info)
        return scope.get_symbol_info(coin_name, pair_base, symbol)
