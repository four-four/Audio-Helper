import requests
import sys
import wget
import parsel
import ssl
import execjs
import argparse
ssl._create_default_https_context = ssl._create_unverified_context

'''
https://blog.csdn.net/travel_Capsule/article/details/90312545?utm_medium=distribute.pc_relevant_download.none-task-blog-blogcommendfrombaidu-4.nonecase&depth_1-utm_source=distribute.pc_relevant_download.none-task-blog-blogcommendfrombaidu-4.nonecas
'''


curl_url = 'https://www.ximalaya.com/revision/play/v1/audio?id=%s&ptype=1'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
           'Host': 'www.ximalaya.com'}

def getxmtime():
    url = "https://www.ximalaya.com/revision/time"
    response = requests.get(url, headers=headers)
    html = response.text
    return html

def exec_js():
    time = getxmtime()

    with open('xmSign.js', encoding='utf-8') as f:
        js = f.read()

    docjs = execjs.compile(js)

    res = docjs.call('python', time)
    print(res)
    return res

def first_curl(id, name):
    sign = exec_js()
    headers['xm-sign'] = sign
    print(headers)
    url = curl_url % str(id)
    wget_url = None
    print(url)

    res = requests.get(url, headers=headers).json()
    try:
        wget_url = res['data']['src']
    except Exception as e:
        print('curl %s failed!: %s' %(name, str(e)))
    return wget_url

def second_wget(url, name):
    wget.download(url, out=name)


def get_total_page(page_url):
    response = requests.get(page_url, headers = headers)
    #获取页面html的内容
    sel = parsel.Selector(response.text)
    #通过css选择器找到a标签   .sound-list代表 class属性为sound-list 然后下面的ul 下的li 下的a
    sound_list = sel.css('.sound-list ul li a')
    #只有前30个是页面链接 截取前30个
    for sound in sound_list[:30]:
        #extract_first()将对象中的文字提取出来
        #获取a标签的href属性的内容
        media_url = sound.css('a::attr(href)').extract_first()
        #/youshengshu/16411402/98791745 --只去最后面的id
        media_url = media_url.split('/')[-1]
        # 获取a标签的title属性的内容
        media_name = sound.css('a::attr(title)').extract_first()
        #用yield将整个循环的内容返回
        print(media_url)
        print(media_name)
        yield media_url,media_name


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("album", help="album id")
    parser.add_argument("-p", "--page", help="total pages, default=1")
    args = parser.parse_args()

    album_id = args.album
    total_pages = 1
    if args.page:
        total_pages = int(args.page)
    url = 'https://www.ximalaya.com/ertong/%s/' % album_id
    for page in range(1, total_pages + 1):
        page_url = url
        if page > 1:
            page_url = page_url + 'p' + str(page)
        
        meidas = get_total_page(page_url)
        for id,name in meidas:
            target_name = name + '.m4a'
            get_url = first_curl(id, name)
            second_wget(get_url, target_name)
