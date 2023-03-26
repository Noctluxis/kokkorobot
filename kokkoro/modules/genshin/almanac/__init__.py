from kokkoro import Service, priv, Bot, scheduler
from kokkoro.typing import MessageSegment, MessageEvent, T_State, GroupMessageEvent
from .almanac import get_almanac_base64_str, load_data
from .tweaks import *
from .draw_lots import get_pic, draw_info, gen_pic
import os
import json

FILE_PATH = os.path.dirname(__file__)
DB_PATH = os.path.join(FILE_PATH, "assets", "config.json")
jdb = jsondb(DB_PATH)

sv_help = '''
[/原神黄历] 查看今天的黄历
[/原神抽签] 抽一签
[/解签] 解答抽签结果
'''.strip()

svr_help = '''
[/开启\关闭原神黄历提醒] 开启或关闭本群的每日黄历提醒（需管理员权限）
'''.strip()


sv = Service("genshin-almanac", bundle="原神相关", help_=sv_help)
svr = Service("genshin-almanac-reminder", bundle="原神相关", help_=svr_help, enable_on_default=False)

almanac = sv.on_fullmatch('原神黄历', only_group=False)


@almanac.handle()
async def send_almanac(bot: Bot, event: MessageEvent):
    almanac_base64 = get_almanac_base64_str()
    await almanac.finish(MessageSegment.image(file=almanac_base64))

reload_almanac = sv.on_fullmatch('重载原神黄历数据', only_group=False)


@reload_almanac.handle()
async def reload_data(bot: Bot, event: MessageEvent):
    if not priv.check_priv(event, priv.SUPERUSER):
        return
    load_data()
    await reload_almanac.finish("重载成功")


@scheduler.scheduled_job('cron', id='原神黄历', hour='8')
async def almanac_reminder():
    # 每日提醒
    almanac_base64 = get_almanac_base64_str()
    msg = MessageSegment.image(file=almanac_base64)
    await svr.broadcast(msg, 'genshin_almanac_reminder', 0.2)


draw = sv.on_fullmatch('原神抽签', only_group=False)


@draw.handle()
async def draw_lots(bot: Bot, event: MessageEvent):
    uid = str(event.user_id)
    quser = jdb.user(uid)

    if quser.db["time"] == get_time():
        result = draw_info(quser.pos)
        draw_pic = gen_pic(result)["pic"]
        cq_str = get_cq(draw_pic)
        msg = cq_str + "\n今天已经抽过签啦，明天再来吧~"
    else:
        draw_result = get_pic()
        pos = draw_result["pos"]
        pic = draw_result["pic"]
        cq_str = get_cq(pic)

        jdb.user(uid).write(pos)
        jdb.save()
        msg = cq_str

    await draw.finish(msg, at_sender=True)

answer_lots = sv.on_fullmatch('解签')


@answer_lots.handle()
async def answer_handle(bot: Bot, event: MessageEvent):
    uid = str(event.user_id)
    quser = jdb.user(uid)

    try:
        answer = draw_info(quser.pos)["answer"]
        msg = f'解签：' + answer
    except KeyError:
        msg = '你还没抽过签哦~向我说“/原神抽签”试试吧~'
    await answer_lots.finish(msg, at_sender=True)
