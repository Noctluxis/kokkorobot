import os
import random

from kokkoro import R, Service, priv
from kokkoro.util import MessageSegment, FreqLimiter
from kokkoro.typing import MessageEvent

CD_NOTICE = '技能冷却中...'
_flmt = FreqLimiter(3)

sv_help = '''
[/xcw骂我]满足变态的欲望
'''.strip()

sv = Service('xcw', help_=sv_help, bundle='通用')
xcw_folder = R.get('record/xcw/').path

xcw = sv.on_fullmatch('xcw骂我', aliases={'小仓唯骂我'}, only_group=False)


def get_xcw():
    files = os.listdir(xcw_folder)
    filename = random.choice(files)
    rec = R.get('record/xcw/', filename)
    return rec


@xcw.handle()
async def xcw_handle(bot, event: MessageEvent):
    uid = event.user_id
    if not _flmt.check(uid):
        await xcw.finish(CD_NOTICE)
    file = get_xcw()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await xcw.send(rec)
        return
    except:
        sv.logger.error("发送失败")
