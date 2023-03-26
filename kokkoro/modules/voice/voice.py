import base64
import os
from io import BytesIO
from typing import List

from PIL import Image, ImageDraw, ImageFont
from nonebot.exception import FinishedException

from kokkoro import Service, Bot
from kokkoro.typing import MessageSegment, T_State, MessageEvent
from .create_img import image_draw
from .getvoice import voiceApi, GenshinAPI, XcwAPI, Error, chinese2katakana, getvoice
from .youdaotranslate import translate

sv_help = '''
中日语音合成
[/柚子 常轨脱离 缘之空 美少女万华镜 galgame]+[中配 日配]+[角色id]+[文本]
（中配将中文翻译为片假名，日配翻译为日语，日配会输出翻译内容供检查）
不填默id认为0，加号替换为空格
例：/柚子 日配 0 我爱宁宁 
/柚子 中配 我爱宁宁 
/柚子 日配 私は綾地寧々を愛している（应该是这样，日语不好）
特殊：
/xcw 日配 日语/中文（自动翻译）
/xcw 中配 中文
/派蒙 中配 中文（更新到鹿野院平藏）
[/角色id列表]查看支持角色和分类
[/语音合成帮助]查看语音合成帮助
'''.strip()

speaker_dict = {
    '柚子': ["綾地寧々", "因幡めぐる", "朝武芳乃", "常陸茉子", "ムラサメ", "鞍馬小春", "在原七海", "四季ナツメ", "明月栞那", "墨染希", "火打谷愛衣", "汐山涼音"],
    '常轨脱离': ["和泉妃愛", "常盤華乃", "錦あすみ", "鎌倉詩桜", "竜閑天梨", "和泉里", "新川広夢", "聖莉々子"],
    '缘之空': ["春日野穹", "天女目瑛", "依媛奈緒", "渚一葉"],
    '美少女万華鏡': ["蓮華", "篝ノ霧枝", "沢渡雫", "亜璃子", "灯露椎", "覡夕莉"],
    'galgame': ["鷹倉杏璃", "鷹倉杏鈴", "アペイリア", "倉科明日香", "ATRI", "アイラ", "新堂彩音", "姫野星奏", "小鞠ゆい", "聖代橋氷織", "有坂真白", "白咲美絵瑠", "二階堂真紅"]
}

XCW = ['xcw', '小仓唯', '镜华']

genshin = ['派蒙', '凯亚', '安柏', '丽莎', '琴', '香菱', '枫原万叶', '迪卢克', '温迪', '可莉', '早柚', '托马', '芭芭拉',
           '优菈', '云堇', '钟离', '魈', '凝光', '雷电将军', '北斗', '甘雨', '七七', '刻晴', '神里绫华', '雷泽', '神里绫人',
           '罗莎莉亚', '阿贝多', '八重神子', '宵宫', '荒泷一斗', '九条裟罗', '夜兰', '珊瑚宫心海', '五郎', '达达利亚', '莫娜',
           '班尼特', '申鹤', '行秋', '烟绯', '久岐忍', '辛焱', '砂糖', '胡桃', '重云', '菲谢尔', '诺艾尔', '迪奥娜', '鹿野院平藏']

speaker_id = '''
类别:==柚子===========常轨脱离=======缘之空=========
id: 0： 绫地宁宁   |0：和泉妃爱   |0：春日野穹     
    1： 因幡爱瑠   |1：常磐华乃   |1：天女目瑛    
    2： 朝武芳乃   |2：锦亚澄     |2：依媛奈绪    
    3： 常陸茉子   |3：镰仓诗樱   |3：渚一叶       
    4： 丛雨       |4：龙闲天梨   |               
    5： 鞍马小春   |5：和泉里     |== 美少女万華鏡==
    6： 在原七海   |6：新川广梦   |0：莲华         
    7： 四季夏目   |7：圣莉莉子   |1：篝之雾枝    
    8： 明月栞那   |              |2：沢渡雫       
    9： 墨染希     |              |3：亚璃子      
    10：火打谷爱衣 |              |4：灯露椎       
    11：汐山凉音   |              |5：覡夕莉      
类别:==galgame====================================            
id: 0： 鹰仓杏璃   《Clover Day's》
    1： 鹰仓杏铃   《Clover Day's》
    2： 艾佩莉娅   《景之海的艾佩莉娅》
    3： 仓科明日香 《苍之彼方的四重奏》
    4： ATRI       《ATRI》 
    5： 艾拉       《可塑性记忆》 
    6： 新堂彩音   《想要传达给你的爱恋》
    7： 姫野星奏   《想要传达给你的爱恋》
    8： 小鞠由依   《想要传达给你的爱恋》
    9： 圣代桥冰织 《糖调！-sugarfull tempering-》
    10：有坂真白   《苍之彼方的四重奏》
    11：白咲美绘瑠 《与你相恋的恋爱Recette》
    12：二阶堂真红 《五彩斑斓的世界》
'''.strip()


def get_speakers(choose, num=0):
    if choose == '常轨脱离':
        speakers, model = speaker_dict["常轨脱离"][num], 5
    elif choose == '缘之空':
        speakers, model = speaker_dict["缘之空"][num], 13
    elif choose == '美少女万華鏡':
        speakers, model = speaker_dict["美少女万華鏡"][num], 17
    elif choose == "galgame":
        speakers, model = speaker_dict["galgame"][num], 29
    else:
        speakers = speaker_dict["柚子"][num]
        if num >= 7:
            model = 9
        else:
            model = 1
    return speakers, model


sv = Service(name='voice', help_=sv_help, bundle='通用')

voice1 = sv.on_fullmatch('柚子', aliases={i for i in speaker_dict.keys()}.union(
    {i for i in speaker_dict.keys()}
), only_group=False)


@voice1.handle()
async def voice1_handle(bot: Bot, event: MessageEvent, state: T_State):
    content = event.raw_message.split(' ')
    if len(content) == 3 or len(content) == 4:
        if content[1] == '中配':
            text_chjp = await chinese2katakana(content[2] if len(content) == 3 else content[3])
        elif content[1] == '日配':
            text_chjp = await translate(content[2] if len(content) == 3 else content[3])
        else:
            await voice1.finish('格式错误，请重发！')
        speaker, model = get_speakers(content[0][1:], num=int(content[2]) if content[2].isdigit() else 0)
        voice_s = getvoice(speaker, model)
    else:
        await voice1.finish('格式错误，请重发！')

    try:
        voice = await voice_s.gethash(text_chjp)
        final_send = MessageSegment.record(voice)
        await voice1.finish(final_send)
    except FinishedException:
        pass
    except:
        await voice1.finish('生成失败，红豆泥斯密马赛~')


voice2 = sv.on_fullmatch('xcw', aliases={i for i in XCW}.union({i for i in genshin}), only_group=False)


@voice2.handle()
async def voice2_handle(bot: Bot, event: MessageEvent, state: T_State):
    try:
        content: List[str] = event.raw_message.split(' ')
        if len(content) == 3:
            if content[1] == '中配':
                if content[0][1:] in XCW:
                    text = await chinese2katakana(content[2])
                    voice = await voiceApi(XcwAPI + text)
                else:
                    text = replace_text(content[2])
                    voice = await voiceApi(GenshinAPI, {'speaker': content[0][1:], 'text': text, 'length': 1.0})
            elif content[1] == '日配':
                text = await translate(content[2])
                voice = await voiceApi(XcwAPI + text)
            else:
                await voice2.finish('格式错误，请重发！')
        else:
            await voice2.finish('格式错误，请重发！')
    except Error as e:
        data = f'发生错误：{e.error}'
        sv.logger.error(data)
    except Exception as e:
        data = f'发生错误：{e}'
        sv.logger.error(data)

    data = MessageSegment.record(voice)
    await voice2.finish(data)


voice_list = sv.on_fullmatch('角色id列表', only_group=False)


@voice_list.handle()
async def speaker_list(bot: Bot, event: MessageEvent, state: T_State):
    img = image_draw(speaker_id)
    await voice_list.finish(MessageSegment.image(file=img))

voice_help = sv.on_fullmatch('语音合成帮助', only_group=False)


@voice_help.handle()
async def help_handle(bot: Bot, event: MessageEvent, state: T_State):
    image = Image.open(os.path.join(os.path.dirname(__file__), f"help.jpg"))
    draw = ImageDraw.Draw(image)  # 建立一个绘图的对象
    font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), f"SIMYOU.ttf"), 40)
    font2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), f"SIMYOU.ttf"), 30)
    text1 = speaker_id
    text = ''
    textcn = ''
    textxcw = '[小仓唯/镜华]指令:/小仓唯[中配/日配] 文本,如/小仓唯 日配 你好'
    text2 = '以下角色无需填写类别,指令/[名字][中配(无日配)] 文本,如/派蒙 中配 你好'
    for prime in genshin:
        text3 = text
        text += prime + " "
        if len(text) > 30:
            if len(text) < 33:
                textcn += text + '\n'
                text = ''
            else:
                textcn += text3 + '\n'
                text = ''
                text += prime + " "
    textcn += text + '\n'
    draw.text((84, 827), text1, font=font, fill="#2e59a7")
    draw.text((84, 2080), textxcw, font=font2, fill="#531dab")
    draw.text((84, 2120), text2, font=font2, fill="#531dab")
    draw.text((84, 2160), textcn, font=font, fill="#2e59a7")

    img_buf = BytesIO()

    image.save(img_buf, format='BMP')
    base64_str = base64.b64encode(img_buf.getvalue()).decode('ascii')
    image_text = 'base64://' + base64_str
    await voice_help.finish(MessageSegment.image(file=image_text))


Genshin_list = (
    (',', '，'), ('.', '。'), ('!', '！'), ('?', '？'), (':', '：'), ('(', '（'), ('<', '《'), ('>', '》'), ('0', '零'), ('1', '一'), ('2', '二'), ('3', '三'), ('4', '四'),
    ('5', '五'), ('6', '六'), ('7', '七'), ('8', '八'), ('9', '九'),)


def replace_text(text):
    for en, cn in Genshin_list:
        text = text.replace(en, cn)
    print(text)
    return text
