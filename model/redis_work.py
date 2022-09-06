import asyncio
import json
from datetime import timedelta
from typing import Union, Dict
from dataclasses import dataclass

import aioredis

from settings.api_key import REDIS_PASS, REDIS_ADDRESS


@dataclass
class RedisConnection:
    """Class for connecting to redis with ContextManager"""
    adress: str = REDIS_ADDRESS
    password: str = REDIS_PASS
    db: int = 1

    connection: Union[aioredis.client.Redis, None] = None

    async def __aenter__(self):
        try:
            self.connection = await aioredis.from_url(
                self.adress,
                password=self.password,
                db=1,
                decode_responses=True,
            )
        except Exception as e:
            print(f'ERROR: Ошибка при подключении к редису {e=}')
            return None

        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            await self.connection.close()
            self.connection = None


async def set_data_to_redis(data: Dict[str, dict], ttl: timedelta = None) -> bool:
    """Set data in redis by key, return success (True/False)"""
    async with RedisConnection() as redis:
        res = []
        for key, val in data.items():
            print(f'Записываю ключ {key} где {val=}')
            res.append(
                await redis.set(
                    key,
                    value=json.dumps(val, default=str),
                    ex=ttl,
                )
            )
        return all(res)


async def get_from_redis(key: str) -> dict:
    """Get data by KEY and return dict or empty dict if error or None result"""
    async with RedisConnection() as redis:
        data = await redis.get(key)
        if isinstance(data, str):
            data = json.loads(data)
        return {} if data is None else data


async def get_all_keys(mask: str = '*') -> list:
    """Get all keys from redis by MASK and return list of keys"""
    async with RedisConnection() as redis:
        res = await redis.keys(pattern=mask)
        return res


if __name__ == '__main__':
    ...
    # a = asyncio.run(get_all_keys())
    # print(a)
    b = asyncio.run(set_data_to_redis({'test2': {'a':11}}, ttl=timedelta(seconds=10)))
    print(b)
    a = asyncio.run(get_from_redis('test2'))
    print(a)
