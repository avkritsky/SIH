# функция получения цен (из редиса по названию валюты)
# функция обновления цен в редисе
# функция сохранения списка имеющихся валют ['BTC', 'USD', 'ETH', ... ]
import asyncio
import json
from datetime import timedelta

from model.redis_work import set_data_to_redis, get_all_keys, get_from_redis
from controller.bot_api_prices_work import get_new_crypto_prices_from_api, get_new_valute_prices_from_api

from settings.config import TTL_FOR_VALUES_IN_SEC


async def update_crypto_prices_and_save_to_redis() -> set:
    """Get new crypto prices and save it in redis"""
    raw_prices = await get_new_crypto_prices_from_api()

    if not raw_prices:
        return set()

    prices = format_raw_prices_data(raw_prices)
    crypto_short_names = list(prices.keys())

    await set_data_to_redis({'crypto': crypto_short_names}, db=2)

    save_data_in_redis_res = await set_data_to_redis(prices, ttl=timedelta(seconds=TTL_FOR_VALUES_IN_SEC))

    if save_data_in_redis_res:
        print('Успешно обновлены цены крипто валют!')
        currency_names = await get_all_keys()
        return set(currency_names)

    return set()


async def update_valute_prices_and_save_to_redis() -> set:
    prices = await get_new_valute_prices_from_api()

    if not prices:
        return set()

    currency_short_names = list(prices.keys())

    await set_data_to_redis({'currency': currency_short_names}, db=2)
    save_data_in_redis_res = await set_data_to_redis(prices, ttl=timedelta(seconds=TTL_FOR_VALUES_IN_SEC))

    if save_data_in_redis_res:
        print('Успешно обновлены цены валют!')

    return set()


async def redis_get_currency_short_names() -> list:
    names: list = await get_from_redis('currency', db=2)

    if not names:
        return ['RUB', 'USD', 'EUR']

    try:
        names.remove('EUR')
    except ValueError:
        pass

    try:
        names.remove('USD')
    except ValueError:
        pass

    names = ['RUB', 'USD', 'EUR'] + names

    return names if names else []


async def redis_get_crypto_short_names() -> tuple:
    names = await get_from_redis('crypto', db=2)
    return names if names else tuple()



async def get_price(value_name: str = 'BTC') -> dict:
    """Get values price from redis by values name. Return dict with keys: fullname, price, last_update"""

    print(f'Пытаюсь получить валюту {value_name}')
    data = await get_from_redis(value_name)
    print(f'ПОлучил валюту {value_name}')
    if not data:
        print('Начинаю получать валюты по API')
        await update_valute_prices_and_save_to_redis()
        value_names = await update_crypto_prices_and_save_to_redis()
        print(value_names)
        if value_name not in value_names:
            print(f'В списке валют нету запрашиваемой: {value_name}!')
            return {}
        return await get_price(value_name)

    return data



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
    data = asyncio.run(get_price('USD'))
    print(type(data))
