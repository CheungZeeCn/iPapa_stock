#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.


from setup import iPapa
from bs4 import BeautifulSoup as BS
import os
import urlparse
from iTask import Task
import util
import re
import logging

class HkStockInfoCnPageHandler(object):
    def __init__(self):
        self.reXHX = re.compile(r"(%s)_+"%"_"*12)

    def parse(self, task):
        print "HkStockInfoCnPageHandler parse", task.url, task['key']
        ret, status = self.parseContent(task['__data'])
        if status == 'OK':
            key = task['key']
            keyOutputPath = iPapa.iTsOutputPath

            outputJsonLoc = os.path.join(keyOutputPath, 'hk_stock_info_cn_'+key+'.json')
            outputTxtLoc = os.path.join(keyOutputPath, 'hk_stock_info_cn_'+key+'.txt')

            if util.dump2JsonFile(ret, outputJsonLoc) != True:
                task.status = 'failed'

            if util.dump2TxtFile(zip(ret.keys(), ret.values()), outputTxtLoc) != True:
                task.status = 'failed'
        
        else:
            task.status = 'failed'
        if task.status == 'ignore': 
            return {}
        return {}

    def parseContent(self, page):
        ret = {}
        try:
            soup = BS(page.decode('gbk'))
            table = soup.find('table', width="92%", cellspacing="1", cellpadding="2", border="0") 
            trList = table.find_all('tr')
            for tr in trList:
                tdList = tr.find_all('td')
                if len(tdList) <= 1:
                    continue
                k = tdList[0].text.strip().split(":")[0]
                v = tdList[1].text.strip()
                ret[k] = v
        except Exception, e:
            util.printException()
            return (None, e)

        return (ret, 'OK')


if __name__ == '__main__':
    inputCase = 'cases/hk_stock_info_cn_3.html'
    data = open(inputCase).read()
    m = HkStockInfoCnPageHandler()
    ret, status =  m.parseContent(data)

