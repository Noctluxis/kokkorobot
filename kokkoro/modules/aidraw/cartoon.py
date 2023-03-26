import base64

from httpx._exceptions import TimeoutException

import kokkoro
from kokkoro import Service, Bot, aiohttpx
from kokkoro.ecoopshop import setushoplimit
from kokkoro.typing import MessageEvent, T_State, GroupMessageEvent, PrivateMessageEvent, Message
from kokkoro.util import DailyNumberLimiter, FreqLimiter
from kokkoro.util import ecoop
from nonebot.adapters.cqhttp import MessageSegment

from PIL import Image
from io import BytesIO

CD_NOTICE = '生成技能冷却中，请稍候再试'
_nlmt = DailyNumberLimiter()
_flmt = FreqLimiter(10)

sv_help = '''
二次元化
[/二次元化] 二次元化相应的图片
'''.strip()

sv = Service('cartoonization', help_=sv_help, bundle='setu相关')

cartoon = sv.on_fullmatch('二次元化', only_group=False)


@cartoon.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'

    sum_lmt = lmt_num(uid) + setushoplimit.get_num(uid)
    EXCEED_NOTICE = f'您今天二次元化太多啦（{sum_lmt}），如有需要请在商店里购买额度'
    if not _nlmt.check(uid, sum_lmt):
        if isinstance(event, GroupMessageEvent):
            await cartoon.finish(sender + EXCEED_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await cartoon.finish(EXCEED_NOTICE)
    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await cartoon.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await cartoon.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    msg = event.message
    if msg:
        state["setu"] = msg


@cartoon.got("setu", prompt="图呢？")
async def get_setu(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    try:
        msg: Message = Message(state["setu"])
        if msg[0].type == "image":
            await bot.send(event=event, message="少女祈祷中...")
            url = msg[0].data["url"]  # 图片链接
            msg_re = await cartonization(url)
            if uid not in kokkoro.configs.SUPERUSERS:
                _nlmt.increase(uid)
            await cartoon.finish(msg_re)
        else:
            await cartoon.reject("这不是图,重来!")
    except TimeoutException:
        await cartoon.finish("受到网络波动攻击，请再试一次")


async def cartonization(img_url):
    res = await aiohttpx.get(img_url)

    img = Image.open(BytesIO(res.content)).convert('RGB')
    if img.width * img.height >= 49_0000:
        img.thumbnail((700, 700))
    img.save(img_data := BytesIO(), format='jpeg')
    img_b64 = base64.b64encode(img_data.getvalue()).decode()

    url_cartoon = "https://hylee-white-box-cartoonization.hf.space/api/predict/"
    data = {
        "fn_index": 0,
        "data": [f"data:image/jpeg;base64,{img_b64}"],
    }

    res = await aiohttpx.post(url_cartoon, json=data, timeout=(63.05, 66.05))

    data = res.json()
    img_cartooon = data["data"][0].split(',')[1]
    return MessageSegment.image(file=f"base64://{img_cartooon}")


def lmt_num(uid):
    coop_level = ecoop.get_coop_level(uid)
    lmt = {
        1: 10,
        2: 12,
        3: 14,
        4: 16,
        5: 18,
        6: 20,
        7: 22,
        8: 24,
        9: 26,
        10: 28,
        11: 999
    }
    return lmt[coop_level]
