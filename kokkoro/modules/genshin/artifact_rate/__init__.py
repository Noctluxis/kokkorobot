from .artifact_eval import *
from kokkoro import Service, Bot
from kokkoro.typing import MessageEvent, MessageSegment, T_State, Message
import requests

from base64 import b64encode
from io import BytesIO

sv_help = '''
[/圣遗物评分] 发送指令加截图进行评分
'''.strip()

sv = Service("genshin-artifact-rate", bundle="原神相关", help_=sv_help)


def get_format_sub_item(artifact_attr):
    msg = ""
    for i in artifact_attr["sub_item"]:
        msg += f'{i["name"]:\u3000<6} | {i["value"]}\n'
    return msg


artifact_rate = sv.on_fullmatch("圣遗物评分", only_group=False)


@artifact_rate.handle()
async def artifact_rate_handle(bot: Bot, event: MessageEvent, state: T_State):
    msg = event.message
    if len(msg) > 1:
        await artifact_rate.finish("只能上传一张截图哦", at_sender=True)
    if msg:
        state["img"] = msg


@artifact_rate.got("img", prompt='图呢')
async def artifact_rate_got(bot: Bot, event: MessageEvent, state: T_State):
    msg: Message = Message(state["img"])
    if not msg[0].type == "image":
        await artifact_rate.reject("这不是图，重来！")
    else:
        await artifact_rate.send(message="少女祈祷中...")
        image_url = msg[0].data["url"]
        image_content = BytesIO(requests.get(image_url).content)
        image_b64 = b64encode(image_content.read()).decode()
        try:
            artifact_attr = await get_artifact_attr(image_b64)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            await artifact_rate.finish("连接超时")
        if 'err' in artifact_attr.keys():
            err_msg = artifact_attr["full"]["message"]
            await artifact_rate.finish(f"发生了点小错误：\n{err_msg}",)
        # await bot.send(ev, f"识图成功！\n正在评分中...", at_sender=True)
        rate_result = await rate_artifact(artifact_attr)
        if 'err' in rate_result.keys():
            err_msg = rate_result["full"]["message"]
            await artifact_rate.finish("发生了点小错误：\n{err_msg}\n*注：将在下版本加入属性修改")
        format_result = f'圣遗物评分结果：\n主属性：{artifact_attr["main_item"]["name"]}\n{get_format_sub_item(artifact_attr)}' \
                        f'------------------------------\n总分：{rate_result["total_percent"]}\n' \
                        f'主词条：{rate_result["main_percent"]}\n副词条：{rate_result["sub_percent"]}\n评分、识图均来自genshin.pub'
        await artifact_rate.finish(format_result, at_sender=True)
