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

class HkPageHandler(object):
    def __init__(self):
        self.historyKeys = set([])
        self.__init__historyKeys()

    def __init__historyKeys(self):
        files = os.listdir(iPapa.iDataPath)        
        for f in files:
            if f.startswith('hk_sotck_info_list'):
                with open(os.path.join(iPapa.iDataPath, f)) as ff:
                    for k in ff:
                        self.historyKeys.add(k.strip().decode('utf-8'))
        return True

    def parse(self, task):
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        if status == 'OK':
            #dump list
            keyOutputPath = iPapa.iTsOutputPath
            outputJsonLoc = os.path.join(keyOutputPath, 'hk_main_stock_list_cn.json')
            outputTxtLoc = os.path.join(keyOutputPath, 'hk_main_stock_list_cn.txt')
            if util.dump2JsonFile(ret['stockList'], outputJsonLoc) != True:
                task.status = 'failed'

            if util.dump2TxtFile(ret['stockList'], outputTxtLoc) != True:
                task.status = 'failed'

            for k in ret['stockInfoPage']:
                if k not in self.historyKeys:
                    newT = Task(-1, url=ret['stockInfoPage'][k], handler='HkStockInfoCnPageHandler', ref=task.url)  
                    newT['key'] = "hk_stock_info_" + k
                    newTasks.append(newT)
        else:
            task.status = 'failed'
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        ret = {'stockInfoPage':{}, 'stockList':[]}
        try:
            soup = BS(page)           
            trList = soup.find_all('tr',  class_ ='tr_normal' ) 
            for tr in trList:
                tdList = tr.find_all('td')
                href = ''
                if hasattr(tdList[1], 'a') and tdList[1].a != None and tdList[1].a != '':
                    href = tdList[1].a['href']
                textList = [ td.text for td in  tdList ]
                textList.append(href)
                ret['stockList'].append(textList)
                ret['stockInfoPage'][textList[0]] = href
        except Exception, e:
            util.printException()
            return (None, e)
        return (ret, 'OK')


if __name__ == '__main__':
    m = HkPageHandler()
    fdata = open('cases/hk_simp_chinese_stock_list.html').read()
    m.parseContent(fdata)

