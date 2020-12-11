import re
import json
import requests

from bs4 import BeautifulSoup
from NewsCrawler import NewsCrawler

class LetterClient:

    def __init__(self):
        self.host = 'https://www.thecamp.or.kr'
        self.session = requests.Session()

    def _post(self, endpoint, data):
        response = self.session.post(self.host + endpoint, data=data)
        if response.status_code != 200:
            raise ConnectionError(f'Connection failed: [{response.status_code}] - {response.text}')
        return response.text

    def login(self, userid, passwd):
        endpoint = '/login/loginA.do'
        data = {
            'state' : 'email-login',
            'autoLoginYn' : 'N',
            'userId' : userid,
            'userPwd' : passwd
        }

        res = self._post(endpoint, data) 
        res = json.loads(res, encoding='utf-8')

        if 'resultCd' in res and res['resultCd'] == '0000':
            print(f'Successfully Login! [{userid}]')
            return True
        print(f'Login failed. [{res["resultMsg"] if "resultMsg" in res else "Unknown Error"}]')
        return False

    def get_cafes(self):
        endpoint = '/eduUnitCafe/viewEduUnitCafeMain.do'
        data = {}
        result = self._post(endpoint, data)
        soup = BeautifulSoup(result, 'html.parser')

        cafe_table = {}

        cafes = soup.select('.cafe-card-box')
        for cafe in cafes:
            name_div = cafe.select('.profile-wrap .id span')[0]
            name = name_div.text.split()[0]
            buttons = cafe.select('.btn-wrap')[0].find_all('a')

            for button in buttons:
                if button.text == '위문편지':
                    regex = re.compile('\'\d+\'')
                    codes = regex.findall(button['href'])

                    edu_seq, train_unit_code = map(lambda x: int(x[1:-1]), codes)
                    cafe_table[name] = (edu_seq, train_unit_code)
                    break
            else:
                cafe_table[name] = None
                continue

        return cafe_table

    def send_letter(self, name, title, content):
        chkedContent = self._splitContent(content)

        for cont in chkedContent:
            #print("cont-------------" + cont + "\n")
            self._send(name, title, cont)

    def _send(self, name, title, content):
        cafes = self.get_cafes()
        if name not in cafes:
            print(f'No Cafe with name: [{name}].')
            return False
        if cafes[name] is None:
            print(f'Cafe[{name}] is not open yet.')
            return False

        mgr_seq = self._get_mgr_seq(*cafes[name])
        endpoint = '/consolLetter/insertConsolLetterA.do'
        data = {
            'boardDiv': '',
            'tempSaveYn': 'N',
            'sympathyLetterEditorFileGroupSeq': '',
            'fileGroupMgrSeq': '',
            'fileMgrSeq': '',
            'sympathyLetterMgrSeq': '',
            'traineeMgrSeq': mgr_seq,
            'sympathyLetterSubject': title,
            'sympathyLetterContent': content,
        }

        result = self._post(endpoint, data)
        #result = json.loads(result, encoding='utf-8')
        print(result)

    def _splitContent(self, content):
        splited = content.split('\n')
        slen = 0
        bodies = []
        for i in range(0, len(splited)):
            if slen + len(splited[i]) > 1450:
                bodies.append('\n'.join(splited[:i - 1]) + '\n' +splited[i][:1450 - slen])
                bodies += self._splitContent(splited[i][1450-slen:] + '\n' + '\n'.join(splited[i + 1:]))
                return bodies
            slen += len(splited[i])
            if i == 24:
                bodies.append("\n".join(splited[:i]))
                bodies += self._splitContent('\n'.join(splited[i + 1:]))
                return bodies
        bodies.append(content)
        return bodies

    def _get_mgr_seq(self, edu_seq, train_unit_code):
        endpoint = '/consolLetter/viewConsolLetterMain.do'
        data = {
            'trainUnitEduSeq': edu_seq,
            'trainUnitCd': train_unit_code,
        }
        result = self._post(endpoint, data)
        soup = BeautifulSoup(result, 'html.parser')

        letter_box = soup.select('.letter-card-box')[0]
        regex = re.compile('\'\d+\'')
        codes = regex.findall(letter_box['href'])

        mgr_seq = map(lambda x: int(x[1:-1]), codes)
        return mgr_seq


if __name__ == '__main__':

    from user_config import LOGIN_ID
    from user_config import LOGIN_PWD

    client = LetterClient()
    client.login(LOGIN_ID, LOGIN_PWD)
    # 그냥 커스텀 텍스트 써서 보낼 때
    title = "Holy"
    contents = "YEAH"
    client.send_letter(name='김한준', title=title, content=contents)

    # 뉴스 스크랩
    # 신문사 선택 가능 (JTBC, YONHAP, CHOSUN)

    nc = NewsCrawler.NaverNews()
    length = nc.getNewslist(nc.OfficeId.JTBC)
    for l in range(20):
        title, contents = nc.getNewsContents(l)
        print(title)
        client.send_letter(name='김한준', title=title, content=contents)
