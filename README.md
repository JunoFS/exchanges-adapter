# Python Adapter for Crypto Exchange Automation

The aim of this is to help developers and crypto enthuasists easily get started on algorithmic trading.

## Supported Exchanges

- Binance
- Bittrex
- Kucoin
- Uniswap (coming soon)

## Design - Write implementation once and deploy across exchages

Example:

    from exchanges.adapter import Exchange

    # To buy in Binance
    api_key = "BINANCE-EXCHANGE-API-KEY"
    api_secret = "BINANCE-EXCHANGE-API-SECRET"
    exchange_name = "binance"
    order_type = "market"

    exchange = Exchange(name=exchange_name, api_key=api_key, api_secret=api_secret)
    order = exchange.buy(
            coin_name=coin_name, amount=amount, quantity=quantity, pair_base=pair_base, order_type=order_type)
    print(order)

    # To bui in KuCoin
    api_key = "KUCOIN-EXCHANGE-API-KEY"
    api_secret = "KUCOIN-EXCHANGE-API-SECRET"
    exchange_name = "kucoin"
    order_type = "limit"

    exchange = Exchange(name=exchange_name, api_key=api_key, api_secret=api_secret)
    order = exchange.buy(
            coin_name=coin_name, amount=amount, quantity=quantity, pair_base=pair_base, order_type=order_type)
    print(order)

# Services interfaces

For exchanges, the following services are provided.

    class ServiceInterface():
        _metaclass__ = ABCMeta

        def getname(self):
            return self.name

        def setname(self):
            return self.name

        name = abstractproperty(getname, setname)

        @abstractmethod
        def buy(self, **kwargs):
            pass

        @abstractmethod
        def sell(self, **kwargs):
            pass

        @abstractmethod
        def update_step_sizes(self, **kwargs):
            pass

        @abstractmethod
        def update_coins(self, **kwargs):
            pass

        @abstractmethod
        def get_price(self, **kwargs):
            pass

        @abstractmethod
        def get_coin_balance(self, **kwargs):
            pass

        @abstractmethod
        def track_coin(self, **kwargs):
            pass

        @abstractmethod
        def get_orders(self, **kwargs):
            pass

        @abstractmethod
        def match_orders(self, **kwargs):
            pass
        
        @abstractmethod
        def get_user(self, **kwargs):
            pass

        @abstractmethod
        def has_coin(self, **kwargs):
            pass

        @abstractmethod
        def calculate_sell_qty(self, **kwargs):
            pass

        @abstractmethod
        def calculate_buy_qty(self, **kwargs):
            pass
