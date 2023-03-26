from kokkoro import aiohttpx
from lxml.html import fromstring
import urllib.parse


async def get_pic_ascii(image_url: str):
    ascii2d_url = f'https://ascii2d.net/search/url/' + image_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    }

    re1 = await aiohttpx.get(ascii2d_url, headers=headers, follow_redirects=True, timeout=(3.05, 6.05))
    html1 = re1.text
    image_data1 = [each for each in parse_html(html1)]

    ascii2d_url2 = str(re1.url).replace('color', 'bovw')
    re2 = await aiohttpx.get(ascii2d_url2, headers=headers, follow_redirects=True, timeout=(3.05, 6.05))
    html2 = re2.text
    image_data2 = [each for each in parse_html(html2)]
    return image_data1, image_data2


def parse_html(html):
    selector = fromstring(html)
    for tag in selector.xpath('//div[@class="container"]/div[@class="row"]/div/div[@class="row item-box"]')[1:6]:
        if pic_url := tag.xpath('./div/img/@src'):  # 缩略图url
            pic_url = urllib.parse.urljoin("https://ascii2d.net/", pic_url[0])
        if description := tag.xpath('./div/div/h6/a[1]/text()'):  # 名字
            description = description[0]
        if author := tag.xpath('./div/div/h6/a[2]/text()'):  # 作者
            author = author[0]
        if origin_url := tag.xpath('./div/div/h6/a[1]/@href'):  # 原图地址
            origin_url = origin_url[0]
        if author_url := tag.xpath('./div/div/h6/a[2]/@href'):  # 作者地址
            author_url = author_url[0]
        if pttype := tag.xpath('./div/div/h6/small/text()'):
            pttype = pttype[0].replace('\n', '')
        yield pic_url, description, author, origin_url, author_url, pttype

