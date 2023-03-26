import random
from nonebot.plugin import on_command
from nonebot.rule import to_me
from kokkoro import Bot, R, Service, priv, util
from kokkoro.typing import CQEvent, Message, GroupMessageEvent, PrivateMessageEvent


# basic function for debug, not included in Service('chat')
zai = on_command('zai?', to_me(), aliases={'在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'})


@zai.handle()
async def say_hello(bot: Bot, event: CQEvent):
    await zai.send('はい！私はいつも貴方の側にいますよ！')


sv = Service('chat', visible=False)

sorry = sv.on_keyword('沙雕机器人', priority=2)
waifu = sv.on_keyword({'老婆', 'waifu', 'laopo'}, only_to_me=True, priority=2)
laogong = sv.on_keyword('老公', only_to_me=True, priority=2)
mua = sv.on_keyword('mua', only_to_me=True, priority=2)
seina = sv.on_keyword('来点星奏', priority=2)
dd = sv.on_keyword({'我朋友说他好了', '我有个朋友说他好了'}, priority=2)
haole = sv.on_keyword('我好了', priority=2)


@sorry.handle()
async def say_sorry(bot: Bot, event: CQEvent):
    await bot.send(event, 'ごめんなさい！嘤嘤嘤(〒︿〒)')


@waifu.handle()
async def chat_waifu(bot: Bot, event: CQEvent):
    if not priv.check_priv(event, priv.SUPERUSER):
        if random.random() < 0.50:
            await bot.send(event, Message(R.img('laopo.jpg').cqcode))
        else:
            await bot.send(event, Message(R.img('喊谁老婆呢.jpg').cqcode))
    else:
        await bot.send(event, 'mua~')


@laogong.handle()
async def chat_laogong(bot: Bot, event: CQEvent):
    if isinstance(event, GroupMessageEvent):
        await bot.send(event, '你走开啦！', at_sender=True)
    elif isinstance(event, PrivateMessageEvent):
        await bot.send(event, '你走开啦！')


@mua.handle()
async def chat_mua(bot: Bot, event: CQEvent):
    if isinstance(event, GroupMessageEvent):
        await bot.send(event, '笨蛋~', at_sender=True)
    elif isinstance(event, PrivateMessageEvent):
        await bot.send(event, '笨蛋~')


@seina.handle()
async def send_seina(bot: Bot, event: CQEvent):
    await bot.send(event, Message(R.img('星奏.png').cqcode))


@dd.handle()
async def ddhaole(bot: Bot, event: CQEvent):
    await bot.send(event, '那个朋友是不是你弟弟？')
    await util.silence(bot, event, 30)


@haole.handle()
async def nihaole(bot: Bot, event: CQEvent):
    await bot.send(event, '不许好，憋回去！')
    await util.silence(bot, event, 30)


# ============================================ #


@sv.on_keyword({'确实', '有一说一', 'u1s1', 'yysy'})
async def chat_queshi(bot: Bot, event: CQEvent):
    if random.random() < 0.1:
        await bot.send(event, Message(R.img('确实.jpg').cqcode))


@sv.on_keyword('会战')
async def chat_clanba(bot: Bot, event: CQEvent):
    if random.random() < 0.02:
        await bot.send(event, Message(R.img('我的天啊你看看都几点了.jpg').cqcode))


@sv.on_keyword('内鬼')
async def chat_neigui(bot: Bot, event: CQEvent):
    if random.random() < 0.10:
        await bot.send(event, Message(R.img('内鬼.png').cqcode))

nyb_player = f'''{R.img('newyearburst.gif').cqcode}
正在播放：New Year Burst
──●━━━━ 1:05/1:30
⇆ ㅤ◁ ㅤㅤ❚❚ ㅤㅤ▷ ㅤ↻
'''.strip()


@sv.on_keyword(('春黑', '新黑'))
async def new_year_burst(bot: Bot, event: CQEvent):
    if random.random() < 0.5:
        await bot.send(event, Message(nyb_player))

