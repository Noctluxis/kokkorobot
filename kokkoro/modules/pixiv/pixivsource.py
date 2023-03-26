from .pixivapi import PixivApi

pixivapi = PixivApi()
pixivapi.login()


async def get_pixiv(msg: str):
    if msg.isdigit():
        json_detail = pixivapi.get_detail(int(msg))
        text = f'作品名：{json_detail.illust.title}\n' \
               f'作者：{json_detail.illust.user.name}@{json_detail.illust.user.account}\n' \
               f'上传时间：{json_detail.illust.create_date}\n' \
               f'收藏数：{json_detail.illust.total_bookmarks}\n' \
               f'简介：{json_detail.illust.caption}\n'
        texts = await pixivapi.get_image(json_detail, original=True)
        texts.insert(0, text)
        return texts
    elif msg == 'main':
        return await pixivapi.get_main()
    elif msg == 'new':
        return await pixivapi.get_new()
    elif msg == 'rank':
        return await pixivapi.get_rank()
    elif msg == 'rankw':
        return await pixivapi.get_rank('week')
    elif msg == 'rankd':
        return await pixivapi.get_rank('day')
    elif msg == 'mark':
        return await pixivapi.get_mark()
    else:
        return await pixivapi.get_search(msg)
