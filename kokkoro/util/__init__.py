import os
import time
import base64
import unicodedata
import zhconv
import random
import nonebot
from io import BytesIO
from collections import defaultdict
from datetime import datetime, timedelta
import pytz
from matplotlib import pyplot as plt
from PIL import Image, ImageOps, ImageFilter
from nonebot.adapters.cqhttp import MessageSegment
import kokkoro
from kokkoro import Bot, configs, aiohttpx
from kokkoro.typing import Message, Union, CQEvent
try:
    import ujson as json
except:
    import json


def load_config(inbuilt_file_var):
    """
    Just use `config = load_config(__file__)`,
    you can get the config.json as a dict.
    """
    filename = os.path.join(os.path.dirname(inbuilt_file_var), 'config.json')
    try:
        with open(filename, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        kokkoro.logger.exception(e)
        return {}


async def delete_msg(bot: Bot, event: CQEvent):
    try:
        await bot.delete_msg(message_id=event.message_id)
    except Exception as e:
        kokkoro.logger.error(f'撤回失败. {type(e)}')


async def silence(bot: Bot, event: CQEvent, ban_time, skip_su=True):
    try:
        if skip_su and event.user_id in configs.SUPERUSERS:
            return
        await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=ban_time)
    except Exception as e:
        kokkoro.logger.error(f'禁言失败. {type(e)}')


def pic2b64(pic: Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def res2b64(res, anti_hexie: bool = True, original: bool = False, enhanced_anti_hexie: bool = False) -> str:
    bytes_stream = BytesIO(res.content)
    img = Image.open(bytes_stream)

    if anti_hexie:
        width, height = img.size
        img = img.convert("RGB")

        pixels = [[0, 0], [width - 1, 0], [0, height - 1], [width - 1, height - 1]]
        for p in pixels:
            img.putpixel((p[0], p[1]),
                         (random.randint(0, 255),
                          random.randint(0, 255),
                          random.randint(0, 255),
                          random.randint(0, 255)))

        if enhanced_anti_hexie:
            border = int(height / 10) + 3
            img = ImageOps.expand(img, (0, border, 0, border), 0)

        # img_up = img.crop((0, 0, width, border)).filter(ImageFilter.GaussianBlur(radius=32))
        # img_down = img.crop((0, height - border, width, height)).filter(ImageFilter.GaussianBlur(radius=32))
        # img_new = Image.new("RGB", (width, height + 2 * border))
        # img_new.paste(img_up, (0, 0))
        # img_new.paste(img, (0, border))
        # img_new.paste(img_down, (0, height + border))
        # img = img_new

        # img = ImageOps.expand(img, 5, random.randint(0, 16777216))
        # img = img.rotate(90, expand=True)
        # img = img.transpose(Image.FLIP_LEFT_RIGHT)

    img_buf = BytesIO()
    if not original:
        # img.save(img_buf, format='JPEG', quality=85)
        img.save(img_buf, format='BMP', quality=85)
    else:
        img.save(img_buf, format='BMP')
    base64_str = base64.b64encode(img_buf.getvalue()).decode('ascii')
    return 'base64://' + base64_str


def fig2b64(plt:plt) -> str:
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100)
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


async def get_setu_from_url(img_url: str, **kwargs):
    re_img = await aiohttpx.get(img_url, timeout=(3.05, 6.05))
    if re_img.status_code == 200:
        return MessageSegment.image(file=res2b64(re_img, **kwargs))
    else:
        return '色图不见了'


def construct_node_message(custom_user_id: int, msg_list: list, custom_nickname: str = 'kokkorobot') -> list[dict]:
    node_msg = []
    for msg in msg_list:
        if not msg:
            continue
        node_msg.append({
            'type': 'node',
            'data': {
                'name': custom_nickname,
                'user_id': custom_user_id,
                'uin': custom_user_id,
                'content': msg
            }
        })
    return node_msg


def concat_pic(pics, border=5):
    num = len(pics)
    w, h = pics[0].size
    des = Image.new('RGBA', (w, num * h + (num-1) * border), (255, 255, 255, 255))
    for i, pic in enumerate(pics):
        des.paste(pic, (0, i * (h + border)), pic)
    return des


def normalize_str(string) -> str:
    """
    规范化unicode字符串 并 转为小写 并 转为简体
    """
    string = unicodedata.normalize('NFKC', string)
    string = string.lower()
    string = zhconv.convert(string, 'zh-hans')
    return string


MONTH_NAME = ('睦月', '如月', '弥生', '卯月', '皐月', '水無月',
              '文月', '葉月', '長月', '神無月', '霜月', '師走')


def month_name(x: int) -> str:
    return MONTH_NAME[x - 1]


DATE_NAME = (
    '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
    '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
    '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十',
    '卅一'
)


def date_name(x:int) -> str:
    return DATE_NAME[x - 1]


NUM_NAME = (
    '〇〇', '〇一', '〇二', '〇三', '〇四', '〇五', '〇六', '〇七', '〇八', '〇九',
    '一〇', '一一', '一二', '一三', '一四', '一五', '一六', '一七', '一八', '一九',
    '二〇', '二一', '二二', '二三', '二四', '二五', '二六', '二七', '二八', '二九',
    '三〇', '三一', '三二', '三三', '三四', '三五', '三六', '三七', '三八', '三九',
    '四〇', '四一', '四二', '四三', '四四', '四五', '四六', '四七', '四八', '四九',
    '五〇', '五一', '五二', '五三', '五四', '五五', '五六', '五七', '五八', '五九',
    '六〇', '六一', '六二', '六三', '六四', '六五', '六六', '六七', '六八', '六九',
    '七〇', '七一', '七二', '七三', '七四', '七五', '七六', '七七', '七八', '七九',
    '八〇', '八一', '八二', '八三', '八四', '八五', '八六', '八七', '八八', '八九',
    '九〇', '九一', '九二', '九三', '九四', '九五', '九六', '九七', '九八', '九九',
)


def time_name(hh: int, mm: int) -> str:
    return NUM_NAME[hh] + NUM_NAME[mm]


class FreqLimiter:
    def __init__(self, default_cd_seconds):
        self.next_time = defaultdict(float)
        self.default_cd = default_cd_seconds

    def check(self, key) -> bool:
        return bool(time.time() >= self.next_time[key])

    def start_cd(self, key, cd_time=0):
        self.next_time[key] = time.time() + (cd_time if cd_time > 0 else self.default_cd)

    def left_time(self, key) -> float:
        return self.next_time[key] - time.time()
                                            

class DailyNumberLimiter:
    tz = pytz.timezone('Asia/Shanghai')
    
    def __init__(self, max_num=0):
        self.today = -1
        self.count = defaultdict(int)
        self.max = None if max_num == 0 else max_num

    def check(self, key, max_num=0) -> bool:
        now = datetime.now(self.tz)
        day = (now - timedelta(hours=5)).day
        if day != self.today:
            self.today = day
            self.count.clear()
        if max_num == 0:
            return bool(self.count[key] < self.max)
        else:
            return bool(self.count[key] < max_num)

    def get_num(self, key):
        return self.count[key]

    def increase(self, key, num=1):
        self.count[key] += num

    def reset(self, key):
        self.count[key] = 0


class EcoopShop:
    tz = pytz.timezone('Asia/Shanghai')

    def __init__(self):
        self.today = -1
        self.count = defaultdict(int)

    def check(self):
        now = datetime.now(self.tz)
        day = (now - timedelta(hours=5)).day
        if day != self.today:
            self.today = day
            self.count.clear()

    def get_num(self, key):
        self.check()
        return self.count[key]

    def increase(self, key, num=1):
        self.check()
        self.count[key] += num

    def decrease(self, key, num=1):
        self.check()
        self.count[key] -= num

    def reset(self, key):
        self.count[key] = 0


from .textfilter.filter import DFAFilter

gfw = DFAFilter()
gfw.parse(os.path.join(os.path.dirname(__file__), 'textfilter/sensitive_words.txt'))


def filt_message(message: Union[Message, str]):
    if isinstance(message, str):
        return gfw.filter(message)
    elif isinstance(message, Message):
        for seg in message:
            if seg.type == 'text':
                seg.data['text'] = gfw.filter(seg.data.get('text', ''))
        return message
    else:
        raise TypeError
