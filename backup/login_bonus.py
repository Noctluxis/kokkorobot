import random
from kokkoro import Service, R, Bot
from kokkoro.typing import CQEvent, Message, GroupMessageEvent, PrivateMessageEvent
from kokkoro.util import DailyNumberLimiter, ecoop
from kokkoro.util.ecoop import Ecoop


sv = Service('pcr-login-bonus', bundle='通用', help_='[签到] 给主さま盖章章')

lmt = DailyNumberLimiter(1)
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

login = sv.on_fullmatch('签到', aliases={'盖章'}, only_group=False)


@login.handle()
async def give_okodokai(bot: Bot, event: CQEvent):
    uid = event.user_id
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info.get('nickname', '未知用户')
    if not lmt.check(uid):
        if isinstance(event, GroupMessageEvent):
            await login.finish(f'>{nickname}\n明日はもう一つプレゼントをご用意してお待ちしますね')
        elif isinstance(event, PrivateMessageEvent):
            await login.finish('明日はもう一つプレゼントをご用意してお待ちしますね')

    lmt.increase(uid)
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
    pic = Message(R.img("priconne/kokkoro_stamp.png").cqcode)
    msg = f'おかえりなさいませ、主さま' + pic + f'\n{eco_num_r}金币を獲得しました\n私からのプレゼントです\n主人今天要{todo}吗？'
    if isinstance(event, GroupMessageEvent):
        msg = f'>{nickname}\n' + msg + '\n' + msg_coop_level
    elif isinstance(event, PrivateMessageEvent):
        msg = msg + '\n' + msg_coop_level
    await login.finish(msg)


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
