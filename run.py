from trading.autotrade import AutoTrade
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    asyncio.run(AutoTrade.listener("binance", "ETH",
                                   "BTC", 0.03994100, 0.03994300, 0.1))
