import random

from nonebot.adapters.cqhttp import GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent, NotifyEvent
from nonebot import on_notice
from nonebot.rule import to_me
import kokkoro
from kokkoro import Service, Bot
from kokkoro.typing import Message


sv1 = Service('group-leave-notice', help_='退群通知')
sv2 = Service('group-welcome', help_='入群欢迎')

group_decrease = sv1.on_notice()
group_increase = sv2.on_notice()


@group_decrease.handle()
async def leave_notice(bot: Bot, event: GroupDecreaseNoticeEvent):
    if not event.is_tome():   
        user_info = await bot.get_stranger_info(user_id=event.user_id)
        nickname = user_info.get('nickname', '未知用户')
        await group_decrease.finish(f'{nickname}({event.user_id})退群了.')


@group_increase.handle()
async def increace_welcome(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.user_id == event.self_id:
        return  # ignore myself
    welcomes = kokkoro.configs.groupmaster.increase_welcome
    gid = event.group_id
    if gid in welcomes:
        await bot.send(event, welcomes[gid], at_sender=True)
    # elif 'default' in welcomes:
    #     await bot.send(event, welcomes[default], at_sender=True)

# poke = on_notice(rule=to_me(), block=True)
#
#
# @poke.handle()
# async def poke(bot: Bot, event: NotifyEvent):
#     if event.sub_type == 'poke':
#         msg = random.choice([
#             "你再戳！", "？再戳试试？", "别戳了别戳了再戳就坏了555", "我爪巴爪巴，球球别再戳了", "你戳你🐎呢？！",
#             "那...那里...那里不能戳...绝对...", "(。´・ω・)ん?", "有事恁叫我，别天天一个劲戳戳戳！", "欸很烦欸！你戳🔨呢",
#             "?", "差不多得了😅"
#         ])
#         await bot.call_api('send_group_msg', group_id=event.group_id, message=f'[CQ:poke,qq={str(event.sender_id)}]')
#         await poke.finish(msg)
