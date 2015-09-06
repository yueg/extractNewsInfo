# -*- coding:utf-8 -*-
__author__ = 'yueg'
import scrapy
import re
from distance import editDistance
from bs4 import BeautifulSoup as bsp
import HTMLParser
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class NewsSpider(scrapy.Spider):


    def __init__(self, query=None):
        self.start_urls = [
            # "http://news.baidu.com/ns?rn=20&word=%s" % query,
            "http://focus.szonline.net/Channel/201509/01/1106802.shtm"
            # "http://www.chinaz.com/manage/2015/0826/438884.shtml?qq-pf-to=pcqq.discussion"
            # "http://www.zjjzx.cn/news/jdrp/40692.html"
            # "http://news.dayoo.com/finance/201508/27/141887_43451353.htm"
            # "http://www.askci.com/news/2015/09/01/93838w3kx.shtml"
            # "http://finance.ifeng.com/a/20150830/13945174_0.shtml"
            # "http://mt.sohu.com/20150901/n420223088.shtml"
            # "http://finance.sina.com.cn/stock/t/20150901/052023133004.shtml"
            # "http://finance.ifeng.com/a/20150830/13945174_1.shtml"
            # "http://www.ebrun.com/20150831/147065.shtml"
            # "http://stock.sohu.com/20150901/n420185055.shtml"
            # "http://news.ifeng.com/a/20150819/44467538_0.shtml"
            # "http://mt.sohu.com/20150825/n419764543.shtml",
            # "http://news.eastday.com/c/20150511/u1a8706292.html"
            # "http://www.cctime.com/html/2014-7-10/2014710111929005.htm"
            # "http://www.cnautonews.com/xwdc/201507/t20150731_418850.htm"
            # "http://auto.sina.com.cn/car/2014-04-05/14471284930.shtml"
            # "http://jnsb.e23.cn/shtml/jnsb/20150613/1448955.shtml"
            # "http://www.shfinancialnews.com/xww/2009jrb/node5019/node5036/node5048/userobject1ai149791.html"
            # "http://www.topnews9.com/article_20150824_45954.html"
            # "http://jjckb.xinhuanet.com/2015-05/26/content_549136.htm"
        ]

    def parse(self, response):
        sel = scrapy.Selector(response)
        url = response.url.encode('utf-8')
        title = sel.xpath('//html/head/title/text()').extract()[0]
        content = response.body
        urlSplit = url.split('/')
        mainUrl = urlSplit[2]

        if mainUrl == "news.baidu.com":
            for link in sel.xpath('//div/h3/a/@href').extract():
                request = scrapy.Request(link, callback=self.parse, dont_filter=True)
                yield request
        else:
            # content = content.decode('utf-8')
            content = self.convCharset2utf8(content)
            content = self.dealContent(content)
            # soap = bsp(content)
            # h1Finds = soap.find_all(name="h1")

            title = self.getTitle(title, content)
            print '---1---', title
            time = self.getTime(title, content)
            print '---2---', time
            content = self.getContent(title, content)
            print '---------------------------3--------------------------'
            print content




    def convCharset2utf8(self, content):
        patt = re.compile('<meta.*?charset=["]?(.*?)"');
        code = re.findall(patt, content)
        if len(code) > 0:
            type = code[0].lower()
            if type == 'gb2312':
                content = content.decode('gbk').encode('utf-8')
            else:
                content = content.decode(type).encode('utf-8')
        return content

    def dealContent(self, content):
        content, number = re.subn('<style[\s\S]*?</style>', '', content, flags=re.I)
        content, number = re.subn('<script[\s\S]*?</script>', '', content, flags=re.I)
        content, number = re.subn('<noscript[\s\S]*?</noscript>', '', content, flags=re.I)
        content, number = re.subn('<iframe[\s\S]*?</iframe>', '', content, flags=re.I)
        content, number = re.subn('<img[\s\S]*?>', '', content, flags=re.I)
        content, number = re.subn('<!--[\s\S]*?-->', '',content)
        content, number = re.subn('<head[\s\S]*?head>', '', content, flags=re.I)
        content, number = re.subn('</p>.{0,7}<p.*?>', '</p>\n<p>', content, flags=re.I)
        content, number = re.subn('</li>.{0,7}<li.*?>', '</li>\n<li>', content, flags=re.I)
        # content, number = re.subn('(i?)<a[\s\S]*?a>', '', content)
        # content, number = re.subn('(i?)(&nbsp;)+', '', content)
        # content, number = re.subn('(i?)(&copy;)+', '', content)
        # content, number = re.subn('(i?)(&quot;)+', '', content)
        # content, number = re.subn('(i?)(&gt;)+', '', content)
        content = self.html_parser.unescape(content)
        content, number = re.subn('<br[ /]?/?>.?<br[ /]?/?>', '\n', content, flags=re.I)
        content, number = re.subn('<br[ /]?/?>', '\n', content, flags=re.I)
        content, number = re.subn('<img.*?>', '', content, flags=re.I)
        content, number = re.subn('<br>', '\n', content, flags=re.I)
        content, number = re.subn('\t', '\n', content)
        content, number = re.subn('\n[\s]*?\n', '\n', content)
        content, number = re.subn('\n[\s]*?\n', '\n', content)
        content, number = re.subn('\n[\s]*?\n', '\n', content)
        content, number = re.subn('\n[\s]*?\n', '\n', content)
        return content

    def getTime(self, title, content):
        pattern = []
        timelist = []
        pattern.append(re.compile('(20\d{2}[年]\d{1,2}[月]\d{1,2}日[ ]?\d{0,2}:?\d{0,2}:?\d{0,2})'.decode("utf8")))
        pattern.append(re.compile('(20\d{2}[/]\d{1,2}[/]\d{1,2}[ ]?\d{0,2}:?\d{0,2}:?\d{0,2})'.decode("utf8")))
        pattern.append(re.compile('(20\d{2}[-]\d{1,2}[-]\d{1,2}[ ]?\d{0,2}:?\d{0,2}:?\d{0,2})'.decode("utf8")))
        cutContent = self.cutContent(title, content)
        lines = cutContent.split('\n')
        lineRange = self.getBeginAndEnd(lines)
        lines = cutContent.split('\n')
        end = lineRange['end']
        for i in range(0, end + 1):
            print lines[i]
            if lines[i] == None or lines[i].strip == '':
                continue
            for patt in pattern:
                temp = re.findall(patt, lines[i].decode('utf8'))
                if len(temp) > 0:
                    return self.getStandardTime(temp[0])
        return self.getTimeFromAllContent(content)

    def getTimeFromAllContent(self, content):
        pattern = []
        pattern.append(re.compile('(20\d{2}[年]\d{1,2}[月]\d{1,2}日[ ]?\d{0,2}:?\d{0,2}:?\d{0,2})'.decode("utf8")))
        pattern.append(re.compile('(20\d{2}[/]\d{1,2}[/]\d{1,2}[ ]?\d{0,2}:?\d{0,2}:?\d{0,2})'.decode("utf8")))
        pattern.append(re.compile('(20\d{2}[-]\d{1,2}[-]\d{1,2}[ ]?\d{0,2}:?\d{0,2}:?\d{0,2})'.decode("utf8")))
        timelist = []
        for patt in pattern:
            temp = re.findall(patt, content.decode('utf8'))
            timelist.extend(temp)
        return self.getRealTimeFromList(timelist)

    def getRealTimeFromList(self, timeList):
        if len(timeList) == 0:
            return ""
        if len(timeList) == 1:
            return self.getStandardTime(timeList[0])
        maxTime = 0
        for time in timeList:
            secsTime = self.getStandardTime(time)
            if secsTime > maxTime:
                maxTime = secsTime
        return maxTime

    def getStandardTime(self, str):
        str, number = re.subn('[/年月]'.decode('utf8'), '-', str)
        str, number = re.subn('[日]'.decode('utf8'), '', str)
        times = str.split(' ')
        t = ''
        if len(times) > 0:
            temp = times[0].split('-')
            if len(temp) < 3:
                return 0
            if len(temp[0]) != 4:
                return 0
            t += temp[0] + '-'
            if len(temp[1]) == 1:
                t += '0' + temp[1] + '-'
            elif len(temp[1]) == 2:
                t += temp[1] + '-'
            else:
                return 0
            if len(temp[2]) == 1:
                t += '0' + temp[2]
            elif len(temp[2]) == 2:
                t += temp[2]
            else:
                return 0
        elif len(times) > 1:
            t += ' ' + times[2]
        str = t
        print str
        if len(str) == 10:
            temp = time.strptime(str, "%Y-%m-%d")
        elif len(str) == 13:
            temp = time.strptime(str, "%Y-%m-%d %H")
        elif len(str) == 16:
            temp = time.strptime(str, "%Y-%m-%d %H:%M")
        elif len(str) == 19:
            temp = time.strptime(str, "%Y-%m-%d %H:%M:%S")
        else:
            return 0
        secsTime = time.mktime(temp)
        return secsTime


    def getTitle(self, title, content):
        soup = bsp(content)
        hs = soup.findAll('h1')
        hs += soup.findAll('h2')
        lines = []
        for h in hs:
            lines.append(h.string)
        if len(lines) != 0:
            ret = self.getTitleFromLinesInHTags(title, lines)
            if ret and ret != '':
                return ret
        content, number = re.subn('<[\s\S]*?>', '', content)
        lines = content.split('\n')
        return self.getTitleFromLinesInAllContext(title, lines)

    def getTitleFromLinesInHTags(self, title, lines):
        title = title.strip().encode('utf8')
        count = editDistance.arithmetic().levenshtein(title, u'')
        ret = ''
        for line in lines:
            if line == None:
                continue
            temp = line.strip().encode('utf8')
            if temp == '':
                continue
            editDis = editDistance.arithmetic().levenshtein(title, temp)
            if editDis < count:
                count = editDis
                ret = temp
        if (count + 0.0) / len(title) > 0.5:
            return ''
        return ret


    def getTitleFromLinesInAllContext(self, title, lines):
        title = title.strip().encode('utf8')
        count = editDistance.arithmetic().levenshtein(title, u'')
        ret = ''
        for line in lines:
            if line == None:
                continue
            temp = line.strip().encode('utf8')
            if temp == '':
                continue
            editDis = editDistance.arithmetic().levenshtein(title, temp)
            if editDis < count:
                count = editDis
                ret = temp
        if (count + 0.0) / len(title) > 0.5:
            return title
        return ret

    def cutContent(self, title, content):
        content, number = re.subn('<[\s\S]*?>', '', content)
        content, number = re.subn('.*?\|.*?\|.*?\n', '\n', content)
        content, number = re.subn('.*?┊.*?┊.*?\n', '\n', content)
        content, number = re.subn('\r', '\n', content)
        content, number = re.subn('\t', ' ', content)
        content, number = re.subn(u'分享到.*?\n', '', content)
        index = content.find(title)
        if index < 0:
            index = 0
        content = content[index:]
        return content

    def getContent(self, title, content):
        content = self.cutContent(title, content)
        lines = content.split('\n')
        lineRange = self.getBeginAndEnd(lines)
        ret = ''
        for i in range(lineRange['begin'],  lineRange['end'] + 1):
            ret += lines[i] + '\n'
        return ret

    def getBeginAndEnd(self, lines):
        for i in range(len(lines)):
            count = 0
            for c in lines[i]:
                if c == u' ' or c == u'\t' or c == u'  ':
                    count += 1
            if count == 0:
                continue
            if len(lines[i].strip()) <= count and lines[i].strip() != '■':
                lines[i] = ''

        begin = 0
        maxBegin = 0
        maxEnd = 0
        length = 0
        count = 0
        emptyCount = 0
        degree = 0.0
        i = 0
        while i < len(lines):
            count += len(lines[i].strip())
            if lines[i].strip() == '':
                emptyCount += 1
            else:
                emptyCount = 0
            if emptyCount == 4:
                length = i + 1 - begin
                if (count + 0.0) / (length + 0.0) > degree:
                    degree = (count + 0.0) / (length + 0.0)
                    maxBegin = begin
                    maxEnd = i
                i += 1
                while i < len(lines) and lines[i].strip() == '':
                    i += 1
                count = 0
                begin = i
                continue
            i += 1

        begin = maxBegin
        end = maxEnd - 4
        ret = {'begin': begin, 'end': end}
        return ret

