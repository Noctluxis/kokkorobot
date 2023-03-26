from httpx._exceptions import TimeoutException
from nonebot.adapters.cqhttp.exception import ActionFailed
from kokkoro import Service, R, Bot
import kokkoro
from kokkoro.util import DailyNumberLimiter, FreqLimiter, ecoop
from kokkoro.typing import CQEvent, T_State, GroupMessageEvent, PrivateMessageEvent, Message
from kokkoro.ecoopshop import setushoplimit

from .setu_source import *
from .setu_nlp import *

CD_NOTICE = '您冲得太快了，请稍候再冲'
_nlmt = DailyNumberLimiter()
_flmt = FreqLimiter(5)

sv_help = '''
不可以色色-----罠
[/色图 关键词]搜索指定关键词的涩图
'''.strip()

sv = Service('setu', help_=sv_help, bundle='setu相关')
setu_folder = R.img('setu/').path

setu = sv.on_fullmatch('setu', aliases={'色图'}, only_group=False)
setu_nlp = sv.on_keyword(keywords={'色图', 'setu', '不够色', '涩图'}, only_group=False, priority=2)


@setu.handle()
async def handle_receive(bot: Bot, event: CQEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'

    sum_lmt = lmt_num(uid) + setushoplimit.get_num(uid)
    EXCEED_NOTICE = f'您今天色色太多啦（{sum_lmt}），请在商店里购买额度或明早5点后再来'
    if not _nlmt.check(uid, sum_lmt):
        if isinstance(event, GroupMessageEvent):
            await setu.finish(sender + EXCEED_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await setu.finish(EXCEED_NOTICE)
    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await setu.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await setu.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    try:
        args = str(event.get_message()).strip()
        msg = await get_setu(args) if args else await get_setu('random')
        await setu.send(msg)
        if uid not in kokkoro.configs.SUPERUSERS:
            _nlmt.increase(uid)
        return
    except TimeoutException:
        await setu.finish("受到网络波动攻击，请再试一次")
    except ActionFailed:
        await setu.finish("图太涩惹，发不出去")


@setu_nlp.handle()
async def handle_nlp_receive(bot: Bot, event: CQEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'

    sum_lmt = lmt_num(uid) + setushoplimit.get_num(uid)
    EXCEED_NOTICE = f'您今天色色太多啦（{sum_lmt}），请在商店里购买额度或明早5点后再来'
    if not _nlmt.check(uid, sum_lmt):
        if isinstance(event, GroupMessageEvent):
            await setu.finish(sender + EXCEED_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await setu.finish(EXCEED_NOTICE)
    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await setu.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await setu.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    try:
        sentence = str(event.get_message()).strip()
        if sentence1 := setu_nlp_test(sentence, 1):
            if text := await get_setu(sentence1):
                await setu_nlp.send(text)
                if uid not in kokkoro.configs.SUPERUSERS:
                    _nlmt.increase(uid)
                return
        if sentence2 := setu_nlp_test(sentence, 2):
            if text := await get_setu(sentence2):
                await setu_nlp.send(text)
                if uid not in kokkoro.configs.SUPERUSERS:
                    _nlmt.increase(uid)
                return
        args = await setu_msg_nlp(sentence)
        msg = await get_setu(args) if args else await get_setu('random')
        await setu_nlp.send(msg)
        if uid not in kokkoro.configs.SUPERUSERS:
            _nlmt.increase(uid)
        return
    except TimeoutException:
        await setu_nlp.finish("受到网络波动攻击，请再试一次")
    except ActionFailed:
        await setu_nlp.finish("图太涩惹，发不出去")


def lmt_num(uid):
    coop_level = ecoop.get_coop_level(uid)
    lmt = {
        1: 5,
        2: 15,
        3: 21,
        4: 27,
        5: 32,
        6: 37,
        7: 41,
        8: 45,
        9: 48,
        10: 50,
        11: 999
    }
    return lmt[coop_level]


