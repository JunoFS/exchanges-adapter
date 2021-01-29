import os
import logging
import json
from hashes.simhash import simhash
import asyncio
import time

from .ws import BinaceWebsocket

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class AutoTrade:
    @classmethod
    async def listener(cls, exchange, coin_name, base_coin, buy_price, sell_price, allowable_percent):
        if exchange == "binance":
            api_key = os.environ.get("BINANCE_API_KEY")
            api_secret = os.environ.get("BINANCE_API_SECRET_KEY")
            bws = BinaceWebsocket(api_key, api_secret)
            await asyncio.gather(bws.listener(exchange, coin_name, base_coin, buy_price, sell_price, allowable_percent))
            logger.info(
                f"Started tracking: {coin_name} on {exchange}, to buy at: {buy_price} and sell at {sell_price}, allowable trade range: {allowable_percent}")
