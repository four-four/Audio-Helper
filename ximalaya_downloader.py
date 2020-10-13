import requests
import re
import sys
import os
import wget
import parsel
import ssl
import execjs
import argparse
from converter import Converter

ssl._create_default_https_context = ssl._create_unverified_context


class Ximalaya_Downloader(object):

    TIME_URL = "https://www.ximalaya.com/revision/time"
    AUDIO_URL = 'https://www.ximalaya.com/revision/play/v1/audio?id=%s&ptype=1'
    ALBUM_URL = 'https://www.ximalaya.com/ertong/%s/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
           'Host': 'www.ximalaya.com'}

    def __init__(self):
        pass

    def getxmtime(self):
        response = requests.get(self.TIME_URL, headers=self.headers)
        html = response.text
        return html

    def exec_js(self):
        time = self.getxmtime()
        with open('xmSign.js', encoding='utf-8') as f:
            js = f.read()

        docjs = execjs.compile(js)
        res = docjs.call('python', time)
        return res

    def first_curl(self, id, name):
        sign = self.exec_js()
        self.headers['xm-sign'] = sign
        url = self.AUDIO_URL % str(id)
        wget_url = None
        print(url)

        res = requests.get(url, headers=self.headers).json()
        try:
            wget_url = res['data']['src']
        except Exception as e:
            print('curl %s failed!: %s' %(name, str(e)))
        return wget_url

    def second_wget(self, url, name):
        wget.download(url, out=name)

    def get_total_page(self, page_url):
        response = requests.get(page_url, headers = self.headers)
        sel = parsel.Selector(response.text)
        sound_list = sel.css('.sound-list ul li a')
        for sound in sound_list[:30]:
            media_url = sound.css('a::attr(href)').extract_first()
            media_url = media_url.split('/')[-1]
            media_name = sound.css('a::attr(title)').extract_first()
            print(media_url)
            print(media_name)
            yield media_url,media_name

    def download(self, album_id, total_pages, out_path):
        url = self.ALBUM_URL % album_id
        for page in range(1, total_pages + 1):
            page_url = url
            if page > 1:
                page_url = page_url + 'p' + str(page)
            
            meidas = self.get_total_page(page_url)
            for id, name in meidas:
                if not name:
                    continue

                target_name = re.sub(r' +', '_', name) + '.m4a'
                get_url = self.first_curl(id, name)
                self.second_wget(get_url, out_path + '/' + target_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("album", help="album id")
    parser.add_argument("-p", "--page", help="total pages, default=1")
    parser.add_argument("outpath", help="dest path")
    args = parser.parse_args()

    album_id = args.album
    out_path = args.outpath
    total_pages = 1
    if args.page:
        total_pages = int(args.page)
    dl = Ximalaya_Downloader()
    dl.download(album_id, total_pages, out_path)
    cv = Converter()
    cv.m4aTomp3(out_path + '/')