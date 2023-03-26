from nonebot import on_command, permission
from kokkoro import Bot, configs
from kokkoro.util import get_setu_from_url
from kokkoro.typing import PrivateMessageEvent, T_State, Message, MessageSegment

forward = on_command('转发')


@forward.handle()
async def handle_first_receive(bot: Bot, event: PrivateMessageEvent, state: T_State):
    if event.user_id not in configs.SUPERUSERS:
        await forward.finish('')
    msg = str(event.get_message()).strip()
    if msg:
        state["num"] = msg


@forward.got("setu", prompt="图呢？")
async def get_setu(bot: Bot, event: PrivateMessageEvent, state: T_State):
    msg: Message = Message(state["setu"])
    if msg[0].type == "image":
        url = msg[0].data["url"]  # 图片链接
        if img_base64 := await get_setu_from_url(url):
            await bot.send_group_msg(group_id=int(state["num"]), message=img_base64)
        else:
            await forward.finish("受到网络波动攻击，请再试一次")
    else:
        await forward.reject("这不是图,重来!")
