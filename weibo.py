import contextlib
import json
import traceback

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from util import logger

HOT_SEARCH_URL = "https://s.weibo.com/top/summary?cate=realtimehot"
HOT_TOPIC_URL = "https://s.weibo.com/top/summary?cate=topicband"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
}

RETRIES = Retry(total=3,
                backoff_factor=1,
                status_forcelist=[k for k in range(400, 600)])

@contextlib.contextmanager
def request_session():
    s = requests.session()
    try:
        s.headers.update(HEADERS)
        s.mount("http://", HTTPAdapter(max_retries=RETRIES))
        s.mount("https://", HTTPAdapter(max_retries=RETRIES))
        yield s
    finally:
        s.close()

class Weibo:

    def get_hot_search(self):
        """热搜
        """
        items = []
        resp = None
        try:
            with request_session() as s:
                resp = s.get(HOT_SEARCH_URL)
                html = resp.text
                soup = BeautifulSoup(html)
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
                            items.append({'title': title, 'url': url})
        except:
            logger.warning(traceback.format_exc())
        return (items,resp)


    def get_hot_topic(self):
        """热门话题
        """
        items = []
        resp = None
        try:
            with request_session() as s:
                resp = s.get(HOT_TOPIC_URL)
                html = resp.text
                soup = BeautifulSoup(html)
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
                            items.append({'title': title, 'url': url,
                                        'detail': detail, 'info': info})
        except:
            logger.warning(traceback.format_exc())
        return (items,resp)


if __name__ == "__main__":
    weibo = Weibo()
    searches,resp = weibo.get_hot_search()
    logger.info('%s',searches[0])
