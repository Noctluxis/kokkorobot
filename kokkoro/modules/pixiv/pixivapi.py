import json
import random

from pixivpy3 import ByPassSniApi
from kokkoro.util import get_setu_from_url


class PixivApi:

    def __init__(self):
        self.latest_list = []
        self.api = ByPassSniApi()
        self.access_token = ''
        self.refresh_token = ''
        self.set_token()
        if not self.api.require_appapi_hosts(hostname="public-api.secure.pixiv.net"):
            self.api.hosts = 'https://210.140.92.180'
        # self.api.set_additional_headers({'Accept-Language': 'en-US'})
        self.api.set_accept_language('en-us')
        self.login()
        self.get_follow_list()

    def set_token(self):
        token_dir = './data/pixiv_token.json'
        with open(token_dir, 'r', encoding='utf8') as fp:
            tokens = json.load(fp)
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']
        return True

    def login(self):
        return self.api.auth(refresh_token=self.refresh_token)

    def get_detail(self, illust_id: int):
        json_detail = self.api.illust_detail(illust_id)
        if json_detail.get('error'):
            return '没有这个作品哦'
        return json_detail

    @staticmethod
    async def get_image(json_re, original=False) -> list[any]:
        if json_re.illust:
            illust_info = json_re.illust
        else:
            illust_info = json_re.illusts[random.randint(0, len(json_re.illusts) - 1)]

        if not illust_info.meta_pages:
            img_url = illust_info.meta_single_page.original_image_url if original \
                else illust_info.image_urls.large
            img_url = img_url.replace('i.pximg.net', 'pixiv.azuka.cf')
            # img.vpixiv.net
            # i.pixiv.re
            return [await get_setu_from_url(img_url, original=original)]
        else:
            illust_list = []
            for i in illust_info.meta_pages:
                img_url = i.image_urls.original if original else i.image_urls.large
                img_url = img_url.replace('i.pximg.net', 'pixiv.azuka.cf')
                illust_list.append(await get_setu_from_url(img_url, original=original))
            return illust_list

    async def get_results(self, json_re, func, num: int):
        i = random.randint(1, num)
        if i > 1:
            for j in range(i - 1):
                next_qs = self.api.parse_qs(json_re.next_url)
                json_re = func(**next_qs)
        return await self.get_image(json_re)

    async def get_main(self):
        json_main = self.api.illust_recommended()
        return await self.get_results(json_main, self.api.illust_recommended, 3)

    async def get_new(self):
        json_new = self.api.illust_follow()
        return await self.get_results(json_new, self.api.illust_follow, 3)

    async def get_rank(self, mode: str = 'month'):
        if mode == 'month':
            json_rank = self.api.illust_ranking('month')
        elif mode == 'week':
            json_rank = self.api.illust_ranking('week')
        else:
            json_rank = self.api.illust_ranking('day_male')
        return await self.get_image(json_rank)

    async def get_mark(self):
        json_mark = self.api.user_bookmarks_illust(19637303)
        return await self.get_results(json_mark, self.api.user_bookmarks_illust, 5)

    async def get_search(self, msg: str):
        json_search = self.api.search_illust(msg)
        if len(json_search.illusts) == 0:
            return '找不到您想要的Pixiv作品哦'
        return await self.get_image(json_search)

    def get_follow_list(self):
        json_new = self.api.illust_follow()
        new_latest_list = [illust['id'] for illust in json_new.illusts]
        if sorted(new_latest_list) == sorted(self.latest_list):
            return []
        else:
            diff_list = list(set(new_latest_list).difference(set(self.latest_list)))
            self.latest_list = new_latest_list
            return diff_list
