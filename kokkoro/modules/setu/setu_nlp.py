import json
import re

import httpx
import nonebot

from kokkoro.configs.setu import baidu_nlp_api_id, baidu_nlp_api_key


async def setu_msg_nlp(msg: str):
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials' \
           f'&client_id={baidu_nlp_api_id}&client_secret={baidu_nlp_api_key}'

    async with httpx.AsyncClient() as client:
        re1 = await client.get(host)
        if re1:
            a_token = re1.json()['access_token']

    bdurl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?charset=UTF-8&access_token=' + a_token

    headers = {
        'Content-Type': 'application/json'
    }

    body = {
        'text': msg
    }

    async with httpx.AsyncClient() as client:
        re2 = await client.post(bdurl, headers=headers, data=json.dumps(body))

    res = json.loads(re2.text)
    adv = search_adv(res['items'], ['ur'])
    if not adv:
        adv = search_adv(res['items'], ['a'])
    if adv and adv == '色':
        adv = None
    if not adv:
        adv = search_adv(res['items'], ['n', 'nw', 'nt'])
    if adv and adv in ['色图', 'setu', '涩图', '色']:
        return None
    return adv


def search_adv(res, word_list):
    for word in res:
        if word['pos'] in word_list:
            return word['item']
    return None


def setu_nlp_test(msg: str, mode: int):
    pattern = '来[点丶份张幅](.*?)的?([色瑟涩😍🐍]|se)([图圖🤮]|tu)'if mode == 1 else '(.*?)的?([色瑟涩😍🐍]|se)([图圖🤮]|tu)'
    info = re.search(pattern, msg)
    return info[1] if info else None


