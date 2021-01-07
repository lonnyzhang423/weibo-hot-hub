import json
import logging
import os
import re
import traceback

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

import util

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)

HOT_SEARCH = "https://s.weibo.com/top/summary?cate=realtimehot"
HOT_TOPIC = "https://s.weibo.com/top/summary?cate=topicband"

retries = Retry(total=2,
                backoff_factor=0.1,
                status_forcelist=[k for k in range(400, 600)])

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
}


def getContent(url: str):
    try:
        with requests.session() as s:
            s.mount("http://", HTTPAdapter(max_retries=retries))
            s.mount("https://", HTTPAdapter(max_retries=retries))
            return s.get(url, headers=headers).text
    except:
        log.error(traceback.format_exc())


def parseSearchList(page: str):
    result = []
    try:
        soup = BeautifulSoup(page)
        ul = soup.select('section.list > ul.list_a > li')
        if ul:
            for li in ul:
                a = li.find('a')
                if a:
                    url = 'https://s.weibo.com{}'.format(a['href'])
                    # 去除热度
                    em = a.select_one('span > em')
                    if em:
                        em.replaceWith('')
                    title = a.find('span').text.strip()
                    result.append({'title': title, 'url': url})
    except:
        log.error(traceback.format_exc())
    return result


def parseTopicList(page: str):
    result = []
    try:
        soup = BeautifulSoup(page)
        ul = soup.select('section.list > ul.list_b > li')
        if ul:
            for li in ul:
                a = li.find('a')
                if a:
                    url = 'https://s.weibo.com{}'.format(a['href'])
                    title = a.select_one('article > h2').text
                    detail = a.select_one('article > p').text
                    if not detail:
                        detail = '暂无数据'
                    info = a.select_one('article > span').text
                    if not info:
                        info = '暂无数据'
                    result.append({'title': title, 'url': url,
                                   'detail': detail, 'info': info})
    except:
        log.error(traceback.format_exc())
    return result


def generateArchiveReadme(searches, topics):
    """生成归档readme
    """
    def search(item):
        return '1. [{}]({})'.format(item['title'], item['url'])

    def topic(item):
        return '1. [{}]({})\n    - {}\n    - {}'.format(item['title'], item['url'], item['detail'], item['info'])

    searchList = '暂无数据'
    if searches:
        searchList = '\n'.join([search(item) for item in searches])

    topicList = '暂无数据'
    if topics:
        topicList = '\n'.join([topic(item) for item in topics])

    readme = ''
    with open('README_archive.template', 'r') as f:
        readme = f.read()

    readme = readme.replace("{date}", util.currentDateStr())
    readme = readme.replace("{updateTime}", util.currentTimeStr())
    readme = readme.replace("{searches}", searchList)
    readme = readme.replace("{topics}", topicList)

    return readme


def generateTodayReadme(searches, topics):
    """生成今日readme
    """
    def search(item):
        return '1. [{}]({})'.format(item['title'], item['url'])

    def topic(item):
        return '1. [{}]({})\n    - {}\n    - {}'.format(item['title'], item['url'], item['detail'], item['info'])

    searchList = '暂无数据'
    if searches:
        searchList = '\n'.join([search(item) for item in searches])

    topicList = '暂无数据'
    if topics:
        topicList = '\n'.join([topic(item) for item in topics])

    readme = ''
    with open('README.template', 'r') as f:
        readme = f.read()

    now = util.currentTimeStr()
    readme = readme.replace("{searches}", searchList)
    readme = readme.replace("{topics}", topicList)
    readme = readme.replace("{updateTime}", now)

    return readme


def handleTodayMd(md):
    log.info('today md:%s', md)
    util.writeText('README.md', md)


def handleArchiveMd(md):
    log.info('archive md:%s', md)
    name = '{}.md'.format(util.currentDateStr())
    file = os.path.join('archives', name)
    util.writeText(file, md)


def saveRawContent(content: str, filePrefix: str):
    if not content:
        log.warning('content is empty or none')
        return

    name = '{}-{}.html'.format(filePrefix, util.currentDateStr())
    file = os.path.join('raw', name)
    util.writeText(file, content)


def run():
    # 热搜
    searchContent = getContent(HOT_SEARCH)
    searchList = parseSearchList(searchContent)
    # 话题榜
    topicContent = getContent(HOT_TOPIC)
    topicList = parseTopicList(topicContent)

    # 最新数据
    todayMd = generateTodayReadme(searchList, topicList)
    handleTodayMd(todayMd)
    # 归档
    archiveMd = generateArchiveReadme(searchList, topicList)
    handleArchiveMd(archiveMd)
    # 原始数据
    saveRawContent(searchContent, 'hot-search')
    saveRawContent(topicContent, 'hot-topic')


if __name__ == "__main__":
    run()
