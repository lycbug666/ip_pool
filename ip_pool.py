# coding: utf-8
import requests
import threading
import time
import codecs

from bs4 import BeautifulSoup as BS

rawProxyList = []
checkedList = []
targets = []
headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      r'Chrome/45.0.2454.101 Safari/537.36',
        'Connection': 'keep-alive'
    }
for i in range(1, 4):
    target = "http://www.xicidaili.com/nn/%d" %i
    targets.append(target)
# print targets


# Parse the proxy website and get proxies
class ProxyGet(threading.Thread):
    def __init__(self, target):
        threading.Thread.__init__(self)
        self.target = target

    def get_proxy(self):
        print ("目标网站：" + self.target)
        r = requests.get(self.target, headers=headers)
        page = r.text
        soup = BS(page, 'lxml')
        tr_lists = soup.find_all("tr", class_="odd")
        # print tr_lists

        '''
        for i in range(len(tr_lists)):
            row = []
            # .stripped_strings 方法返回去除前后空白的Python的string对象.
            for text in tr_lists[i].stripped_strings:
                row.append(text)
                row = ['58.208.16.141','808','江苏苏州','高匿','HTTP,......]
                print row
                ip = row[0]
                port = row[1]
                agent = row[4].lower
                addr = agent + '://' + ip + ':' + port
            '''

        for tr_list in tr_lists:
            # print tr_list
            ip = tr_list.select('td')[1].get_text()
            print ip
            port = tr_list.select('td')[2].get_text()
            print port
            agent = tr_list.select('td')[5].get_text().lower()
            print agent
            addr = agent + '://' + ip + ':' + str(port)
            proxy = [ip, port, agent, addr]
            print proxy
            rawProxyList.append(proxy)

    def run(self):
        self.get_proxy()


# check if the proxies are useful.
class ProxyCheck(threading.Thread):

    def __init__(self, proxy_list):
        threading.Thread.__init__(self)
        self.proxy_list = proxy_list
        self.timeout = 2
        self.testUrl = "https://www.baidu.com/"

    def check_proxy(self):

        for proxy in self.proxy_list:
            proxies = {}
            if proxy[2] == "http":
                proxies['http'] = proxy[3]
            else:
                proxies['https'] = proxy[3]
            t1 = time.time()
            try:
                r = requests.get(self.testUrl, headers=headers, proxies=proxies, timeout=self.timeout)
                time_used = time.time() - t1
                if r:
                    checkedList.append((proxy[0], proxy[1], proxy[2], proxy[3], time_used))
                    # print checkedList
                else:
                    continue
            except Exception as e:
                continue

    def run(self):
        self.check_proxy()
        # print("hello")

if __name__ == '__main__':

    getThreads = []
    checkedThreads = []

    # 对每个目标网站开启一个线程负责抓取代理
    for i in range(len(targets)):
        t = ProxyGet(targets[i])
        getThreads.append(t)

    for i in range(len(getThreads)):
        getThreads[i].start()

    for i in range(len(getThreads)):
        getThreads[i].join()

    print ('.'*10+"总共抓取了%s个代理" %len(rawProxyList) +'.'*10)

    # 开启20个线程负责校验，将抓取到的150个代理分成20份，每个线程校验一份.

    for i in range(10):
        n = len(rawProxyList) / 10
        print (str(int(n * i)) + ":" + str(int(n * (i+1))))
        t = ProxyCheck(rawProxyList[int(n * i):int(n * (i + 1))])
        # 从获取到的代理列表中循环抽取代理来测试，若测试时间超过设定的延时，则抛弃
        checkedThreads.append(t)

    for i in range(len(checkedThreads)):
        checkedThreads[i].start()

    for i in range(len(checkedThreads)):
        checkedThreads[i].join()

    print checkedList
    print ('.' * 10 + "总共有%s个代理通过校验" % len(checkedList) + '.' * 10)

    # 数据持久化
    f = codecs.open("proxy_list.txt", "wb+")
    for checked_proxy in sorted(checkedList):
        print "checked proxy is: %s\t %ss" %(checked_proxy[3],checked_proxy[4])
        f.write("%s:%s\t%s\t%s\t%s\n" % (checked_proxy[0], checked_proxy[1], checked_proxy[2],
                                         checked_proxy[3], checked_proxy[4]))
