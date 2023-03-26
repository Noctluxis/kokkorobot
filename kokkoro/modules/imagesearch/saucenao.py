from kokkoro import aiohttpx
from lxml.html import fromstring


async def get_pic_sn(image_url: str):
    saucenao_url = 'https://saucenao.com/search.php'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    my_data = {
        'file': '(binary)',
        'url': image_url,
        'frame': '1',
        'hide': '0',
        'database': '999'
    }

    res = await aiohttpx.post(saucenao_url, headers=headers, data=my_data, timeout=(3.05, 6.05))
    html = res.text

    image_data = sorted([each for each in parse_html(html)], key=lambda image_data: image_data[1], reverse=True)
    return image_data


def parse_html(html):
    selector = fromstring(html)
    for tag in selector.xpath('//div[@class="result"]/table'):
        pic_url = tag.xpath('./tr/td/div/a/img/@src')
        if pic_url:
            pic_url = pic_url[0]
        elif pic_url := tag.xpath('./tr/td/div/div/a/img/@data-src2'):
            pic_url = pic_url[0]
        elif pic_url := tag.xpath('./tr/td/div/div/a/img/@src'):
            pic_url = pic_url[0]
        else:
            pic_url = None
        similarity = tag.xpath(
            './tr/td[@class="resulttablecontent"]/div[@class="resultmatchinfo"]/div[@class="resultsimilarityinfo"]/text()')
        if similarity:
            similarity = float(similarity[0].replace('%', ''))
        else:
            similarity = "没有写"  # 相似度
        title = tag.xpath(
            './tr/td[@class="resulttablecontent"]/div[@class="resultcontent"]/div[@class="resulttitle"]')
        if title:
            title = title[0].xpath('string(.)').strip()
        else:
            title = "没有写"  # 标题
        content = tag.xpath(
            './tr/td[@class="resulttablecontent"]/div[@class="resultcontent"]/div[@class="resultcontentcolumn"]')
        if content:
            content = content[0].xpath('string(.)').strip()
        else:
            content = "没有说"  # 内容
        yield pic_url, similarity, title, content
