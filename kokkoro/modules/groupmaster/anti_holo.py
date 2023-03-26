from nonebot.plugin import on_keyword
from kokkoro import Bot
from kokkoro.typing import CQEvent, Message, T_State

SB_HOLO = '''
Hololive hololive ホロ 木口 术口
时乃空 ときのそら Tokino 空妈
萝卜子 ロボ子さん Roboko 大根子
樱巫女 さくらみこ Sakura Miko 樱火龙 elite工厂厂长 黄油精英巫女 赌鬼巫女 樱污女
星街彗星 星街 すいせい Hoshimati Suisei suisui 有点神经病的蓝发大姐姐 有点大姐姐的蓝发神经病
夜空梅露 夜空メル Yozora Mel 梅露 梅球王 Banpire 清楚系天才美少女吸血鬼
夏色祭 まつり Natsuiro Matsuri 马自立 祭妹 夏半首
赤井心 赤井はあと Akai Haato 心大人 はぁちゃま 哈恰玛 哈恰嘛
亚绮 罗森塔尔 アキ ローゼンタール Aki Rosenthal akirose 力速双A弱精灵
白上吹雪 白上フブキ Shirakami Fubuki 🌽 fbk 屑狐狸 喵喵狐 debuki 赫鲁晓狐 工具狐
人见酷丽丝 人見クリス Hitomi Kurisu
凑阿库娅 湊あくあ Minato Aqua aqua 阿夸 夸哥 夸神 山田赫敏 大亏哥 桐谷夸人 
紫咲诗音 紫咲シオン Murasaki 诗音 傻紫 紫咲紫苑
百鬼绫目 百鬼あやめ Nakiri Ayame
愈月巧可 癒月ちょこ Yuzuki Choco 巧可老师
大空昴 大空スバル Ōzora Subaru 
大神澪 大神ミオ Ōkami Mio mio 大神三才 三才妈妈
猫又小粥 猫又おかゆ Nekomata Okayu 汤哥 饭团猫 大脸猫
戌神 沁音 戌神ころね Inugami Korone 吼啦迷迭吼啦哟 外神
兔田佩克拉 兎田ぺこら Usada Pekora 
润羽露西娅 潤羽るしあ Uruha Rushia 绿粽子 三亚王 狂爆粽子 阿马粽
不知火芙蕾雅 不知火フレア Shiranui Flare 芙碳 ぬいぬい nuinui フーたん
白银诺艾尔 白銀ノエル Shirogane Noel 
宝钟 玛琳 宝鐘マリン Houshou Marine 无船承运人 山贼
天音彼方 天音かなた Amane Kanata 彼方碳 かなたん PP天使 天音腾格尔
桐生可可 桐生 ココ Kiryū Kiryuu Coco 虫皇 龙皇 憨憨龙 ass龙 宝批龙 西成女王
角卷绵芽 角巻わため Tsunomaki Watame wtm 顶顶羊 咚咚羊 畜生羊 木口锤石
常暗永远 常闇トワ Tokoyami Towa 永远大人 トワ様
姬森璐娜 姫森 ルーナ Himemori Luuna 璐娜 英语教师
雪花菈米 雪花ラミィYukihana Lamy 菈米 菈米妈妈
桃铃音音 桃鈴ねね Momosuzu Nene 铃桃音音
狮白牡丹 獅白ぼたん Shishiro Botan
魔乃阿萝耶 魔乃アロエ Mano Aloe 魔乃 阿萝耶
尾丸波尔卡 尾丸ポルカ Omaru Polka 特质系西索
AZKi AZiK
Ayunda Risu 栗鼠 印尼面包狗 猫狗的女儿
Moona Hoshinova
Airani Iofifteen
噶呜 古拉 Gawr Gura がうる ぐら
一伊那尔栖 Ninomae Ina'nis 一伊那尓栖
森美声 Mori Calliope 巨乳版露西娅 巨乳露西娅
小鸟游琪亚拉 Takanashi Kiara 小鳥遊キアラ 琪亚拉
阿米莉亚 Watson Amelia ワトソン アメリア
友人A YuujinA
谷乡元昭 YAGOO yagoo 谷郷元昭 Tanigou Motoaki
'''.split()


anti_holo = on_keyword(keywords=set(SB_HOLO), priority=2)


@anti_holo.handle()
async def handle_anti_holo(bot: Bot, event: CQEvent, state: T_State):
    await bot.send(event, Message('Vtuber天狗爪巴！'))
