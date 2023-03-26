from kokkoro import Bot, Service, aiohttpx
from kokkoro.util import DailyNumberLimiter, FreqLimiter
from kokkoro.typing import CQEvent, T_State, GroupMessageEvent, PrivateMessageEvent

_flmt = FreqLimiter(3)
CD_NOTICE = f'技能冷却中，请稍候再试'

sv_help = '''
能不能好好说话
[/好好说话 拼音缩写]拼音缩写解码
'''.strip()

sv = Service('anti_abbr', help_=sv_help, bundle='通用')

anti_abbr = sv.on_fullmatch('hhsh', aliases={'好好说话'}, only_group=False)


@anti_abbr.handle()
async def handle_first_receive(bot: Bot, event: CQEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'
    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await anti_abbr.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await anti_abbr.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    args = str(event.get_message()).strip()
    if args:
        state["word"] = args


@anti_abbr.got("word", prompt="请输入拼音字母缩写")
async def handle_city(bot: Bot, event: CQEvent, state: T_State):
    word = state["word"]
    if not word:
        await anti_abbr.reject("请重新输入！")
    data = await get_abbr(word)
    try:
        name = data[0]['name']
        print(name)
        content = data[0]['trans']
        print(content)
        await bot.send(event=event, message=name + "\n" + " ".join(content))
    except:
        await bot.send(event=event, message="没有找到结果")


async def get_abbr(word: str):
    url = "https://lab.magiconch.com/api/nbnhhsh/guess"

    headers = {
        'origin': 'https://lab.magiconch.com',
        'referer': 'https://lab.magiconch.com/nbnhhsh/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    }
    data = {
        "text": f"{word}"
    }

    res = await aiohttpx.post(url=url, headers=headers, data=data, timeout=(3.05, 6.05))
    msg = res.json()
    return msg if msg else []
