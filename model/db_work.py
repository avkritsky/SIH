import asyncio
from classes.db import DBManager
from settings.config import default_path_to_db
from settings.tables_models import user_table


async def create_table(db_name: str = 'user_data',
                       db_path: str = default_path_to_db,
                       columns: dict = user_table) -> bool:
    """Function for create table with DB_NAME in DB_PATH with COLUMNS"""
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
                   data: dict,
                   db_path: str = default_path_to_db):
    """Add data to DB_NAME"""
    column_names = ', '.join(data.keys())
    values_placeholder = ', '.join('?' * len(data))
    values = tuple(data.values())

    query = f"""INSERT INTO {db_name}({column_names})
                VALUES 
                (
                    {values_placeholder}
                )
    """

    res = await DBManager(path=db_path).execute(query, values)
    if res:
        print(f'Successful added data to DB {db_name}!')
    return res


async def get_data(db_name: str,
                   criterias: dict = None,
                   order_by: str = None,
                   desc: bool = False,
                   db_path: str = default_path_to_db) -> list:
    criterias = criterias or {}

    query = f"""SELECT *
                FROM {db_name}
    """

    if criterias:
        placeholders = (f'{column} = ?' for column in criterias)
        query += f' WHERE {" AND ".join(placeholders)}'

    if order_by:
        query += f' ORDER BY {order_by}' + ('', ' DESC')[desc]

    db = DBManager(path=db_path)
    res = await db.select(query, tuple(criterias.values()))
    if res:
        print(f'Successful select data from db {db_name}!')
        print(f'{db.last_result=}')
    return db.last_result


async def del_data(db_name: str,
                   criterias: dict = None,
                   db_path: str = default_path_to_db):
    criterias = criterias or {}

    query = f"""DELETE FROM {db_name} """

    if criterias:
        placeholders = (f'{column} = ?' for column in criterias)
        query += f' WHERE {" AND ".join(placeholders)}'

    db = DBManager(path=db_path)
    res = await db.execute(query, tuple(criterias.values()))
    if res:
        print(f'Successful deleted data from db {db_name}!')
        return True
    return False


async def update_data(db_name: str,
                      data: dict,
                      criterias: dict = None,
                      db_path: str = default_path_to_db):

    criterias = criterias or {}

    data_lines = [f'{header} = ?' for header, value in data.items()]

    query = f"""UPDATE {db_name}
                SET {", ".join(data_lines)}
            """

    data_holder = list(data.values())

    if criterias:
        placeholders = (f'{column} = ?' for column in criterias)
        query += f' WHERE {" AND ".join(placeholders)}'
        data_holder += list(criterias.values())

    res = await DBManager(path=db_path).execute(query, tuple(data_holder))

    if res:
        print('Успешное обновление данных!')

    return res


if __name__ == '__main__':
    # asyncio.run(add_data(db_name='user_transaction', data={'user_id': 'a17e16',
    #                        'operation_type': 'BUY',
    #                        'spended_currency': 'BTC',
    #                        'spended_count': 6,
    #                        'received_currency': 'USDT',
    #                        'received_count': 130000,}))
    asyncio.run(update_data(db_name='user_transaction',
                            data={'spended_count': 888},
                            criterias={'user_id': 'a17e16'}))
