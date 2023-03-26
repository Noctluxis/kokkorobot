from kokkoro import Service, scheduler, Bot
from kokkoro.typing import MessageSegment, MessageEvent, GroupMessageEvent
from PIL import Image
from io import BytesIO

import os
import json
import time
import base64

FILE_PATH = os.path.dirname(__file__)

sv_help = '''
原神每日材料提醒
[/今日武器突破材料] 查看今日武器突破材料  
[/今日角色天赋材料] 查看今日角色天赋材料  
[/今日材料] 查看今天的武器突破材料和角色天赋材料 
'''.strip()

sv = Service("genshin-daily-material-reminder", bundle="原神相关", help_=sv_help, enable_on_default=False)

arms_material = sv.on_fullmatch("今日武器突破材料", aliases={"今日武器材料", "武器材料", "今日武器升级材料"}, only_group=False)
roles_material = sv.on_fullmatch("今日角色天赋材料", aliases={"今日角色材料", "角色材料", "今日天赋升级材料"}, only_group=False)
material = sv.on_fullmatch("今日材料", aliases={"今日素材"}, only_group=False)


def get_today_material(name: str):
    # 返回今天的材料图片CQ码
    week = time.strftime("%w")

    if week == "0":
        return "今天是周日，所有材料副本都开放了。"
    elif week in ["1", "4"]:
        png_name = f"{name}_周一周四.png"
    elif week in ["2", "5"]:
        png_name = f"{name}_周二周五.png"
    elif week in ["3", "6"]:
        png_name = f"{name}_周三周六.png"

    image = Image.open(os.path.join(FILE_PATH, "icon", png_name))
    bio = BytesIO()
    image.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    return MessageSegment.image(file=base64_str)


@arms_material.handle()
async def send_arms_material_remind(bot: Bot, event: MessageEvent):
    arms_material_CQ = get_today_material("武器突破材料")
    await arms_material_CQ.finish(arms_material_CQ)


@roles_material.handle()
async def send_roles_material_remind(bot: Bot, event: MessageEvent):
    roles_material_CQ = get_today_material("角色天赋材料")
    await roles_material.finish(roles_material_CQ)


@material.handle()
async def send_material_remind(bot: Bot, event: MessageEvent):
    if time.strftime("%w") == "0":
        await material.finish("今天是周日，所有材料副本都开放了。")
    arms_material_CQ = get_today_material("武器突破材料")
    roles_material_CQ = get_today_material("角色天赋材料")
    await material.send(arms_material_CQ)
    await material.finish(roles_material_CQ)


@scheduler.scheduled_job('cron', hour='8')
async def material_remind():
    # 每日提醒
    if time.strftime("%w") == "0":
        # 如果今天是周日就不发了
        return
    arms_material_CQ = get_today_material("武器突破材料")
    roles_material_CQ = get_today_material("角色天赋材料")
    await sv.broadcast(arms_material_CQ, '原神武器突破材料', 0.5)
    await sv.broadcast(roles_material_CQ, '原神角色天赋材料', 0.5)
        
        