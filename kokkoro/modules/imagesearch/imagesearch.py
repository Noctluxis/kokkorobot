import asyncio

from httpx._exceptions import TimeoutException

import kokkoro
from kokkoro import Service, Bot
from kokkoro.ecoopshop import setushoplimit
from kokkoro.typing import MessageEvent, T_State, GroupMessageEvent, PrivateMessageEvent, Message
from kokkoro.util import DailyNumberLimiter, FreqLimiter
from kokkoro.util import ecoop, get_setu_from_url, construct_node_message
from .ascii2d import get_pic_ascii
from .saucenao import get_pic_sn

CD_NOTICE = '搜图技能冷却中，请稍候再试'
_nlmt = DailyNumberLimiter()
_flmt = FreqLimiter(10)

sv_help = '''
以图搜图
[/搜图] SauceNao或ascii2d以图搜图
'''.strip()

sv = Service('imagesearch', help_=sv_help, bundle='setu相关')

imagesearch = sv.on_fullmatch('搜图', only_group=False)


@imagesearch.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'

    sum_lmt = lmt_num(uid) + setushoplimit.get_num(uid)
    EXCEED_NOTICE = f'您今天搜图太多啦（{sum_lmt}），如有需要请在商店里购买额度'
    if not _nlmt.check(uid, sum_lmt):
        if isinstance(event, GroupMessageEvent):
            await imagesearch.finish(sender + EXCEED_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await imagesearch.finish(EXCEED_NOTICE)
    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await imagesearch.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await imagesearch.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    msg = event.message
    if msg:
        state["setu"] = msg


@imagesearch.got("setu", prompt="图呢？")
async def get_setu(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    try:
        msg: Message = Message(state["setu"])
        if msg[0].type == "image":
            await bot.send(event=event, message="少女祈祷中...")
            url = msg[0].data["url"]  # 图片链接
            msg_re = await get_result(url)
            if uid not in kokkoro.configs.SUPERUSERS:
                _nlmt.increase(uid)
            if len(msg_re) == 1:
                if len(msg_re[0]) == 1:
                    await imagesearch.finish(msg_re[0][0])
                else:
                    await imagesearch.send(msg_re[0][0])
                    node_msg = construct_node_message(custom_user_id=int(bot.self_id), msg_list=msg_re[0])
                    if isinstance(event, GroupMessageEvent):
                        await bot.send_group_forward_msg(group_id=event.group_id, messages=node_msg)
                    else:
                        await bot.send_private_forward_msg(user_id=event.user_id, messages=node_msg)
            else:
                for ascii2d_re in msg_re:
                    if len(ascii2d_re) == 1:
                        await imagesearch.send(ascii2d_re[0])
                    else:
                        await imagesearch.send(ascii2d_re[0])
                        node_msg = construct_node_message(custom_user_id=int(bot.self_id), msg_list=ascii2d_re)
                        if isinstance(event, GroupMessageEvent):
                            await bot.send_group_forward_msg(group_id=event.group_id, messages=node_msg)
                        else:
                            await bot.send_private_forward_msg(user_id=event.user_id, messages=node_msg)
                    await asyncio.sleep(0.5)
        else:
            await imagesearch.reject("这不是图,重来!")
    except TimeoutException:
        await imagesearch.finish("受到网络波动攻击，请再试一次")


async def get_result(url: str):
    image_data = await get_pic_sn(url)
    if (not image_data) or image_data[0][1] < 60:
        image_data = await get_pic_ascii(url)
        msg1 = await ascii2d_info(image_data, 0)
        msg2 = await ascii2d_info(image_data, 1)
        return [msg1, msg2]
    elif image_data:
        image_data_list = []
        for image_single_data in image_data:
            text = f'[SauceNao]匹配度：{image_single_data[1]}%\n{image_single_data[2]}\n作品信息：{image_single_data[3]}\n'
            if img_base64 := await get_setu_from_url(image_single_data[0]):
                image_data_list.append(text + img_base64)
            else:
                image_data_list.append(text)
        return [image_data_list]
    else:
        return ['搜不到哦']


async def ascii2d_info(img_data, mode: int) -> list:
    if len(img_data[mode]) == 0:
        return [f'图片超过5MB，尝试压缩后重试']
    img_data_list = []
    for img_data in img_data[mode]:
        mod = '色合検索' if mode == 0 else '特徴検索'

        if img_data[5] == 'pixiv':
            text = f'[ascii2d{mod}]\n标题：{img_data[1]}\n作者：{img_data[2]}\nPixiv地址：{img_data[3]}\n作者主页：{img_data[4]}'
        elif img_data[5] == 'twitter':
            text = f'[ascii2d{mod}]\n作者：{img_data[2]}\n发推时间：{img_data[1]}\n推特地址：{img_data[3]}\n作者主页：{img_data[4]}'
        else:
            return [f'搜不到哦']

        if img_base64 := await get_setu_from_url(img_data[0]):
            img_data_list.append(text + img_base64)
        else:
            img_data_list.append(text)

    return img_data_list


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
