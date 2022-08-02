import asyncio
from classes.db import DBManager
from settings.config import default_path_to_db, columns_for_main_table, columns_for_transaction_table


async def create_table(db_name: str = 'user_data',
                       db_path: str = default_path_to_db,
                       columns: dict = columns_for_main_table) -> bool:
    column_with_types = (f'{column} {column_type}' for column, column_type in columns.items())

    query = f"""CREATE TABLE IF NOT EXISTS {db_name}
                (
                    {', '.join(column_with_types)}
                );
    """
    res = await DBManager(path=db_path).execute(query=query)
    if res:
        print(f'Successful create DB {db_name}!')
    return res


async def add_data(db_name: str,
                   data: dict):

    column_names = ', '.join(data.keys())
    values_placeholder = ', '.join('?' * len(data))
    values = tuple(data.values())

    query = f"""INSERT INTO {db_name}({column_names})
                VALUES 
                (
                    {values_placeholder}
                )
    """

    res = await DBManager().execute(query, values)
    if res:
        print(f'Successful added data to DB {db_name}!')
    return res


async def get_data(db_name: str,
                   criterias: dict = None,
                   order_by: str = None,
                   desc: bool = False) -> list:
    criterias = criterias or {}

    query = f"""SELECT *
                FROM {db_name}
    """

    if criterias:
        placeholders = (f'{column} = ?' for column in criterias)
        query += f' WHERE {" AND ".join(placeholders)}'

    if order_by:
        query += f' ORDER BY {order_by}' + ('', ' DESC')[desc]

    db = DBManager()
    res = await db.select(query, tuple(criterias.values()))
    if res:
        print(f'Successful select data from db {db_name}!')
        print(f'{db.last_result=}')
    return db.last_result


if __name__ == '__main__':
    # asyncio.run(add_data(db_name='user_transaction', data={'user_id': 'a17e16',
    #                        'operation_type': 'BUY',
    #                        'spended_currency': 'BTC',
    #                        'spended_count': 6,
    #                        'received_currency': 'USDT',
    #                        'received_count': 130000,}))
    asyncio.run(get_data(db_name='user_transaction'))
