# ecoop数据库路径
DB_PATH = './data/ecoop.db'


class global_ecoop:
    # eco and coop
    ENABLE_GET_LIMIT = [False, False]  # 是否启用限制
    ENABLE_SPEND_LIMIT = [False, False]
    DAILY_ECOOP_GET_LIMIT = [20, 20]  # 每天获取限制
    DAILY_ECOOP_SPEND_LIMIT = [5000, 20]  # 每天消耗限制


SQL_DB = {
    'default': 'default_db',
    ('ecoop_data', 'ecoop_log'): 'ecoop',
}


def get_database(name):
    for k, v in SQL_DB.items():
        if name in k:
            return v
    return SQL_DB['default']
