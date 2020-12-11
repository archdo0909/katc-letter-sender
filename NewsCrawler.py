import json
import requests

from bs4 import BeautifulSoup
from urllib.request import urlopen
from enum import Enum, auto
from datetime import datetime, timedelta


class NewsCrawler:
    class NaverNews:
        soup = ""
        class NewsType(Enum):
            def _generate_next_value_(name, start, count, last_values):
                return name
            POLITIC     = auto()
            ECONOMY     = auto()
            SOCIETY     = auto()
            LIFECULTURE = auto()
            WORLD       = auto()
            ITSCIENCE   = auto()
        
        class OfficeId(Enum):
            
            JTBC = 437
            YONHAP = 1
            CHOSUN = 23

        def getNewslist(self, newsType):
            t = datetime.today() - timedelta(1)
            y = str(t.year)
            m = str(t.month).zfill(2)
            d = str(t.day).zfill(2)

            self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
            #url = 'https://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&date='+y+m+d
            url = "https://news.naver.com/main/ranking/office.nhn?officeId=" + str(newsType.value).zfill(3)
            newsPage = requests.get(url, headers=self.headers)
            self.soup = BeautifulSoup(newsPage.content, "html.parser")
            
            print(len(self.soup.select(".list_content")))

            length_list = len(self.soup.select(".list_content"))
            #contents_url = print(self.soup.select(".list_content")[0].a['href'])
            #title = print(self.soup.select(".list_content")[0].a.get_text())

            return length_list

        def getNewsContents(self, num):
            title = self.soup.select(".list_content")[num].a.get_text()
            
            contents_url = "https://news.naver.com" + str(self.soup.select(".list_content")[num].a['href'])
            contents_page = requests.get(contents_url, headers=self.headers)

            res = BeautifulSoup(contents_page.content, "html.parser")

            contents_body = res.select('#articleBodyContents')[0].get_text().replace('\n', " ")
            contents_body = contents_body.replace('// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}', "")
            
            return title, contents_body


if __name__ == '__main__':

    nc = NewsCrawler.NaverNews()
    length = nc.getNewslist(nc.OfficeId.CHOSUN)
    nc.getNewsContents(1)