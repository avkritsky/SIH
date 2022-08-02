default_path_to_db = '../data/main.db'

columns_for_main_table = {
                           'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                           'user_id': 'TEXT NOT NULL',
                           'default_value_type': 'TEXT',
                           'total': 'TEXT'
                       }

columns_for_transaction_table = {
                           'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                           'user_id': 'TEXT NOT NULL',
                           'operation_type': 'TEXT',
                           'spended_currency': 'TEXT',
                           'spended_count': 'INTEGER',
                           'received_currency': 'TEXT',
                           'received_count': 'INTEGER',
                       }
