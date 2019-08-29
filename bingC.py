# coding:utf-8

"""
Usage:
  python bingC.py IP/MASK [output_path]
Example:
  python bingC.py 132.12.43.0/24 result.txt
  python bingC.py 132.12.43.0/24
"""

import requests
import Queue
import threading
import re
import sys
import time
from IPy import IPy
from api import BingSearch
from config import ENABLE_BING_API

queue = Queue.Queue()
ips = set()
lock = threading.Lock()
thread_num = 20


def scan():
    global thread_num
    while 1:
        if queue.qsize() > 0:
            ip = queue.get()

            #先bing普通处理,主要结果数量优先
            morepage = 1
            page = 1
            index = 1
            prec = ''
            pagesize = 0;
            cookies = requests.cookies.RequestsCookieJar()
            response = requests.get('https://www.bing.com/',headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'},cookies=cookies)
            cookies.update(response.cookies)
            while morepage:
                #获取pagesize

                q = "https://www.bing.com/search?first=" + str(index) + "&q=ip:" + ip           
                c = requests.get(q,proxies={"https":"http://localhost:8080"} , verify=False,headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'},cookies=cookies).content

                content = re.search(r'<ol id="b_results">(.*?)<nav role="navigation"',c).group(1)
                if (page == 1):
                    pagesize = int(re.search(r'<ul class="sb_pagF">.*?first=(\d+).*?</a>', c).group(1))-1
               
                l = re.findall(r'<li class="b_algo">(.*?)</li>', c)
                for each in l:
                    domain = re.search(r'<h2><a target="_blank" href="(.*?)".*?</h2>',each).group(1)
                    title = re.search(r'<h2><a.*?>(.*?)</a></h2>',each).group(1)
                    msg = ip + ' -> ' + domain + ' -> ' + title
                    ips.add(msg)

                
                page = page + 1
                index = ((page-1) * pagesize)+1
                if (prec==content):
                    morepage =0
                
                prec = content


            # bing api处理
            if ENABLE_BING_API:
                print "[*]api enabled!"
                ans_obj = BingSearch("ip:" + ip)
                for each in ans_obj['d']['results']:
                    ips.add(ip + ' -> ' + each['Url'].split('://')[-1].split('/')[0] + " | " + each['Title'])
            



        else:
            thread_num -= 1
            break




def setThreadDaemon(thread):
    # Reference: http://stackoverflow.com/questions/190010/daemon-threads-explanation
    PYVERSION = sys.version.split()[0]
    if PYVERSION >= "2.6":
        thread.daemon = True
    else:
        thread.setDaemon(True)


def runThreads():
    print "Running..."
    for i in range(thread_num):
        t = threading.Thread(target=scan, name=str(i))
        setThreadDaemon(t)
        t.start()
    # It can quit with Ctrl-C
    while 1:
        if thread_num > 0:
            time.sleep(0.01)
        else:
            break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    try:
        _list = IPy.IP(sys.argv[1])
    except Exception, e:
        sys.exit('Invalid IP/MASK, %s' % e)
    for each in _list:
        queue.put(str(each))

    runThreads()
    for each in ips:
        try:
            print each
        except UnicodeEncodeError:
            pass
    #ips去重复处理
    print "Total: " + str(len(ips))

    if len(sys.argv) is 3:
        path = sys.argv[2]
        try:
            f = open(path, 'w')
            for each in ips:
                f.write(each + '\n')
            f.close()
        except IOError, e:
            sys.exit('Invalid file path')
