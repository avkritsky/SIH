# функция получения цен (из редиса по названию валюты)
# функция обновления цен в редисе
# функция сохранения списка имеющихся валют ['BTC', 'USD', 'ETH', ... ]
import asyncio
from datetime import timedelta

from model.redis_work import set_data_to_redis, get_all_keys
from controller.bot_api_prices_work import get_new_crypto_prices_from_api

from settings.config import TTL_FOR_VALUES_IN_SEC


async def update_crypto_prices_and_save_to_redis():
    """Get new crypto prices and save it in redis"""
    raw_prices = await get_new_crypto_prices_from_api()

    if not raw_prices:
        return False

    prices = format_raw_prices_data(raw_prices)

    save_data_in_redis_res = await set_data_to_redis(prices, ttl=timedelta(seconds=TTL_FOR_VALUES_IN_SEC))

    if save_data_in_redis_res:
        print('Успешно обновлены цены крипто валют!')
    print(save_data_in_redis_res)

    print(await get_all_keys())



def format_raw_prices_data(raw_data: dict) -> dict:
    """Format raw crypto prices data to normal dict like {'BTS': {...}} """
    new_data = {}

    prices_data = raw_data.get('data', [])

    if not prices_data:
        return {}

    for item in prices_data:
        fullname = item.get('name')
        name = item.get('symbol')
        price = item.get("quote", {}).get("USD", {}).get("price", "err")
        last_updated = item.get("quote", {}).get("USD", {}).get("last_updated", "err")

        new_data[name] = {
            'fullname': fullname,
            'price': price,
            'last_updated': last_updated,
        }

    return new_data


if __name__ == '__main__':
    asyncio.run(update_crypto_prices_and_save_to_redis())
