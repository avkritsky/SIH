import asyncio
import json

from model.api_work import execute_get_request

from settings.api_key import API_COINMARKET_KEY


async def get_new_valute_prices_from_api() -> dict:
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'

    try:
        status, raw_prices = await execute_get_request(url)
        if status != 200:
            print(f'Bad response code: {status}!')
            return {}
    except Exception as e:
        print(f'Error on request to CB: {e=}')
        return {}

    valutes = raw_prices.get('Valute', {})

    return valutes


async def get_new_crypto_prices_from_api() -> dict:
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    parameters = {
        'cryptocurrency_type': 'all',
        # 'start': '1',
        # 'limit': '10',
        'convert': 'USD',
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_COINMARKET_KEY,
    }

    try:
        status, raw_prices = await execute_get_request(url, parameters, headers)
        if status != 200:
            print(f'Bad response code: {status}!')
            return {}
        return raw_prices
    except Exception as e:
        print(f'Error on request to CryptoAPI: {e=}')
        return {}


if __name__ == '__main__':
    asyncio.run(get_new_valute_prices_from_api())
