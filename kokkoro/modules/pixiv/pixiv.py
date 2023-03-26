import json
import timeout_decorator

from nonebot.plugin import on_command
from nonebot.adapters.cqhttp.exception import ActionFailed
import kokkoro
from kokkoro import Service, Bot, scheduler
from kokkoro.util import DailyNumberLimiter, FreqLimiter, ecoop, construct_node_message
from kokkoro.typing import MessageEvent, T_State, GroupMessageEvent, PrivateMessageEvent, Message
from kokkoro.ecoopshop import pixivshoplimit
from kokkoro import configs
from timeout_decorator.timeout_decorator import TimeoutError
from pixivpy3 import PixivError

from .pixivsource import get_pixiv, pixivapi

CD_NOTICE = '您冲得太快了，请稍候再冲'
_nlmt = DailyNumberLimiter()
_flmt = FreqLimiter(5)

sv_help = '''
查看P站作品
[/pixiv pixivid]查看指定id作品
[/pixiv]随机来张主页图
[/pixiv new]随机来张新作品
[/pixiv mark]随机来张收藏
[/pixiv rank]随机来张月榜（rankw星期榜，rankd日榜）
[/pixiv 关键词]搜索指定tag的作品
'''.strip()

sv = Service('pixiv', help_=sv_help, bundle='setu相关')
svp = Service('pixiv-push', help_=sv_help, bundle='setu相关', enable_on_default=False)

pixiv = sv.on_fullmatch('pixiv', aliases={'Pixiv'}, only_group=False)


@pixiv.handle()
async def handle_receive(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'

    sum_lmt = lmt_num(uid) + pixivshoplimit.get_num(uid)
    EXCEED_NOTICE = f'您今天P站看的太多啦（{sum_lmt}），如有需要请在商店里购买额度'
    if not _nlmt.check(uid, sum_lmt):
        if isinstance(event, GroupMessageEvent):
            await pixiv.finish(sender + EXCEED_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await pixiv.finish(EXCEED_NOTICE)
    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await pixiv.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await pixiv.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    try:
        args = str(event.get_message()).strip()
        if args:
            msg = await get_pixiv(args)
        else:
            msg = await get_pixiv('main')
        if len(msg) <= 6:
            for text in msg:
                await pixiv.send(text)
        else:
            await pixiv.send(msg[0])
            await pixiv.send(msg[1])
            await pixiv.send('图片过多，其余图片请于转发消息中查看')
            node_msg = construct_node_message(custom_user_id=int(bot.self_id), msg_list=msg)
            if isinstance(event, GroupMessageEvent):
                await bot.send_group_forward_msg(group_id=event.group_id, messages=node_msg)
            else:
                await bot.send_private_forward_msg(user_id=event.user_id, messages=node_msg)
        # if uid not in kokkoro.configs.SUPERUSERS:
        _nlmt.increase(uid)
        return
    except PixivError:
        await pixiv.finish("pixivapi连接失败，请稍候再试")
    except ActionFailed:
        await pixiv.finish("图太涩惹，发不出去")


set_token = on_command('settoken', priority=1)
set_host = on_command('sethost', priority=1)


@set_token.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent, state: T_State):
    if event.user_id not in configs.SUPERUSERS:
        await set_token.finish('Insufficient authority.')
    msg = event.message
    if msg:
        state["access_token"] = msg


@set_token.got('access_token', '请输入access_token')
async def get_access_token_token(bot: Bot, event: MessageEvent, state: T_State):
    pass


@set_token.got('refresh_token', '请输入refresh_token')
async def get_refresh_token(bot: Bot, event: MessageEvent, state: T_State):
    if state['access_token'] and state['refresh_token']:
        token_dict = {'access_token': state['access_token'], 'refresh_token': state['refresh_token']}
        token_dir = './data/pixiv_token.json'
        with open(token_dir, "w") as f:
            json.dump(token_dict, f)
        pixivapi.set_token()
        try:
            pixivapi.login()
        except:
            await set_token.finish('token错误，请重新设置')
    else:
        return


@set_host.handle()
async def sethost_handle(bot: Bot, event: MessageEvent, state: T_State):
    if event.user_id not in configs.SUPERUSERS:
        await set_host.finish('Insufficient authority.')
    args = str(event.get_message()).strip()
    if args:
        state["host"] = args


@set_host.got("host", prompt='请输入host')
async def got_host(bot: Bot, event: MessageEvent, state: T_State):
    host = state["host"]
    if not host:
        await set_host.finish("host不能为空")
    pixivapi.api.hosts = 'https://' + host
    await set_host.finish('设置成功')


@scheduler.scheduled_job('interval', minutes=10)
async def pixiv_push():
    try:
        pixiv_list = pixiv_get_list()
    except PixivError:
        kokkoro.logger.info('Scheduled job pixiv_push time out. Skipped.')
        return
    if not len(pixiv_list) == 0:
        for pid in pixiv_list:
            json_detail = pixivapi.get_detail(pid)
            text = f'作品名：{json_detail.illust.title}\n' \
                   f'作者：{json_detail.illust.user.name}@{json_detail.illust.user.account}\n' \
                   f'PixivID：{json_detail.illust.id}'
            texts = await pixivapi.get_image(json_detail)
            texts.insert(0, text)
            if len(texts) <= 6:
                for msg in texts:
                    await svp.broadcast(msg, 'pixiv推送', 0.5)
            else:
                await svp.broadcast(texts, 'pixiv推送', 0.5, node_msg=True)


@timeout_decorator.timeout(10)
def pixiv_get_list():
    pixivapi.login()
    return pixivapi.get_follow_list()


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
