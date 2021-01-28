from abc import ABCMeta, abstractmethod, abstractproperty


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

