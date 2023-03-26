from .gacha import gacha_info, Gacha, POOL
from .pool_data import init_pool_list
import os
import json
from kokkoro import Service, priv, Bot
from kokkoro.typing import MessageEvent, GroupMessageEvent, MessageSegment
from kokkoro.util import DailyNumberLimiter
from kokkoro.configs.genshin import Gacha10Limit,Gacha90Limit,Gacha180Limit


daily_limiter_10 = DailyNumberLimiter(Gacha10Limit)
daily_limiter_90 = DailyNumberLimiter(Gacha90Limit)
daily_limiter_180 = DailyNumberLimiter(Gacha180Limit)

FILE_PATH = './data'

sv_help = '''
[/相遇之缘] 10连抽卡
[/纠缠之缘] 90连抽卡
[/原之井] 180连抽卡
[/原神卡池] 查看当前UP池
[/原神卡池切换] 切换其他原神卡池
[/更新原神卡池] 爬取官方的卡池数据
'''.strip()


sv = Service("genshin-gacha", bundle="原神相关", help_=sv_help)

group_pool = {
    # 这个字典保存每个群对应的卡池是哪个，群号字符串为key,卡池名为value，群号不包含在字典key里卡池按默认DEFAULT_POOL
}


def save_group_pool():
    with open(os.path.join(FILE_PATH, 'gid_pool.json'), 'w', encoding='UTF-8') as f:
        json.dump(group_pool, f, ensure_ascii=False)


# 检查gid_pool.json是否存在，没有创建空的
if not os.path.exists(os.path.join(FILE_PATH, 'gid_pool.json')):
    save_group_pool()


# 读取gid_pool.json的信息
with open(os.path.join(FILE_PATH, 'gid_pool.json'), 'r', encoding='UTF-8') as f:
    group_pool = json.load(f)


gacha10 = sv.on_fullmatch("相遇之缘", only_group=False)
gacha90 = sv.on_fullmatch("纠缠之缘", only_group=False)
gacha180 = sv.on_fullmatch("原之井", only_group=False)
get_pool = sv.on_fullmatch("原神卡池", aliases={'原神up', '原神UP', '原神Up'})
set_pool = sv.on_fullmatch("原神卡池切换", aliases={"切换原神卡池", "原神切换卡池"})
update_pool = sv.on_fullmatch("原神卡池更新", aliases={"更新原神卡池", "原神更新卡池"})


@gacha10.handle()
async def gacha10_handle(bot: Bot, event: MessageEvent):
    gid = str(event.group_id) if isinstance(event, GroupMessageEvent) else ''
    userid = event.user_id
    if not daily_limiter_10.check(userid):
        await gacha10.finish('今天已经抽了很多次啦，明天再来吧~')
    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    daily_limiter_10.increase(userid)
    await gacha10.finish(G.gacha_10())


@gacha90.handle()
async def gacha90_handle(bot: Bot, event: MessageEvent):
    gid = str(event.group_id) if isinstance(event, GroupMessageEvent) else ''
    userid = event.user_id
    if not daily_limiter_90.check(userid):
        await gacha90.finish('今天已经抽了很多次啦，明天再来吧~')
    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    daily_limiter_90.increase(userid)
    await gacha90.finish(G.gacha_90())


@gacha180.handle()
async def gacha_(bot: Bot, event: MessageEvent):
    gid = str(event.group_id) if isinstance(event, GroupMessageEvent) else ''
    userid = event.user_id
    if not daily_limiter_180.check(userid):
        await gacha180.finish('今天已经抽了很多次啦，明天再来吧~')
    daily_limiter_180.increase(userid)
    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    await gacha180.finish(G.gacha_90(180))


@get_pool.handle()
async def get_pool_handle(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    if gid in group_pool:
        info = gacha_info(group_pool[gid])
    else:
        info = gacha_info()
    await get_pool.finish(info, at_sender=True)


@set_pool.handle()
async def set_pool_handle(bot: Bot, event: GroupMessageEvent):
    if not priv.check_priv(event, priv.ADMIN):
        await set_pool.finish('只有群管理才能切换卡池')

    pool_name = event.message.extract_plain_text().strip()
    gid = str(event.group_id)

    if pool_name in POOL.keys():
        if gid in group_pool:
            group_pool[gid] = pool_name
        else:
            group_pool.setdefault(gid, pool_name)
        save_group_pool()
        await set_pool.finish(f"卡池已切换为 {pool_name} ")

    txt = "请使用以下命令来切换卡池\n"
    for i in POOL.keys():
        txt += f"/原神卡池切换 {i} \n"
    await set_pool.finish(txt)


@update_pool.handle()
async def update_pool_handle(bot: Bot, event: GroupMessageEvent):
    if not priv.check_priv(event, priv.ADMIN):
        await set_pool.finish('只有群管理才能更新卡池')
    await update_pool.send('正在更新卡池')
    await init_pool_list()
    await update_pool.finish('更新卡池完成')

