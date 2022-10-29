import asyncio
import json
from decimal import Decimal
from datetime import datetime
from typing import Union
from datetime import datetime

# DB
from model.db_work import create_table, add_data, get_data, update_data, del_data
# SETTINGS
from settings.tables_models import created_tables_on_start
# Dataclasses
from model.transaction_data_class import Transaction
from model.user_data_class import UserData


async def db_create_tables() -> bool:
    """Create tables for SIH from settings.tables_models"""
    res = await asyncio.gather(
        *[asyncio.create_task(create_table(db_name=table_name, columns=table))
          for table_name, table in created_tables_on_start.items()]
    )

    if all_res := all(res):
        print(f'Успешное создание всех БД ({len(res)})!')
    return all_res


async def db_add_user(user_id: str,
                      user_name: str,
                      default_value_type: str = 'RUB',
                      total: str = '{}',
                      settings: str = '{}',
                      ):
    """Add user to user_data"""
    res = await add_data(db_name='user_data',
                         data={
                             'user_id': user_id,
                             'user_name': user_name,
                             'default_value_type': default_value_type,
                             'total': total,
                             'settings': settings,
                         })

    if res:
        print(f'Успешно создан пользователь {user_name} с ID: {user_id}!')
    return res

async def db_add_transaction(transaction: Transaction):
    """Add transaction to user_transaction"""

    res = await add_data(db_name='user_transaction',
                         data={
        'user_id': transaction.user_id,
        'timestamp': int(datetime.timestamp(datetime.now())),
        'spended_currency': transaction.spended_currency,
        'spended_count': transaction.spended_count,
        'received_currency': transaction.received_currency,
        'received_count': transaction.received_count,
    })

    # await update_user_total_info(transaction)

    if res:
        print(f'Успешно добавлена транзакция пользователя {transaction.user_id}!')
    return res


async def db_get_user_transaction(user_id: str, selected_page: int = 1):
    res = await get_data(db_name='user_transaction',
                         criterias={'user_id': user_id})
    # TODO: добавить разбивку на чанки по 10 транзакций и выдавать SELECTED_PAGE-транзакцию -1
    return res


async def db_del_user_transaction(user_id: str, trans_id: int):
    res = await del_data(db_name='user_transaction',
                         criterias={'user_id': user_id,
                                    'id': trans_id})
    return res


async def db_update_user_total_info(user_id: str, new_total: dict):
    """Update user total cash after transaction"""

    # total = await get_user_total(user_id)

    await update_data(db_name='user_data',
                      data={
                          'total': json.dumps(new_total),
                      },
                      criterias={
                           'user_id': user_id,
                      })


async def db_update_user_settings(user_id: str, new_settings: dict):
    """Update user's settings"""

    await update_data(db_name='user_data',
                      data={
                          'settings': json.dumps(new_settings),
                      },
                      criterias={
                           'user_id': user_id,
                      })


async def db_get_user_total(user_id: str) -> dict:
    """Return dict with users total data or empty dict on error"""
    user_data = await get_data(db_name='user_data',
                               criterias={'user_id': user_id})

    if not user_data:
        return {}

    try:
        raw_total = user_data[0][-1]
        total = json.loads(raw_total)
        return total if isinstance(total, dict) else {}
    except IndexError as e:
        print(f'Ошибка получения общей информации пользователя {user_id}: {e=}')
        return {}
    except json.JSONDecodeError as e:
        print(f'Ошибка при загрузке данных из JSON: {e=}')
        return {}


async def db_get_user_data(user_id: str) -> Union[bool, UserData]:
    """Return users data from DB as an instance of a class UserData"""
    raw_user_data = await get_data(db_name='user_data',
                               criterias={'user_id': user_id})

    if not raw_user_data:
        return False

    user_data = UserData().from_raw_data(raw_user_data[0])

    return user_data


async def db_add_user_statistics(user_id: str, summ_val: str, summ_prc: str):
    res = await add_data(db_name='user_stats',
                         data={
        'user_id': user_id,
        'timestamp': int(datetime.timestamp(datetime.now())),
        'summary_profit': summ_val,
        'summary_profit_perc': summ_prc,
    })

    if res:
        print(f'Успешно добавлена статистика пользователя {user_id}!')

    return res


async def db_get_user_statistics(user_id: str) -> list:
    """Return users data from DB as an instance of a class UserData"""
    raw_user_stats = await get_data(db_name='user_stats',
                                   criterias={'user_id': user_id})

    return raw_user_stats



if __name__ == '__main__':
    ...
    print(int(datetime.timestamp(datetime.now().replace(hour=0, minute=0, second=0))))
