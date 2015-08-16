#/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

from setup import iPapa
from bs4 import BeautifulSoup as BS
from iTask import Task
import urlparse
import os
import util
import time
import urlparse


class InitShHandler(object):
    def __init__(self):
        self.historyKeys = set([])
        self.__init__historyKeys()

    def __init__historyKeys(self):
        files = os.listdir(iPapa.iDataPath)        
        for f in files:
            if f.startswith('sh_sotck_info_list'):
                with open(os.path.join(iPapa.iDataPath, f)) as ff:
                    for k in ff:
                        self.historyKeys.add(k.strip().decode('utf-8'))
        return True

    def parse(self, task):
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        if status == 'OK':
            #dump list
            for i in range(len(ret['stockList'])):
                ret['stockList'][i]['href'] = urlparse.urljoin(task.url, ret['stockList'][i]['href'])
                newT = Task(-1, url=ret['stockList'][i]['href'], handler='ShStockBasicInfoHandler', ref=task.url)  
                newTasks.append(newT)
                
            keyOutputPath = iPapa.iTsOutputPath
            outputJsonLoc = os.path.join(keyOutputPath, 'sh_stock_list_page_%d.json' % task['key'])
            outputTxtLoc = os.path.join(keyOutputPath, 'sh_stock_list_page_%d.txt' % task['key'])

            if util.dump2JsonFile(ret['stockList'], outputJsonLoc) != True:
                task.status = 'failed'

            if util.dumpDictList2TxtFile(ret['stockList'], outputTxtLoc) != True:
                task.status = 'failed'

            #new tasks here

            page = task['key']
            if ret['nextPage'] != '':
                newT = Task(-1, url=urlparse.urljoin(task.url, ret['nextPage']), handler='InitShHandler', ref=task.url)  
                newT['key'] = page+1
                newTasks.append(newT)
        else:
            task.status = 'failed'
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        page = page.decode('gbk')
        ret = {'stockList':[], 'nextPage':''}
        try:
            soup = BS(page)
            theA = soup.find('a', text='下一页')
            if theA != None and theA['href'] != '':
                ret['nextPage'] = theA['href']

            table = soup.find('table', width="100%", cellspacing="1", cellpadding="2", border="0", bgcolor="#337fb2") 
            trList = table.find_all('tr')
            for tr in trList[1:]:
                tdList = tr.find_all('td')             
                code = tdList[0].text
                name = tdList[1].text
                href = tdList[0].a['href']
                ret['stockList'].append({'code': code, 'name': name, 'href': href})
        except Exception, e:
            util.printException()
            return (None, e)
        return (ret, 'OK')


if __name__ == '__main__':
    m = InitShHandler()
    fdata = open('cases/sh_stock_list.html').read()
    ret, status = m.parseContent(fdata.decode('gbk'))
    print ret['nextPage']

