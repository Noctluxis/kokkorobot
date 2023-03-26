from nonebot.plugin import on_command
from kokkoro import Bot, configs
from kokkoro.typing import CQEvent, T_State, GroupMessageEvent, PrivateMessageEvent
from kokkoro.service import parse_gid


leave = on_command('quit', aliases={'退群'})


@leave.handle()
async def quit_rec(bot: Bot, event: CQEvent, state: T_State):
    if event.user_id not in configs.SUPERUSERS:
        await leave.finish('Insufficient authority.')
    if isinstance(event, GroupMessageEvent):
        state['gids'] = [event.group_id]
    elif isinstance(event, PrivateMessageEvent):
        gid = event.get_plaintext().split()
        if gid:
            state['gids'] = gid


@leave.got('gids', prompt='请输入需要退出的群聊群号', args_parser=parse_gid)
async def group_quit(bot: Bot, event: CQEvent, state: T_State):
    failed = []
    succ = []
    for gid in state['gids']:
        try:
            await bot.set_group_leave(group_id=gid)
            succ.append(gid)
        except:
            failed.append(gid)
    msg = f'已尝试退出{len(succ)}个群'
    if failed:
        msg += f"\n退出{len(failed)}个群失败：\n{failed}"
    su = configs.SUPERUSERS[0]
    await bot.send_private_msg(user_id=su, message=msg)