from functools import wraps
from typing import Callable

async def params_wrapper(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # формирование ключа
        param_hash = hash((*args, *kwargs.values()))
        print(f'Данные по ключу: {func.__name__}:{param_hash}')

        # проверка значения ключа в редисе
        data_in_redis = False

        # выполнение функции
        if not data_in_redis:
            print('Данные не кешированы в редисе!')
            return await func(*args, **kwargs)

        # запись данных в редис
    return wrapper


if __name__ == '__main__':
    print(isinstance(params_wrapper, Callable))
