from kokkoro import Service, Bot
from kokkoro.typing import MessageEvent
from .qiu_qiu_translation import qiu_qiu_word_translation, qiu_qiu_phrase_translation

sv_help = '''
[/丘丘一下 丘丘语句] 翻译丘丘语,注意这个翻译只能把丘丘语翻译成中文，不能反向
[/丘丘词典 丘丘语句] 查询丘丘语句的单词含义
'''.strip()


sv = Service("qiuqiu-translator", bundle="原神相关", help_=sv_help)

suffix = "\n※ 这个插件只能从丘丘语翻译为中文，不能反向翻译\n※ 发送词语时请注意空格位置是否正确，词语不区分大小写，不要加入任何标点符号\n" \
         "※ 翻译数据来源于 米游社论坛 https://bbs.mihoyo.com/ys/article/2286805 \n※ 如果你有更好的翻译欢迎来提出 issues"

qiuqiu = sv.on_fullmatch("丘丘一下", only_group=False)
qiuqiu_dict = sv.on_fullmatch("丘丘词典", only_group=False)


@qiuqiu.handle()
async def qiuqiu_handle(bot: Bot, event:MessageEvent):
    txt = event.message.extract_plain_text().strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_word_translation(txt)
    mes += suffix
    await qiuqiu.finish(mes)


@qiuqiu_dict.handle()
async def qiuqiu_dict_handle(bot: Bot, event: MessageEvent):
    txt = event.message.extract_plain_text().strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_phrase_translation(txt)
    mes += suffix
    await qiuqiu_dict.finish(mes)
