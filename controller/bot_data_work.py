import asyncio
import json

# DB
from model.db_work import create_table, add_data, get_data, update_data
# SETTINGS
from settings.tables_models import created_tables_on_start
# Dataclasses
from model.transaction_data_class import Transaction, TransactionType


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
    try:
        transaction = Transaction(
            user_id=user_id,
            operation_type=(TransactionType.BUY, TransactionType.SEND)[operation_type == TransactionType.SEND.value],
            spended_currency=spended_currency,
            spended_count=spended_count,
            received_currency=received_currency,
            received_count=received_count,
        )
    except Exception as e:
        print(f'Ошибка при формировании transaction: {e=}')
        return False

    res = await add_data(db_name='user_transaction',
                         data={
        'user_id': user_id,
        'operation_type': operation_type,
        'spended_currency': spended_currency,
        'spended_count': spended_count,
        'received_currency': received_currency,
        'received_count': received_count,
    })

    await update_user_total_info(user_id, transaction)

    if res:
        print(f'Успешно добавлена транзакция пользователя {user_id}!')
    return res


async def show_user_transaction(user_id: str, selected_page: int = 1):
    res = await get_data(db_name='user_transaction',
                         criterias={'user_id': user_id})
    # TODO: добавить разбивку на чанки по 10 транзакций и выдавать SELECTED_PAGE-транзакцию -1
    return res


async def update_user_total_info(user_id: str, transaction_data: Transaction):
    """Update user total cash after transaction"""
    user_data = await get_data(db_name='user_data',
                               criterias={'user_id': user_id})

    if not user_data:
        return False

    try:
        default_val, raw_total = user_data[0][-2:]
        print(default_val, raw_total)
    except IndexError as e:
        print(f'Ошибка получения общей информации пользователя {user_id}: {e=}')
        return False

    try:
        total = json.loads(
            raw_total
        )

        add_transaction_data_to_total(total, transaction_data)
    except Exception as e:
        print(f'Ошибка обновления данных TOTAL у {user_id=}: {e=}')
        return False

    await update_data(db_name='user_data',
                      data={
                          'total': total,
                      },
                      criterias={
                           'user_id': user_id,
                      })


def add_transaction_data_to_total(user_total: dict, transaction_data: Transaction):

    user_total.setdefault(transaction_data.received_currency, 0)
    user_total[transaction_data.received_currency] += transaction_data.received_count

    user_total.setdefault(transaction_data.spended_currency, 0)
    user_total[transaction_data.spended_currency] -= transaction_data.spended_count


async def recalculation_user_total_info():
    """Take all user transactions from USER_TRANSACTION table and calculate total user cash"""
    ...



if __name__ == '__main__':
    ...
    # asyncio.run(create_tables())
    # asyncio.run(update_user_total_info(user_id='1'))