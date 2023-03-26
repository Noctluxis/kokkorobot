from kokkoro import Service, Bot, priv
from kokkoro.typing import MessageEvent, MessageSegment, GroupMessageEvent
from .query_resource_points import get_resource_map_mes, get_resource_list_mes, init_point_list_and_map

sv_help = '''
[/原神哪里有XXX] 查询XXX的位置图，XXX是资源的名字
[/原神资源列表] 查询所有的资源名称
'''.strip()

sv = Service("genshin-resource", bundle="原神相关", help_=sv_help)

res_points = sv.on_fullmatch("原神哪里有")
res_list = sv.on_fullmatch("原神资源列表")
update_list = sv.on_fullmatch("更新原神资源列表")
update_map = sv.on_fullmatch("更新原神资源地图")


@res_points.handle()
async def inquire_resource_points(bot: Bot, event: MessageEvent):
    resource_name = event.message.extract_plain_text().strip()
    if resource_name == "":
        return
    await res_points.finish(await get_resource_map_mes(resource_name))


@res_list.handle()
async def inquire_resource_list(bot: Bot, event: GroupMessageEvent):
    # 长条消息经常发送失败，所以只能这样了
    mes_list = []
    txt_list = get_resource_list_mes().split("\n")
    for txt in txt_list:
        data = {
            "type": "node",
            "data": {
                "name": "kokkorobot",
                "uin": "2326044349",
                "content": txt
                    }
                }
        mes_list.append(data)
    # await bot.send(ev, get_resource_list_mes(), at_sender=True)
    await bot.send_group_forward_msg(group_id=event.group_id, messages=mes_list)


@update_list.handle()
async def update_list_handle(bot: Bot, event: MessageEvent):
    if not priv.check_priv(event, priv.SUPERUSER):
        await update_list.finish('请联系维护组更新列表')
    await init_point_list_and_map()
    await update_list.finish('刷新成功')


@update_map.handle()
async def update_map_icon(bot: Bot, event: MessageEvent):
    if not priv.check_priv(event, priv.SUPERUSER):
        await update_map.finish('请联系维护组更新地图')
    await init_point_list_and_map()
    await update_map.finish('更新成功')

