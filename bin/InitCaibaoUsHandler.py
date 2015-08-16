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


class InitCaibaoUsHandler(object):
    def parse(self, task):
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        if status == 'OK':
            for text in ret:
                print text.strip()
        else:
            task.status = 'failed'
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        ret = []
        page = page.decode('utf-8')
        try:
            soup = BS(page)
            tableDiv = soup.find('div', class_='genTable')
            trList = tableDiv.find_all('tr')
            for tr in trList:
                ret.append(tr.text)   
        except Exception, e:
            util.printException()
            return (None, e)
        return (ret, 'OK')


if __name__ == '__main__':
    m = InitCaibaoUsHandler()
    fdata = open('cases/sh_stock_list.html').read()
    ret, status = m.parseContent(fdata.decode('gbk'))
    print ret['nextPage']

