import json
import random

from nonebot.adapters.cqhttp import MessageSegment
from kokkoro import aiohttpx
from kokkoro.configs.setu import apikey, size1200
from kokkoro.util import get_setu_from_url


async def get_setu(keyword: str):
    j = random.randint(1, 2)

    if url_api1 := await get_setu_from_api(keyword, j):
        return await get_setu_from_url(url_api1)
    elif url_api2 := await get_setu_from_api(keyword, 3 - j):
        return await get_setu_from_url(url_api2)
    elif keyword == 'random':
        return 'setuapi炸了，请稍后再试'
    else:
        return await get_setu('random')


async def get_setu_from_api(keyword: str, api_num):
    if api_num == 1:
        setu_url = f'https://api.lolicon.app/setu/v2?size=original&size=regular'
        if not keyword == 'random':
            setu_url = f'https://api.lolicon.app/setu/v2?size=original&size=regular&tag=' + keyword

        r = await aiohttpx.get(setu_url, timeout=(3.05, 6.05))

        re = json.loads(r.text)
        if re['data']:
            if size1200:
                return re['data'][0]['urls']['regular'].replace("i.pixiv.re", "pixiv.azuka.cf")  # .replace("_webp", "")
            else:
                return re['data'][0]['urls']['original'].replace("i.pixiv.re", "pixiv.azuka.cf")
        else:
            return False

    elif api_num == 2:
        setu_url = f'http://setu.yuban10703.xyz/setu?level=1'
        if not keyword == 'random':
            setu_url = f'http://setu.yuban10703.xyz/setu?tags={keyword}'

        r = await aiohttpx.get(setu_url, follow_redirects=True)
        if r.status_code == 200:
            re = json.loads(r.text)
            if size1200:
                return re['data'][0]['urls']['large'].replace("i.pximg.net", "pixiv.azuka.cf")  # .replace("_webp", "")
            else:
                return re['data'][0]['urls']['original'].replace("i.pximg.net", "pixiv.azuka.cf")
        else:
            return False

