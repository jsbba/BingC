#!/usr/bin/env python
 
 
import time
import urllib2
from lxml import etree
from urllib import urlencode
from optparse import OptionParser
 
 
class search(object):
    def __init__(self):
        self.result = []
        self.count = 0
 
    def getresponse(self, dork, first=0, nrslt=15, last=None):
        query = {'q': dork,
                 'qs': 'n',
                 'from': 'QBLH',
                 'pq': dork,
                 'sc': '1-100',
                 'sp': '-1',
                 'sk': '',
                 'cvid': '69fc3e99c6195bad1e668cf2f40b56c3',
                 'first': first}
 
        bing_query = urlencode(query)
        bing_url = 'http://www.bing.com/search?%s' % bing_query
 
        # ------------- cookie ------------
        cookie_k1 = 'SRCHHPGUSR'
        cookie_v1 = urlencode({'NTAB': '0',
                               'NEWWND': '0',
                               'SRCHLANG': '',
                               'AS': '1'})
 
        cookie_k2 = '_FS'
        cookie_v2 = urlencode({'mkt': 'en-us',
                               'ui': '#en-us'})
 
        cookie_k3 = '&NRSLT'
        cookie_v3 = nrslt
 
        cookie = "%s=%s;%s=%s;%s=%s" % (cookie_k1, cookie_v1,
                                        cookie_k2, cookie_v2,
                                        cookie_k3, cookie_v3)
 
        headers = {'Host': 'www.bing.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:12.0)',
                   'Accept': 'text/html,application/xhtml+xml, \
                   application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Cookie': cookie}
 
        # print headers
 
        request = urllib2.Request(bing_url, headers=headers)
        opener = urllib2.urlopen(request)
        htmlresponse = opener.read()
 
        # print htmlresponse
        return htmlresponse
 
    def bing(self, dork, first=0, nrslt=15, last=None):
            """Bing search"""
            starttime = time.time()
 
            while (not last) or (first < last):
                htmlresponse = self.getresponse(dork, first, nrslt, last)
 
                htmlparser = etree.HTML(htmlresponse)
                # print htmlparser.xpath('//div[@class="sa_mc"]')
                # print htmlparser.xpath('//a/@href')
                # total = htmlparser.xpath('//span[@id="count"]/text()')
                # if len(total) == 0:
                #     break
                # print total
                # total = int(total[0].split(" ")[0].replace(',', ''))
 
                hrefs = htmlparser.xpath('//div[@class="sb_tlst"]/h3/a/@href')
                n_hrefs = len(hrefs)
                if n_hrefs == 0:
                    break
 
                # next page
                first += len(hrefs)
                self.count += n_hrefs
                self.result.extend(hrefs)
 
            endtime = time.time()
            costtime = endtime - starttime
 
            return costtime, self.count, self.result
 
 
def main():
    banner = '''
        _     _                        _
        | |__ (_)_ __   __ _ _   _ _ __| |
        | '_ \| | '_ \ / _` | | | | '__| |
        | |_) | | | | | (_| | |_| | |  | |
        |_.__/|_|_| |_|\__, |\__,_|_|  |_|
                    |___/
        Get Bing url search result(s)
        Created by hap.ddup@gmail.com
        '''
 
    usage = "Usage: %prog -q [bing dork(s)]"
    parser = OptionParser(usage)
 
    parser.add_option("-q",
                      "--query",
                      dest="bingquery",
                      help="bing query words. \"index.php?id=\"")
    (options, args) = parser.parse_args()
 
    if options.bingquery:
        s = search()
        costtime, count, hrefs = s.bing(options.bingquery, 0, 15)
 
        print "cost time: %fd\ttotal: %d" % (costtime, count)
        for href in hrefs:
            print href
    else:
        print banner
        parser.error("select -h for help")
 
if __name__ == "__main__":
    main()