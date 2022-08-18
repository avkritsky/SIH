import asyncio

from model.api_work import execute_get_request

from settings.api_key import API_COINMARKET_KEY


async def update_crypto_prices_in_redis() -> bool:
    """Get new prices and save it in redis"""
    # get new prices
    new_raw_prices = await get_new_crypto_prices_from_api()

    if not new_raw_prices:
        return False

    # get data from responses data (names and prices)
    new_prices = format_raw_prices_data(new_raw_prices)

    if not new_prices:
        return False

    # FORMATTED DATA EXAMPLE
    # {'1INCH': {'fullname': '1inch Network', 'price': 0.7643219756703467},
    #  'AAVE': {'fullname': 'Aave', 'price': 98.74531533031404},

    # save to redis with ttl
    from pprint import pprint
    pprint(new_prices)
    ...


def format_raw_prices_data(raw_data: dict) -> dict:
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
        print(status, type(status))
        if status != 200:
            print(f'Bad response code: {status}!')
            return {}
        return raw_prices
    except Exception as e:
        print(f'Error on request to CryptoAPI: {e=}')
        return {}


if __name__ == '__main__':
    asyncio.run(update_crypto_prices_in_redis())
