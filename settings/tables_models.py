user_table = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'user_id': 'TEXT NOT NULL',
    'user_name': 'TEXT NOT NULL',
    'default_value_type': 'TEXT',
    'total': 'TEXT',
}

transaction_table = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'user_id': 'TEXT NOT NULL',
    'operation_type': 'TEXT',
    'spended_currency': 'TEXT',
    'spended_count': 'INTEGER',
    'received_currency': 'TEXT',
    'received_count': 'INTEGER',
}

created_tables_on_start = {
    'user_data': user_table,
    'transaction_data': transaction_table,
}
