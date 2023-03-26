from .Artifact import artifact_obtain, ARTIFACT_LIST, Artifact, calculate_strengthen_points
from .json_rw import init_user_info, updata_uid_stamina, user_info, save_user_info

from kokkoro import Service, Bot, scheduler
from kokkoro.typing import MessageEvent
from kokkoro.configs.genshin import STAMINA_RESTORE, MAX_STAMINA
from kokkoro.ecoopshop import genshinshoplimit

import random

sv_help = '''
[/原神副本] 查询当前有哪些副本，掉落哪个套装  
[/刷副本 副本名称] 刷一次副本，可获得狗粮点数和圣遗物  
[/查看圣遗物仓库 1] 查询仓库第一页有哪些圣遗物  
[/强化圣遗物10级 5] 把仓库编号为5的圣遗物强化10级  
[/圣遗物洗点 5] 把仓库编号为5的圣遗物洗点，洗点后返还50%的强化点数，强化等级降为0，全属性重新随机  
[/圣遗物详情 5] 查看圣遗物详情
[/转换狗粮 5] 把仓库编号为5的圣遗物销毁转化为狗粮，会返还80%狗粮点数  
[/查看体力值] 查看自己体力值
'''.strip()

sv = Service("genshin-artifact-collect", bundle="原神相关", help_=sv_help)

get_obtain = sv.on_fullmatch('原神副本', aliases={'圣遗物副本', '查看原神副本', '查看圣遗物副本'}, only_group=False)


@get_obtain.handle()
async def get_obtain_handle(bot: Bot, event: MessageEvent):
    mes = "当前副本如下\n"
    for name in artifact_obtain.keys():
        suits = " ".join(artifact_obtain[name])
        mes += f"{name}  掉落  {suits}\n"
    await get_obtain.finish(mes, at_sender=True)

get_artifact = sv.on_fullmatch('刷副本', only_group=False)


@get_artifact.handle()
async def _get_artifact_handle(bot: Bot, event: MessageEvent):
    obtain = event.message.extract_plain_text().strip()
    uid = str(event.user_id)
    init_user_info(uid)

    if obtain == "":
        return

    if not (obtain in artifact_obtain.keys()):
        mes = f"没有副本名叫 {obtain} ,发送 /原神副本 可查看所有副本"
        await get_artifact.finish(mes, at_sender=True)

    if user_info[uid]["stamina"] + genshinshoplimit.get_num(event.user_id) < 20:
        await get_artifact.finish("体力值不足，请等待体力恢复.\n发送 /查看体力值 可查看当前体力", at_sender=True)

    if user_info[uid]["stamina"] >= 20:
        user_info[uid]["stamina"] -= 20
    else:
        genshinshoplimit.decrease(event.user_id, 20 - user_info[uid]["stamina"])
        user_info[uid]["stamina"] = 0
    # 随机掉了几个圣遗物
    r = random.randint(1, 3)
    # 随机获得的狗粮点数
    strengthen_points = random.randint(70000, 100000)
    user_info[uid]["strengthen_points"] += strengthen_points

    mes = f"本次刷取副本为 {obtain} \n掉落圣遗物{r}个\n获得狗粮点数 {strengthen_points}\n"

    for _ in range(r):
        # 随机一个副本掉落的套装名字,然后随机部件的名字
        r_suit_name = random.choice(artifact_obtain[obtain])
        r_artifact_name = random.choice(ARTIFACT_LIST[r_suit_name]["element"])

        artifact = Artifact(r_artifact_name)

        number = int(len(user_info[uid]["warehouse"])) + 1

        # mes += f"当前仓库编号 {number}\n"
        mes += artifact.get_artifact_CQ_code(number)
        mes += "\n"

        user_info[uid]["warehouse"].append(artifact.get_artifact_dict())

    save_user_info()
    await get_artifact.finish(mes, at_sender=True)

warehouse = sv.on_fullmatch("查看圣遗物仓库", only_group=False)


@warehouse.handle()
async def _get_warehouse(bot: Bot, event: MessageEvent):
    page = event.message.extract_plain_text().strip()
    uid = str(event.user_id)
    init_user_info(uid)
    if page == "":
        page = "1"

    if not page.isdigit():
        await warehouse.finish("你需要输入一个数字", at_sender=True)

    page = int(page)

    mes = "仓库如下\n"
    txt = ""
    for i in range(5):
        try:
            ar = user_info[uid]["warehouse"][i + (page - 1) * 5]
            artifact = Artifact(ar)
            number = i + (page - 1) * 5 + 1
            # txt += f"\n\n仓库圣遗物编号 {i+(page-1)*5+1}"
            txt += artifact.get_artifact_CQ_code(number)
        except IndexError:
            pass
    if txt == "":
        txt = "当前页数没有圣遗物"
    mes += txt
    mes += f"\n\n当前为仓库第 {page}页，你的仓库共有 {(len(user_info[uid]['warehouse']) // 5) + 1} 页"
    await warehouse.finish(mes, at_sender=True)

strengthen = sv.on_fullmatch("强化圣遗物", only_group=False)


@strengthen.handle()
async def strengthen_handle(bot: Bot, event: MessageEvent):
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        txt = event.message.extract_plain_text().replace(" ", "")
        strengthen_level, number = txt.split("级")
    except Exception:
        await strengthen.finish("指令格式错误", at_sender=True)

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await strengthen.finish("圣遗物编号错误", at_sender=True)

    strengthen_level = int(strengthen_level)
    artifact = Artifact(artifact)
    strengthen_point = calculate_strengthen_points(artifact.level + 1, artifact.level + strengthen_level)

    if strengthen_point > user_info[uid]["strengthen_points"]:
        await strengthen.finish("狗粮点数不足\n你可以发送 /刷副本 副本名称 获取狗粮点数\n"
                                "或者发送 /转换狗粮 圣遗物编号 销毁仓库里不需要的圣遗物获取狗粮点数\n"
                                "发送 /转换全部0级圣遗物 可将全部0级圣遗物销毁", at_sender=True)

    user_info[uid]["strengthen_points"] -= strengthen_point

    for _ in range(strengthen_level):
        artifact.strengthen()

    mes = "强化成功，当前圣遗物属性为：\n"
    mes += artifact.get_artifact_detail()

    user_info[uid]["warehouse"][int(number) - 1] = artifact.get_artifact_dict()
    save_user_info()
    await strengthen.finish(mes, at_sender=True)

artifact_detail = sv.on_fullmatch("圣遗物详情", only_group=False)


@artifact_detail.handle()
async def detail_handle(bot: Bot, event: MessageEvent):
    number = event.message.extract_plain_text().strip()
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await artifact_detail.finish("编号错误", at_sender=True)

    artifact = Artifact(artifact)
    await artifact_detail.finish(artifact.get_artifact_detail(), at_sender=True)

unlearn = sv.on_fullmatch("圣遗物洗点", only_group=False)


@unlearn.handle()
async def unlearn_handle(bot: Bot, event: MessageEvent):
    number = event.message.extract_plain_text().strip()
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await unlearn.finish("编号错误", at_sender=True)

    artifact = Artifact(artifact)
    if artifact.level < 20:
        await unlearn.finish("没有强化满的圣遗物不能洗点", at_sender=True)

    strengthen_points = calculate_strengthen_points(1, artifact.level)
    strengthen_points = int(strengthen_points * 0.5)

    artifact.re_init()
    user_info[uid]["warehouse"][int(number) - 1] = artifact.get_artifact_dict()

    user_info[uid]["strengthen_points"] += strengthen_points

    mes = f"洗点完成，获得返还狗粮{strengthen_points} \n当前圣遗物属性如下：\n"
    mes += artifact.get_artifact_detail()
    save_user_info()

    await unlearn.finish(mes, at_sender=True)

trans = sv.on_fullmatch("转换狗粮", aliases={"转化狗粮"})


@trans.handle()
async def trans_handle(bot: Bot, event: MessageEvent):
    number = event.message.extract_plain_text().strip()
    uid = str(event.user_id)
    init_user_info(uid)

    try:
        artifact = user_info[uid]["warehouse"][int(number) - 1]
    except IndexError:
        await trans.finish("编号错误", at_sender=True)

    artifact = Artifact(artifact)

    strengthen_points = calculate_strengthen_points(0, artifact.level)
    strengthen_points = int(strengthen_points * 0.8)
    del user_info[uid]["warehouse"][int(number) - 1]
    user_info[uid]["strengthen_points"] += strengthen_points
    save_user_info()

    mes = f"转化完成，圣遗物已转化为{int(strengthen_points)}狗粮点数\n你当前狗粮点数为{int(user_info[uid]['strengthen_points'])} "
    await trans.finish(mes, at_sender=True)

get_user_stamina = sv.on_fullmatch("查看体力值", only_group=False)


@get_user_stamina.handle()
async def stamina_handle(bot: Bot, event: MessageEvent):
    uid = str(event.user_id)
    init_user_info(uid)
    if (potion := genshinshoplimit.get_num(event.user_id)) == 0:
        mes = f"你当前的体力值为{int(user_info[uid]['stamina'])}，体力值每{STAMINA_RESTORE}分钟恢复1点，" \
              f"自动恢复上限为{MAX_STAMINA}\n"
    else:
        mes = f"你当前的体力值为{int(user_info[uid]['stamina'])}，剩余脆弱树脂为{potion}，" \
              f"每{STAMINA_RESTORE}分钟恢复1点，自动恢复上限为{MAX_STAMINA}\n"
    mes += f"你当前的狗粮点数为{int(user_info[uid]['strengthen_points'])}"
    await get_user_stamina.finish(mes, at_sender=True)

trans_all = sv.on_fullmatch("转化全部0级圣遗物", aliases={"转换全部0级圣遗物"}, only_group=False)


@trans_all.handle()
async def trans_all_handle(bot: Bot, event: MessageEvent):
    uid = str(event.user_id)
    init_user_info(uid)

    _0_level_artifact = 0
    temp_list = []

    for artifact in user_info[uid]["warehouse"]:
        if artifact["level"] == 0:
            _0_level_artifact += 1
        else:
            temp_list.append(artifact)

    strengthen_points = _0_level_artifact * 3024
    user_info[uid]["warehouse"] = temp_list
    user_info[uid]["strengthen_points"] += strengthen_points
    save_user_info()

    await trans_all.finish(f"0级圣遗物已全部转化为狗粮，共转化{_0_level_artifact}个圣遗物，获得狗粮点数{strengthen_points}")


@scheduler.scheduled_job('interval', minutes=STAMINA_RESTORE)
async def _call():
    updata_uid_stamina()
