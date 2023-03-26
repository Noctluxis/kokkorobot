import random

import kokkoro.configs
from kokkoro import Service, priv, Bot
from kokkoro.util import FreqLimiter
from kokkoro.util.ecoop import Ecoop, get_coop_level
from kokkoro.typing import GroupMessageEvent, PrivateMessageEvent, MessageEvent, T_State, Message
from kokkoro.ecoopshop import *

CD_NOTICE = '频繁购买可能会导致BUG，请稍候再试'
NOT_ENOUGH_NOTICE = '金币不够啦，主人需要可可萝的零花钱了吗'
_flmt = FreqLimiter(10)

sv = Service('_shop_', manage_priv=priv.SUPERUSER, visible=False)

SHOPNOTICE = '''
=====================
- KokkoroBot商店 -
=====================
主人，做好旅途的准备，度过更充实的冒险生活吧
[/购买 商品名]即可购买
========
[可以色色] 10金币 增加5次色色额度
[PixivPremium] 10金币 增加5次pixiv额度
[搜图卡] 5金币 增加2次搜图额度
[十连卷] 5金币 增加1500宝石(pcr抽卡小游戏用）
[3000宝石] 10金币 增加3000宝石(pcr抽卡小游戏用）
[天井卷] 30金币 一井(pcr抽卡小游戏用）
[集卡卷] 5金币 增加一次集卡机会(pcr集卡小游戏用)
[脆弱树脂] 10金币 增加60体力(原神圣遗物收集)
[心形甜甜圈] 10金币 提高COOP的道具
[苹果派] 50金币 提高COOP的道具
[混合浆果蛋糕] 100金币 提高COOP的道具
========
[/金币排行榜] 查看本群金币排行榜
[/钱包] 查看钱包余额
========
※购买的额度商品请确保当天使用，隔日将被清零
'''.strip()

shop_help = sv.on_fullmatch('shop', aliases={'商店'}, only_group=False)
buy = sv.on_fullmatch('buy', aliases={'购买'}, only_group=False)
rank_eco = sv.on_fullmatch('rank-eco', aliases={'金币排行榜'})
rank_coop = sv.on_fullmatch('rank-coop', aliases={'COOP排行榜', 'coop排行榜', 'Coop排行榜'})
get_eco = sv.on_fullmatch('钱包', aliases={'查看钱包'}, only_group=False)


@shop_help.handle()
async def shop_handle(bot: Bot, event: MessageEvent, state: T_State):
    await shop_help.finish(SHOPNOTICE)


@buy.handle()
async def buy_handle(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n'

    if not _flmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await buy.finish(sender + CD_NOTICE)
        elif isinstance(event, PrivateMessageEvent):
            await buy.finish(CD_NOTICE)

    _flmt.start_cd(uid)
    msg = event.message
    if msg:
        state["item"] = msg


@buy.got("item", prompt="请输入需要购买的商品")
async def buy_got(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n' if isinstance(event, GroupMessageEvent) else ''

    msg = str(state["item"])
    ecoop = Ecoop(uid)
    if msg == '可以色色':
        if ecoop.check_ecoop('eco', 10):
            ecoop.spend_ecoop('eco', 10, reason='shop')
            setushoplimit.increase(uid, 5)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == 'PixivPremium' or msg == 'pixivpremium':
        if ecoop.check_ecoop('eco', 10):
            ecoop.spend_ecoop('eco', 10, reason='shop')
            pixivshoplimit.increase(uid, 5)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == '搜图卡':
        if ecoop.check_ecoop('eco', 5):
            ecoop.spend_ecoop('eco', 5, reason='shop')
            imagesearchshoplimit.increase(uid, 2)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == '十连卷':
        if ecoop.check_ecoop('eco', 5):
            ecoop.spend_ecoop('eco', 5, reason='shop')
            jewelshoplimit.increase(uid, 1500)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == '3000宝石':
        if ecoop.check_ecoop('eco', 10):
            ecoop.spend_ecoop('eco', 10, reason='shop')
            jewelshoplimit.increase(uid, 3000)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == '天井卷':
        if ecoop.check_ecoop('eco', 30):
            ecoop.spend_ecoop('eco', 30, reason='shop')
            tenjoshoplimit.increase(uid, 1)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == '集卡卷':
        if ecoop.check_ecoop('eco', 5):
            ecoop.spend_ecoop('eco', 5, reason='shop')
            collectshoplimit.increase(uid, 1)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == '脆弱树脂':
        if ecoop.check_ecoop('eco', 10):
            ecoop.spend_ecoop('eco', 10, reason='shop')
            genshinshoplimit.increase(uid, 60)
            await buy.finish(sender + f'购买{msg}成功')
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    elif msg == '心形甜甜圈' or msg == '苹果派' or msg == '混合浆果蛋糕':
        if msg == '心形甜甜圈':
            eco_cost = 10
            coop = 4
        elif msg == '苹果派':
            eco_cost = 50
            coop = random.randint(23, 27)
        else:
            eco_cost = 100
            coop = random.randint(60, 70)

        if ecoop.check_ecoop('eco', eco_cost):
            coop_level = get_coop_level(uid)
            ecoop.spend_ecoop('eco', eco_cost, reason='shop')
            ecoop.add_ecoop('coop', coop, reason='shop')
            new_coop_level = get_coop_level(uid)
            msg_rank_up = f'COOP Rank Up!\n' if not new_coop_level == coop_level else ''
            if new_coop_level < 11:
                msg_coop_level = msg_rank_up + f'现在您的COOP等级为Rank.{new_coop_level}，以后也要和可可萝好好相处哦！'
            else:
                msg_coop_level = msg_rank_up + f'现在您的COOP等级为Rank.Max，以后也要和可可萝好好相处哦！'
            await buy.finish(sender + f'购买{msg}成功\n' + msg_coop_level)
        else:
            await buy.finish(sender + NOT_ENOUGH_NOTICE)
    else:
        await buy.finish('没有您想要的商品，请确认后重新购买')


@rank_eco.handle()
async def rank_eco_handle(bot: Bot, event: MessageEvent):
    ecoop = Ecoop(event)
    eco_rank = await ecoop.ecoop_rank(bot, 'eco')

    msg = f'本群金币排行榜\n'
    for i in range(len(eco_rank)):
        if (eco := eco_rank[i]['eco']) == 0:
            continue
        uid = eco_rank[i]['uid']
        user_info = await bot.get_stranger_info(user_id=uid)
        nickname = user_info.get('nickname', '未知用户')
        msg = msg + f'{str(i + 1)}.{nickname}:{str(eco)}金币\n'
    await rank_eco.finish(msg[0:-1])


@rank_coop.handle()
async def rank_eco_handle(bot: Bot, event: MessageEvent):
    ecoop = Ecoop(event)
    eco_rank = await ecoop.ecoop_rank(bot, 'coop')

    msg = f'本群COOP排行榜\n'
    j = 0
    for i in range(len(eco_rank)):
        if (coop := eco_rank[i]['coop']) == 0:
            continue
        uid = eco_rank[i]['uid']
        if uid in kokkoro.configs.SUPERUSERS:
            j = j + 1
            continue
        user_info = await bot.get_stranger_info(user_id=uid)
        nickname = user_info.get('nickname', '未知用户')
        coop_level = get_coop_level(uid)
        coop_level_s = str(coop_level) if coop_level < 11 else 'MAX'
        msg = msg + f'{str(i + 1 - j)}.{nickname}: Rank.{coop_level_s}\n'
    await rank_eco.finish(msg[0:-1])


@get_eco.handle()
async def get_eco_handle(bot: Bot, event: MessageEvent):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    sender = f'>{nickname}\n' if isinstance(event, GroupMessageEvent) else ''

    ecoop = Ecoop(uid)
    eco = ecoop.get_ecoop('eco')
    await get_eco.finish(sender + f'您的钱包还有{int(eco)}金币，需要可可萝的零花钱了吗？')
