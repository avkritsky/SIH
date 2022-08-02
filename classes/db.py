from dataclasses import dataclass
from typing import Union

import aiosqlite

from settings.config import default_path_to_db


@dataclass
class DBManager:
    """Class for easy work with AIOSQLITE"""
    path: str = default_path_to_db
    last_result: Union[None, list] = None

    async def select(self, query: str, params: tuple = None) -> bool:
        """SELECT METHOD (result saved in LAST_RESULT)"""
        try:
            async with aiosqlite.connect(self.path) as db:
                async with db.execute(sql=query, parameters=params) as cursor:
                    self.last_result = []
                    async for row in cursor:
                        self.last_result.append(row)
        except Exception as e:
            print(f'Error: DB-SELECT: {e}\nWith query: {query}')
            return False
        else:
            return True

    async def execute(self, query: str, params: tuple = None) -> bool:
        """EXECUTE METHOD (execute and commit changes)"""
        try:
            async with aiosqlite.connect(self.path) as db:
                await db.execute(sql=query, parameters=params)
                await db.commit()
        except Exception as e:
            print(f'Error: DB-INSERT: {e}\nWith query: {query}')
            return False
        else:
            return True
