from aiohttp import ClientSession


async def execute_post_request(url: str, data: dict = None):
    async with ClientSession().post(url=url, data=data) as res:
        data = await res.json()
        return data


async def execute_get_request(url: str, parameters: dict = None, headers: dict = None):
    async with ClientSession(headers=headers) as sess:
        async with sess.get(url=url, params=parameters) as request:
            status = request.status
            data = await request.json(content_type=None)
    return status, data



if __name__ == '__main__':
    ...

    # {'data': [{'circulating_supply': 19125012,
    #            'cmc_rank': 1,
    #            'date_added': '2013-04-28T00:00:00.000Z',
    #            'id': 1,
    #            'last_updated': '2022-08-18T18:28:00.000Z',
    #            'max_supply': 21000000,
    #            'name': 'Bitcoin',
    #            'num_market_pairs': 9677,
    #            'platform': None,
    #            'quote': {'USD': {'fully_diluted_market_cap': 489317553414.36,
    #                              'last_updated': '2022-08-18T18:28:00.000Z',
    #                              'market_cap': 445628765755.25256,
    #                              'market_cap_dominance': 40.0147,
    #                              'percent_change_1h': -0.41887086,
    #                              'percent_change_24h': -0.82842289,
    #                              'percent_change_30d': -0.5912546,
    #                              'percent_change_60d': 18.95705991,
    #                              'percent_change_7d': -3.62247572,
    #                              'percent_change_90d': -19.27418072,
    #                              'price': 23300.835876874356,
    #                              'tvl': None,
    #                              'volume_24h': 24509523985.664406,
    #                              'volume_change_24h': -20.2313}},
    #            'self_reported_circulating_supply': None,
    #            'self_reported_market_cap': None,
    #            'slug': 'bitcoin',
    #            'symbol': 'BTC',
    #            'tags': ['mineable',
    #                     'pow',
    #                     'sha-256',
    #                     'store-of-value',
    #                     'state-channel',
    #                     'coinbase-ventures-portfolio',
    #                     'three-arrows-capital-portfolio',
    #                     'polychain-capital-portfolio',
    #                     'binance-labs-portfolio',
    #                     'blockchain-capital-portfolio',
    #                     'boostvc-portfolio',
    #                     'cms-holdings-portfolio',
    #                     'dcg-portfolio',
    #                     'dragonfly-capital-portfolio',
    #                     'electric-capital-portfolio',
    #                     'fabric-ventures-portfolio',
    #                     'framework-ventures-portfolio',
    #                     'galaxy-digital-portfolio',
    #                     'huobi-capital-portfolio',
    #                     'alameda-research-portfolio',
    #                     'a16z-portfolio',
    #                     '1confirmation-portfolio',
    #                     'winklevoss-capital-portfolio',
    #                     'usv-portfolio',
    #                     'placeholder-ventures-portfolio',
    #                     'pantera-capital-portfolio',
    #                     'multicoin-capital-portfolio',
    #                     'paradigm-portfolio'],
    #            'total_supply': 19125012,
    #            'tvl_ratio': None},
