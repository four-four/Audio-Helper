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
from login import login

session = login()

ssl._create_default_https_context = ssl._create_unverified_context


class Ximalaya_Downloader(object):

    TIME_URL = "https://www.ximalaya.com/revision/time"
    AUDIO_URL = 'https://www.ximalaya.com/revision/play/v1/audio?id=%s&ptype=1'
    ALBUM_URL = 'https://www.ximalaya.com/ertong/%s/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
           'Host': 'www.ximalaya.com',
    }
    def __init__(self):
        pass

    def getxmtime(self):
        response = session.get(self.TIME_URL, headers=self.headers)
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

        res = session.get(url, headers=self.headers).json()
        try:
            wget_url = res['data']['src']
        except Exception as e:
            print('curl %s failed!: %s' %(name, str(e)))
        return wget_url

    def second_wget(self, url, name):
        if 'm4a' not in name:
            name = name + '.m4a'
        print(url)
        print(name)
        wget.download(url, out=name)

    def get_total_page_by_html(self, page_url):
        response = session.get(page_url, headers = self.headers)
        print(response.text)
        sel = parsel.Selector(response.text)
        sound_list = sel.css('.sound-list ul li a')
        for sound in sound_list[:30]:
            media_url = sound.css('a::attr(href)').extract_first()
            media_url = media_url.split('/')[-1]
            media_name = sound.css('a::attr(title)').extract_first()
            print(media_url)
            print(media_name)
            yield media_url,media_name
    
    def download_media(self, media_url, out_path, out_name):
        get_url = self.first_curl(media_url, out_name)
        self.second_wget(get_url, out_path + '/' + out_name)

    def download_favourite(self, total_pages, out_path):
        url = 'https://www.ximalaya.com/revision/my/getLikeTracks'
        self.download_page(url, out_path, itemTrack='tracksList', itemName='trackTitle')
    
    def download_album(self, album_id, total_pages, out_path):
        url = 'https://www.ximalaya.com/revision/album/v1/getTracksList?albumId=%s&pageNum=' % str(album_id)
        for page in range(1, total_pages + 1):
            page_url = url + str(page)
            self.download_page(page_url, out_path)
    
    def download_page(self, url, out_path, itemTrack='tracks', itemName='title'):
        response = session.get(url, headers = self.headers).json()
        media_list = []
        try:
            media_list = response['data'][itemTrack]
        except Exception as e:
            print("Failed to get track list.")
            return
        for media in media_list:
            track_id = media['trackId']
            name = media[itemName]
            target_name = re.sub(r' +|\(|\)|\.', '_', name) + '.m4a'
            get_url = self.first_curl(track_id, name)
            self.second_wget(get_url, out_path + '/' + target_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", help="media id")
    parser.add_argument("-n", "--name", help="media name")
    parser.add_argument("-a", "--album", help="album id")
    parser.add_argument("-p", "--page", help="total pages, default=1")
    parser.add_argument("-f", "--favourite", help="download my favourite")
    parser.add_argument("-u", "--url", help="album url")
    parser.add_argument("outpath", help="dest path")
    args = parser.parse_args()

    dl = Ximalaya_Downloader()
    cv = Converter()
    out_path = args.outpath
    # Download a specific media
    if args.id:
        mediam_id = args.id
        out_name = "temp"
        if args.name:
            out_name = args.name
        dl.download_media(mediam_id, out_path, out_name)
    else:
    # Download an album
        total_pages = 1
        if args.page:
            total_pages = int(args.page)
        if args.album:
            album_id = args.album
            dl.download_album(album_id, total_pages, out_path)
        if args.url:
            dl.download_pages(args.url, total_pages, out_path)
        if args.favourite:
            dl.download_favourite(total_pages, out_path)

    cv.m4aTomp3(out_path + '/')