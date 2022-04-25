import contextlib

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from util import logger

HOT_SEARCH_URL = "https://m.weibo.cn/api/container/getIndex"

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
        {
            "icon_width": 24,
            "icon_height": 24,
            "card_type": 4,
            "scheme": "https://m.weibo.cn/search?containerid=100103type%3D1%26t%3D10%26q%3D%23%E5%8F%96%E6%B6%88%E5%88%9D%E4%B8%AD%E6%AF%95%E4%B8%9A%E5%90%8E%E6%99%AE%E8%81%8C%E5%88%86%E6%B5%81%23&stream_entry_id=31&isnewpage=1&extparam=seat%3D1%26realpos%3D1%26flag%3D2%26filter_type%3Drealtimehot%26c_type%3D31%26pos%3D0%26lcate%3D5001%26cate%3D0%26dgr%3D0%26display_time%3D1650855802%26pre_seqid%3D16508558027530414814115&luicode=10000011&lfid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot",
            "icon": "https://simg.s.weibo.com/20210226_hot.png",
            "pic": "https://simg.s.weibo.com/20170303_img_search_1.png",
            "itemid": "c_type:31|cate:10103|t:31|key:#取消初中毕业后普职分流#||type:25",
            "desc": "取消初中毕业后普职分流",
            "desc_extr": 2605983
          }
        """
        items = []
        resp = None
        try:
            with request_session() as s:
                payload = {
                    "containerid": "106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot",
                    "extparam": "filter_type%3Drealtimehot%26mi_cid%3D100103%26pos%3D0_0%26c_type%3D30%26display_time%3D1550505541",
                    "luicode": "10000011",
                    "lfid": "231583",
                }
                resp = s.get(HOT_SEARCH_URL, params=payload)
                j = resp.json()
                if j["ok"] == 1:
                    cards = j["data"]["cards"]
                    if cards:
                        items = cards[0]["card_group"]
        except:
            logger.exception('get hot search failed')
        return (items, resp)

    def get_hot_topic(self):
        """热门话题
        {
            "pic": "https://wx3.sinaimg.cn/large/6038bf91ly8h1kxbthduoj20dw0dwdgi.jpg",
            "top_mark_pic": "https://n.sinaimg.cn/photo/5b5e52aa/20170406/page_rankinglist_card8_2x_default.png",
            "top_mark_text": 1,
            "desc": "1.3万讨论 1.3亿阅读",
            "card_display_type": 0,
            "title_sub": "#男朋友的分享欲可以有多强#",
            "display_arrow": 0,
            "card_type": 25,
            "scheme": "https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E7%94%B7%E6%9C%8B%E5%8F%8B%E7%9A%84%E5%88%86%E4%BA%AB%E6%AC%B2%E5%8F%AF%E4%BB%A5%E6%9C%89%E5%A4%9A%E5%BC%BA%23&stream_entry_id=128&isnewpage=1&extparam=seat%3D1%26dgr%3D0%26unitid%3D1650798070792%26lcate%3D5004%26c_type%3D128%26cate%3D5004%26pos%3D1-0-0%26display_time%3D1650872354%26pre_seqid%3D165087187124900621285&luicode=10000011&lfid=231648_-_4",
            "card_expand": {
              "content": "情侣就是要互相分享生活中的琐事，相互的体谅，包容和关爱"
            }
        }
        """
        items = []
        resp = None
        try:
            with request_session() as s:
                payload = {
                    "containerid": "231648_-_4",
                    "extparam": "seat%3D1%26position%3D%255B%255D%26dgr%3D0%26display_time%3D1650872180%26pre_seqid%3D16508721809380183149353",
                    "luicode": "10000011",
                    "lfid": "231648_-_1",
                }
                resp = s.get(HOT_SEARCH_URL, params=payload)
                j = resp.json()
                if j["ok"] == 1:
                    cards = j["data"]["cards"]
                    if cards:
                        items = cards[0]["card_group"]
        except:
            logger.exception('get hot topic failed')
        return (items, resp)


if __name__ == "__main__":
    weibo = Weibo()
    # searches, _ = weibo.get_hot_search()
    # logger.info(searches)

    topics, _ = weibo.get_hot_topic()
    logger.info(topics)
