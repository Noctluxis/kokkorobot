import time
import traceback
from decimal import Decimal
from typing import List, Tuple
from bisect import bisect

from peewee import PeeweeException

import kokkoro
from kokkoro import Bot
from kokkoro.configs.ecoop import global_ecoop
from kokkoro.util import DailyNumberLimiter
from kokkoro.util.ecoopdb import (DataBaseException, NotEnoughEcoopError,
                                   EcoopLimitExceededError, database,
                                   ecoop_data, ecoop_log)

eco_get_limiter = DailyNumberLimiter(global_ecoop.DAILY_ECOOP_GET_LIMIT[0])
eco_spend_limiter = DailyNumberLimiter(global_ecoop.DAILY_ECOOP_SPEND_LIMIT[0])
coop_get_limiter = DailyNumberLimiter(global_ecoop.DAILY_ECOOP_GET_LIMIT[1])
coop_spend_limiter = DailyNumberLimiter(global_ecoop.DAILY_ECOOP_SPEND_LIMIT[1])


class Ecoop:
    """
    积分操作类,包括:
    - get_ecoop:获取ecoop数额
    - check_ecoop:检查ecoop数额
    - add_ecoop:增加ecoop(原子操作)
    - spend_ecoop:消费ecoop(原子操作)
    - give_ecoop:给予ecoop(原子操作)
    - (异步)ecoop_log:获取ecoop日志
    - (异步)ecoop_rank:获取本群ecoop排行
    有返回值时即为成功操作。
    操作失败时会返回以下异常:
    `DataBaseException`:数据库操作异常
    `NotEnoughEcoopError`:欲消耗超过自己持有的ecoop数
    `EcoopLimitExceededError`:超过日获取/消耗ecoop上限
    `AttributeError`:参数错误
    """

    def __init__(self, session):
        """
        实例化时请传入`ev(CQEvent)` 或 `session(CommandSession)` 或 `uid(int)`。
        """
        if type(session) == (int or str):
            try:
                self.uid = int(session)
            except:
                raise AttributeError(
                    'Cannot initialize class,please ensure type of session is CQEvent or CommandSession or int.')
        else:
            try:
                self.uid = session.user_id
            except AttributeError:
                self.uid = session.event.user_id
            except:
                raise AttributeError(
                    'Cannot initialize class,please ensure type of session is CQEvent or CommandSession or int.')

        self.raw_session = session

    def _write_log(self, target_uid: int, ecoop_type: str, exchange_ecoop: Decimal, reason: str = ''):
        try:
            ecoop_log.replace(
                target_uid=target_uid,
                operator_uid=self.uid,
                type=0 if exchange_ecoop > 0 else 1,
                ecoop=0 if ecoop_type == 'eco' else 1,
                exchange_ecoop=exchange_ecoop,
                reason=reason,
                time_created=time.time()).execute()

        except PeeweeException as e:
            raise DataBaseException('ecoop', e)

    def get_ecoop(self, ecoop_type: str) -> Decimal:
        """
        获取ecoop数额
        参数:ecoop类型'eco'或'coop'
        返回:积分数量
        """
        try:
            ecoop = ecoop_data.get_or_create(uid=self.uid)
            ecoop_r = ecoop[0].eco if ecoop_type == 'eco' else ecoop[0].coop
            return round(ecoop_r, 2)

        except PeeweeException as e:
            raise DataBaseException('ecoop', e)

    def check_ecoop(self, ecoop_type: str, ecoop) -> bool:
        """
        检查ecoop数额
        检查ecoop数额是否足以扣除
        参数:ecoop类型'eco'或'coop' 欲花费的ecoop数
        返回:能扣除True,反之False(bool)
        """
        try:
            ecoop = Decimal(ecoop)
            return self.get_ecoop(ecoop_type) - ecoop >= 0

        except:
            traceback.print_exc()
            return False

    def add_ecoop(self, ecoop_type: str, ecoop, reason='') -> Decimal:
        """
        增加：ecoop
        参数:ecoop类型'eco'或'coop' 增加的ecoop数量
        返回:操作后的ecoop数量
        """
        try:
            ecoop = Decimal(ecoop)
            type_num = 0 if ecoop_type == 'eco' else 1

            if global_ecoop.ENABLE_GET_LIMIT[type_num]:
                limiter = eco_get_limiter if type_num == 0 else coop_get_limiter
                if not limiter.check(self.uid):
                    raise EcoopLimitExceededError(
                        global_ecoop.DAILY_ECOOP_GET_LIMIT[type_num], 1)

            if type_num == 0:
                ecoop_data.replace(uid=self.uid, eco=ecoop_data.get_or_create(uid=self.uid)[0].eco + ecoop,
                                   coop=ecoop_data.get_or_create(uid=self.uid)[0].coop).execute()
            else:
                ecoop_data.replace(uid=self.uid, eco=ecoop_data.get_or_create(uid=self.uid)[0].eco,
                                   coop=ecoop_data.get_or_create(uid=self.uid)[0].coop + ecoop).execute()

            if global_ecoop.ENABLE_GET_LIMIT[type_num]:
                limiter.increase(self.uid, ecoop)

            self._write_log(self.uid, ecoop_type, ecoop, reason)

            if type_num == 0:
                return ecoop_data.get_or_create(uid=self.uid)[0].eco
            else:
                return ecoop_data.get_or_create(uid=self.uid)[0].coop

        except PeeweeException as e:
            raise DataBaseException('ecoop', e)

    def spend_ecoop(self, ecoop_type: str, ecoop, forcibly=False, reason='') -> Decimal:
        """
        消费ecoop
        参数:ecoop类型'eco'或'coop' 要减少的ecoop数,是否强制扣除(不检查ecoop数)(可选,默认False)
        返回:操作后的ecoop数量
        """
        try:
            ecoop = Decimal(ecoop)
            type_num = 0 if ecoop_type == 'eco' else 1
            if type_num == 0:
                now_ecoop = ecoop_data.get_or_create(uid=self.uid)[0].eco
            else:
                now_ecoop = ecoop_data.get_or_create(uid=self.uid)[0].coop

            if now_ecoop - Decimal(ecoop) < 0:
                if not forcibly:
                    raise NotEnoughEcoopError(ecoop, now_ecoop)
                else:
                    pass

            if global_ecoop.ENABLE_SPEND_LIMIT[type_num]:
                limiter = eco_spend_limiter if type_num == 0 else coop_spend_limiter
                if not limiter.check(self.uid):
                    raise EcoopLimitExceededError(
                        global_ecoop.DAILY_ECOOP_SPEND_LIMIT[type_num], 0)

            if type_num == 0:
                ecoop_data.replace(uid=self.uid, eco=ecoop_data.get_or_create(uid=self.uid)[0].eco - ecoop,
                                   coop=ecoop_data.get_or_create(uid=self.uid)[0].coop).execute()
            else:
                ecoop_data.replace(uid=self.uid, eco=ecoop_data.get_or_create(uid=self.uid)[0].eco,
                                   coop=ecoop_data.get_or_create(uid=self.uid)[0].coop - ecoop).execute()

            if global_ecoop.ENABLE_SPEND_LIMIT[type_num]:
                limiter.increase(self.uid, ecoop)

            self._write_log(self.uid, ecoop_type, -ecoop, reason)
            if type_num == 0:
                return ecoop_data.get_or_create(uid=self.uid)[0].eco
            else:
                return ecoop_data.get_or_create(uid=self.uid)[0].coop

        except PeeweeException as e:
            raise DataBaseException('ecoop', e)

    def give_ecoop(self, ecoop_type: str, ecoop, target_uid: int, forcibly=False) -> Tuple[Decimal, Decimal]:
        """
        给予ecoop
        参数:ecoop类型'eco'或'coop' 要减少的ecoop数,接受ecoop的人的QQ号,是否强制扣除(不检查ecoop数)(可选,默认False)
        返回:操作后的给予ecoop的人的ecoop数量,接受ecoop的人的ecoop数量
        """
        try:
            ecoop = Decimal(ecoop)
            type_num = 0 if ecoop_type == 'eco' else 1
            if type_num == 0:
                now_ecoop = ecoop_data.get_or_create(uid=self.uid)[0].eco
            else:
                now_ecoop = ecoop_data.get_or_create(uid=self.uid)[0].coop

            if now_ecoop - Decimal(ecoop) < 0:
                if not forcibly:
                    raise NotEnoughEcoopError(ecoop, now_ecoop)
                else:
                    pass

            if global_ecoop.ENABLE_GET_LIMIT[type_num]:
                limiter1 = eco_get_limiter if type_num == 0 else coop_get_limiter
                if not limiter1.check(target_uid):
                    raise EcoopLimitExceededError(
                        global_ecoop.DAILY_ECOOP_GET_LIMIT[type_num], 1)

            if global_ecoop.ENABLE_SPEND_LIMIT:
                limiter2 = eco_spend_limiter if type_num == 0 else coop_spend_limiter
                if not limiter2.check(self.uid):
                    raise EcoopLimitExceededError(
                        global_ecoop.DAILY_ECOOP_SPEND_LIMIT[type_num], 0)

            with database('ecoop_data').atomic():
                if type_num == 0:
                    ecoop_data.replace(uid=self.uid,
                                       eco=ecoop_data.get_or_create(uid=self.uid)[0].eco - ecoop,
                                       coop=ecoop_data.get_or_create(uid=self.uid)[0].coop).execute()
                    ecoop_data.replace(uid=target_uid,
                                       eco=ecoop_data.get_or_create(uid=target_uid)[0].eco + ecoop,
                                       coop=ecoop_data.get_or_create(uid=self.uid)[0].coop).execute()
                else:
                    ecoop_data.replace(uid=self.uid,
                                       eco=ecoop_data.get_or_create(uid=target_uid)[0].eco,
                                       coop=ecoop_data.get_or_create(uid=self.uid)[0].coop - ecoop).execute()
                    ecoop_data.replace(uid=target_uid,
                                       eco=ecoop_data.get_or_create(uid=target_uid)[0].eco,
                                       coop=ecoop_data.get_or_create(uid=target_uid)[0].coop + ecoop).execute()

            self._write_log(target_uid, ecoop_type, -ecoop, reason='赠送他人ecoop')

            if global_ecoop.ENABLE_SPEND_LIMIT[type_num]:
                limiter1.increase(self.uid, ecoop)
            if global_ecoop.ENABLE_GET_LIMIT[type_num]:
                limiter2.increase(target_uid, ecoop)

            if type_num == 0:
                return ecoop_data.get_or_create(uid=self.uid)[0].eco, ecoop_data.get_or_create(uid=target_uid)[0].eco
            else:
                return ecoop_data.get_or_create(uid=self.uid)[0].coop, ecoop_data.get_or_create(uid=target_uid)[0].coop

        except PeeweeException as e:
            raise DataBaseException('ecoop', e)

    async def ecoop_log(self, limit: int = 5) -> List[dict]:
        """
        获取ecoop日志(异步)
        参数:获取的条数(可选,默认5条)
        返回:
        [{'target_uid': ...,
        'operator_uid': ...,
        'type': 'spend' or 'get',
        'ecoop': 'eco' or 'coop'
        'exchange_ecoop': ...,
        'reason': ...,
        'time_created': ...},
        {'target_uid': ...,
        'operator_uid': ...,
        ...},
        ...]
        """
        try:
            logs = ecoop_log.select().where(ecoop_log.operator_uid == self.uid). \
                order_by(ecoop_log.time_created.desc()).limit(limit)
            return [{'target_uid': log.target_uid,
                     'operator_uid': log.operator_uid,
                     'type': 'spend' if log.type == 1 else 'get',
                     'ecoop': 'eco' if log.ecoop == 0 else 'coop',
                     'exchange_ecoop': log.exchange_ecoop,
                     'reason': log.reason,
                     'time_created': log.time_created} for log in logs]
        except ecoop_log.DoesNotExist:
            return []
        except Exception as e:
            raise DataBaseException('ecoop', e)

    async def ecoop_rank(self, bot: Bot, ecoop_type: str, limit: int = 0) -> List[dict]:
        """
        获取ecoop排行(异步)
        参数:ecoop类型'eco'或'coop' 获取的条数(可选,默认10条)
        **请注意:必须传入原始session或event才能调用**
        返回:
            [{'uid': ...,
            'eco': ...},
            ...]
            或
            [{'uid': ...,
            'coop': ...},
            ...]
        """
        try:
            # self_id = self.raw_session.self_id
            group_id = self.raw_session.group_id
        except AttributeError:
            # self_id = self.raw_session.event.self_id
            group_id = self.raw_session.event.group_id
        except:
            raise AttributeError("In order to call this method,please offer session rather than int.")
        try:
            group_member_list = [i['user_id'] for i in
                                 await bot.get_group_member_list(group_id=group_id)]
            if ecoop_type == 'eco':
                if not limit == 0:
                    rank = ecoop_data.select().where(ecoop_data.uid.in_(group_member_list)).order_by(
                           ecoop_data.eco.desc()).limit(limit)
                else:
                    rank = ecoop_data.select().where(ecoop_data.uid.in_(group_member_list)).order_by(
                           ecoop_data.eco.desc())
                return [{'uid': i.uid, 'eco': i.eco} for i in rank]
            if ecoop_type == 'coop':
                if not limit == 0:
                    rank = ecoop_data.select().where(ecoop_data.uid.in_(group_member_list)).order_by(
                           ecoop_data.coop.desc()).limit(limit)
                else:
                    rank = ecoop_data.select().where(ecoop_data.uid.in_(group_member_list)).order_by(
                           ecoop_data.coop.desc())
                return [{'uid': i.uid, 'coop': i.coop} for i in rank]
        except Exception as e:
            raise DataBaseException('ecoop', e)


def get_coop_level(uid) -> int:
    if uid in kokkoro.configs.SUPERUSERS:
        return 11
    ecoop = Ecoop(uid)
    coop = int(ecoop.get_ecoop('coop'))
    breakpoints = [100, 300, 500, 750, 1000, 1500, 2000, 3000, 4000]
    level = list(range(1, 11))
    return level[bisect(breakpoints, coop)]
