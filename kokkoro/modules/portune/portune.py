import random
import os
import kokkoro
from kokkoro.util import DailyNumberLimiter, ecoop
from kokkoro import Bot, R, Service, priv
from kokkoro.util import pic2b64
from kokkoro.typing import *
from .luck_desc import luck_desc
from .luck_type import luck_type
from PIL import Image, ImageSequence, ImageDraw, ImageFont
from kokkoro.util.ecoop import Ecoop


sv_help = '''
[/签到|/盖章|/抽签|/人品|/运势|/抽凯露签]
签到获取金币和COOP
随机角色/指定凯露预测今日运势
准确率高达114.514%！
'''.strip()
# 帮助文本
sv = Service('_portune_', manage_priv=priv.SUPERUSER, help_=sv_help, bundle='通用', visible=False)

todo_list = [
    '找伊绪老师上课',
    '给宫子买布丁',
    '和真琴一起寻找伤害优衣的人',
    '找小雪探讨女装',
    '与吉塔一起登上骑空艇',
    '和霞一起调查伤害优衣的人',
    '和佩可小姐一起吃午饭',
    '找小小甜心玩过家家',
    '帮碧寻找新朋友',
    '去真步真步王国',
    '找镜华补习数学',
    '陪胡桃排练话剧',
    '和初音一起午睡',
    '成为露娜的朋友',
    '帮铃莓打扫咲恋育幼院',
    '和静流小姐一起做巧克力',
    '去伊丽莎白农场给栞小姐送书',
    '观看慈乐之音的演出',
    '解救挂树的群友',
    '来一发十连',
    '井一发当期的限定池',
    '给妈妈买一束康乃馨',
    '购买黄金保值',
    '竞技场背刺',
    '去赛马场赛马',
    '用决斗为海马带来笑容',
    '成为魔法少女',
    '来几局日麻'
]

lmt = DailyNumberLimiter(1)
# 设置每日抽签的次数，默认为1
Data_Path = kokkoro.configs.RES_DIR
# 也可以直接填写为res文件夹所在位置，例：absPath = "C:/res/"
Img_Path = 'portunedata/imgbase'


portune = sv.on_fullmatch('签到', aliases={'盖章', '运势', '抽签', '人品'}, only_group=False)
portune_kyaru = sv.on_fullmatch('抽凯露签', aliases={'抽臭鼬签', '抽猫猫签'}, only_group=False)


@portune.handle()
async def portune_handle(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    if not lmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await portune.finish(f'>{nickname}\n明日はもう一つプレゼントをご用意してお待ちしますね')
        elif isinstance(event, PrivateMessageEvent):
            await portune.finish('明日はもう一つプレゼントをご用意してお待ちしますね')
    to_sender = f'>{nickname}\n' if isinstance(event, GroupMessageEvent) else ''
    lmt.increase(uid)
    model = 'DEFAULT'
    pic = drawing_pic(model)
    msg_login = login_bonus(uid)
    msg = to_sender + f'おかえりなさいませ、主さま' + pic + msg_login
    await portune.finish(msg)


@portune_kyaru.handle()
async def portune_kyaru_handle(bot: Bot, event: MessageEvent, state: T_State):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    if not lmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await portune.finish(f'>{nickname}\n明日はもう一つプレゼントをご用意してお待ちしますね')
        elif isinstance(event, PrivateMessageEvent):
            await portune.finish('明日はもう一つプレゼントをご用意してお待ちしますね')
    to_sender = f'>{nickname}\n' if isinstance(event, GroupMessageEvent) else ''
    lmt.increase(uid)
    model = 'KYARU'
    pic = drawing_pic(model)
    msg_login = login_bonus(uid)
    msg = to_sender + f'おかえりなさいませ、主さま' + pic + msg_login
    await portune_kyaru.finish(msg)


def login_bonus(uid):
    login_ecoop = Ecoop(uid)
    coop = ecoop.get_coop_level(uid)
    login_ecoop.add_ecoop(ecoop_type='coop', ecoop=random.randint(8, 12), reason='signin')
    new_coop = ecoop.get_coop_level(uid)
    msg_rank_up = f'COOP Rank Up!\n' if not new_coop == coop else ''
    if new_coop < 11:
        msg_coop_level = msg_rank_up + f'现在您的COOP等级为Rank.{new_coop}，以后也要和可可萝好好相处哦！'
    else:
        msg_coop_level = msg_rank_up + f'现在您的COOP等级为Rank.Max，以后也要和可可萝好好相处哦！'
    eco_num = get_eco(new_coop)
    eco_num_r = random.randint(eco_num - 2, eco_num + 2)
    login_ecoop.add_ecoop(ecoop_type='eco', ecoop=eco_num_r, reason='signin')
    todo = random.choice(todo_list)
    msg = f'\n{eco_num_r}金币を獲得しました\n私からのプレゼントです\n主人今天要{todo}吗？\n' + msg_coop_level
    return msg


def get_eco(coop_level):
    eco_lmt = {
        1: 10,
        2: 12,
        3: 14,
        4: 16,
        5: 18,
        6: 20,
        7: 22,
        8: 24,
        9: 26,
        10: 28,
        11: 20
    }
    return eco_lmt[coop_level]


def drawing_pic(model) -> Image:
    fontPath = {
        'title': R.img('portunedata/font/Mamelon.otf').path,
        'text': R.img('portunedata/font/sakura.ttf').path
    }

    if model == 'KYARU':
        base_img = get_base_by_name("frame_1.jpg")
    else:
        base_img = random_Basemap()

    filename = os.path.basename(base_img.path)
    charaid = filename.lstrip('frame_')
    charaid = charaid.rstrip('.jpg')

    img = base_img.open()
    # Draw title
    draw = ImageDraw.Draw(img)
    text, title = get_info(charaid)

    text = text['content']
    font_size = 45
    color = '#F5F5F5'
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath['title'], font_size)
    font_length = ttfront.getsize(title)
    draw.text((image_font_center[0]-font_length[0]/2, image_font_center[1]-font_length[1]/2),
                title, fill=color,font=ttfront)
    # Text rendering
    font_size = 25
    color = '#323232'
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath['text'], font_size)
    result = decrement(text)
    if not result[0]:
        return Exception('Unknown error in daily luck') 
    textVertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = vertical(result[i + 1])
        x = int(image_font_center[0] + (result[0] - 2) * font_size / 2 + 
                (result[0] - 1) * 4 - i * (font_size + 4))
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill = color, font = ttfront)

    img = pic2b64(img)
    img = MessageSegment.image(img)
    return img


def get_base_by_name(filename) -> R.ResImg:
    return R.img(os.path.join(Img_Path, filename))


def random_Basemap() -> R.ResImg:
    base_dir = R.img(Img_Path).path
    random_img = random.choice(os.listdir(base_dir))
    return R.img(os.path.join(Img_Path, random_img))


def get_info(charaid):
    for i in luck_desc:
        if charaid in i['charaid']:
            typewords = i['type']
            desc = random.choice(typewords)
            return desc, get_luck_type(desc)
    raise Exception('luck description not found')


def get_luck_type(desc):
    target_luck_type = desc['good-luck']
    for i in luck_type:
        if i['good-luck'] == target_luck_type:
            return i['name']
    raise Exception('luck type not found')


def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = ' '
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [numberOfSlices, text[:int(length / 2)] + fillIn, fillIn + text[int(length / 2):]]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [numberOfSlices, text[:int((length + 1) / 2)] + fillIn,
                                    fillIn + space + text[int((length + 1) / 2):]]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality:(i + 1) * cardinality])
    return result


def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return '\n'.join(list)
