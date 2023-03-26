import os
import time
import traceback
from datetime import datetime

import peewee

from kokkoro import logger

from kokkoro.configs.ecoop import (get_database, DB_PATH)

# Define Database Basics


def database(class_name):
    return peewee.SqliteDatabase(
            database=DB_PATH,
            pragmas={
                'journal_mode': 'wal',
                'cache_size': -1024 * 64,
            })


class BaseDatabase(peewee.Model):
    pass


# Define Database Structure
# 如果你要自己添加数据库的定义，请直接继承BaseDatabase类即可，如:
#   class example(BaseDatabase):
#       pass


class ecoop_data(BaseDatabase):
    """
    ecoop数据表
    uid:用户的QQ号(bigint)
    eco:用户的经济(Decimal,20,2,自动进位)
    coop:用户的协作(Decimal,20,2,自动进位)
    """
    uid = peewee.BigIntegerField(primary_key=True)
    eco = peewee.DecimalField(max_digits=20, decimal_places=2, auto_round=True, default=0)
    coop = peewee.DecimalField(max_digits=20, decimal_places=2, auto_round=True, default=0)


class ecoop_log(BaseDatabase):
    """
    ecop变动日志表
    target_uid:积分变动的用户QQ号(bigint)
    operator_uid:操作者QQ号(bigint)
    type:类型，0指代增加，1指代减少(int)
    ecoop:ecoop类型，0指代eco，1指代coop(int)
    exchange_ecoop:ecoop变动数额(Decimal,20,2,自动进位)
    reason:变动理由(varchar)
    time_created:变动时间(bigint)
    """
    target_uid = peewee.BigIntegerField()
    operator_uid = peewee.BigIntegerField()
    type = peewee.IntegerField()
    ecoop = peewee.IntegerField()
    exchange_ecoop = peewee.DecimalField(max_digits=20, decimal_places=2, auto_round=True, default=0)
    reason = peewee.CharField(default='')
    time_created = peewee.TimestampField(default=time.time())


# Define Exception Class

class DataBaseException(IOError):
    def __init__(self, database, error=None):
        self.database = database
        self.error = error

    def __str__(self):
        return "Error <{}> occurred when attempt to operate database <{}>".format(repr(self.error), repr(self.database))


class NotEnoughEcoopError(ValueError):
    def __init__(self, need_ecoop, now_ecoop):
        self.need_ecoop = need_ecoop
        self.now_ecoop = now_ecoop

    def __str__(self):
        return "Operation need {} ecoop, but you have {} ecoop" \
            .format(repr(self.need_ecoop), repr(self.now_ecoop))


class EcoopLimitExceededError(ValueError):
    def __init__(self, ecoop_limit, ecoop_type):
        """
        ecoop_type : 0:`spend` , 1:`get` (int)
        """
        self.ecoop_limit = ecoop_limit
        self.ecoop_type = 'spend' if ecoop_type == 0 else 'get'

    def __str__(self):
        return "Operation {} ecoop reached ecoop limit({} ecoop), please retry later." \
            .format(repr(self.ecoop_type), repr(self.ecoop_limit))


# Initialize Database

def init():
    logger.info(f'Initializing Database...')
    for db in BaseDatabase.__subclasses__():
        try:
            db_name = db.__name__
            db.bind(database(db_name))
            database(db_name).connect()
            if not db.table_exists():
                database(db_name).create_tables([db])
                logger.info(f'Table <{db_name}> not exists, will be created in database <{get_database(db_name)}>.')
            database(db_name).close()
        except Exception as e:
            traceback.print_exc()
            logger.critical(f'Error <{e}> encountered while initializing database <{get_database(db_name)}>.')


init()
