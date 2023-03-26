import os
import json
import random

from kokkoro import Service, Bot
from kokkoro.util import DailyNumberLimiter, FreqLimiter
from kokkoro.typing import CQEvent, T_State, GroupMessageEvent, PrivateMessageEvent

_nlmt = DailyNumberLimiter(10)
_flmt = FreqLimiter(3)
CD_NOTICE = f'收收味，请稍候再发'

sv_help = '''
发病小作文
[/发病 对象]来一篇发病小作文
'''.strip()

sv = Service('asill', help_=sv_help, bundle='通用')

asill = sv.on_fullmatch('发病')


@asill.handle()
async def handle_first_receive(bot: Bot, event: CQEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'
    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await asill.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await asill.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    args = str(event.get_message()).strip()
    if args:
        state["aim"] = args


@asill.got('aim', prompt='请发送[发病 对象]~')
async def handle_word(bot: Bot, event: CQEvent, state: T_State):
    aim = state["aim"]
    if not aim:
        await asill.reject("要发病的对象不能为空")
    illness = await get_data()
    text = illness["text"]
    person = illness["person"]
    text = text.replace(person, aim)
    await asill.finish(text)


async def get_data():
    _path = os.path.join(os.path.dirname(__file__), 'data.json')

    with open(_path, "r", encoding='utf-8') as df:
        words = json.load(df)

    return random.choice(words)
