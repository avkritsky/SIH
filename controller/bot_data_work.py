import asyncio
import json

# DB
from model.db_work import create_table, add_data, get_data
# SETTINGS
from settings.tables_models import created_tables_on_start


async def create_tables() -> bool:
    """Create tables for SIH from settings.tables_models"""
    res = await asyncio.gather(
        *[asyncio.create_task(create_table(db_name=table_name, columns=table))
          for table_name, table in created_tables_on_start.items()]
    )

    if all_res := all(res):
        print(f'Успешное создание всех БД ({len(res)})!')
    return all_res


async def add_user(user_id: str,
                   user_name: str,
                   default_value_type: str = 'RUB',
                   total: str = '{}',
                   ):
    """Add user to user_data"""
    res = await add_data(db_name='user_data',
                         data={
                             'user_id': user_id,
                             'user_name': user_name,
                             'default_value_type': default_value_type,
                             'total': total,
                         })

    if res:
        print(f'Успешно создан пользователь {user_name} с ID: {user_id}!')
    return res

async def add_transaction(user_id: str,
                          operation_type: str,
                          spended_currency: str,
                          spended_count: int,
                          received_currency: str,
                          received_count: int):
    """Add transaction to user_transaction"""
    res = await add_data(db_name='user_transaction',
                         data={
                             'user_id': user_id,
                             'operation_type': operation_type,
                             'spended_currency': spended_currency,
                             'spended_count': spended_count,
                             'received_currency': received_currency,
                             'received_count': received_count,
                         })

    if res:
        print(f'Успешно добавлена транзакция пользователя {user_id}!')
    return res


async def show_user_transaction(user_id: str, selected_page: int = 1):
    res = await get_data(db_name='user_transaction',
                         criterias={'user_id': user_id})
    # TODO: добавить разбивку на чанки по 10 транзакций и выдавать SELECTED_PAGE-транзакцию -1
    return res


if __name__ == '__main__':
    ...
    # asyncio.run(create_tables())
    asyncio.run(show_user_transaction(user_id='a17e16'))