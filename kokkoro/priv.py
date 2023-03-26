from datetime import datetime
from nonebot.adapters.cqhttp import Bot
from kokkoro import configs
from kokkoro.typing import CQEvent

BLACK = -999
DEFAULT = 0
NORMAL = 1
PRIVATE = 10
ADMIN = 21
OWNER = 22
WHITE = 51
SUPERUSER = 999
SU = SUPERUSER


# ===================== block list ======================= #
_black_group = {}  # Dict[group_id, expr_time]
_black_user = {}  # Dict[user_id, expr_time]


def set_block_group(group_id, time):
    _black_group[group_id] = datetime.now() + time


def set_block_user(user_id, time):
    if user_id not in configs.SUPERUSERS:
        _black_user[user_id] = datetime.now() + time


def check_block_group(group_id):
    if group_id in _black_group and datetime.now() > _black_group[group_id]:
        del _black_group[group_id]  # 拉黑时间过期
        return False
    return bool(group_id in _black_group)


def check_block_user(user_id):
    if user_id in configs.BLACK_LIST:
        return True
    if user_id in _black_user and datetime.now() > _black_user[user_id]:
        del _black_user[user_id]  # 拉黑时间过期
        return False
    return bool(user_id in _black_user)


def get_user_priv(event: CQEvent):
    uid = event.user_id
    if uid in configs.SUPERUSERS:
        return SUPERUSER
    if check_block_user(uid):
        return BLACK
    if uid in configs.WHITE_LIST:
        return WHITE
    if event.post_type == 'message':
        if event.message_type == 'group':
            if not event.anonymous:
                role = event.sender.role
                if role == 'member':
                    return NORMAL
                elif role == 'owner':
                    return OWNER
                elif role == 'admin':
                    return ADMIN
                elif role == 'administrator':
                    return ADMIN  # for cqhttpmirai
            return NORMAL
        if event.message_type == 'private':
            return PRIVATE
        return NORMAL
    else:
        return NORMAL
            

def check_priv(event: CQEvent, require: int) -> bool:
    return bool(get_user_priv(event) >= require)
