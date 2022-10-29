user_table = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'user_id': 'TEXT NOT NULL',
    'user_name': 'TEXT NOT NULL',
    'default_value_type': 'TEXT',
    'total': 'TEXT',
    'settings': 'TEXT',
}

user_transaction = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'user_id': 'TEXT NOT NULL',
    'timestamp': 'INTEGER',
    'spended_currency': 'TEXT',
    'spended_count': 'TEXT',
    'received_currency': 'TEXT',
    'received_count': 'TEXT',
}

user_stats = {
    'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'user_id': 'TEXT NOT NULL',
    'timestamp': 'INTEGER',
    'summary_profit': 'TEXT',
    'summary_profit_perc': 'TEXT',
}

created_tables_on_start = {
    'user_data': user_table,
    'user_transaction': user_transaction,
    'user_stats': user_stats,
}
