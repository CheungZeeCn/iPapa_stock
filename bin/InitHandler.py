#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

from bs4 import BeautifulSoup as BS
from iTask import Task
import os
import urlparse
import util

class InitHandler(object):
    def parse(self, task):
        output = {}
        ret, status = ('ok', 'ok')
        if status != 'ok':
            task.status = 'failed'
            return output
            
        output['newTasks'] = []
        newHK = Task(-1, url="https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdeqty_c.htm", handler='HkPageHandler', ref=task.url)  
        newHK2 = Task(-1, url="https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/market/sec_tradinfo/stockcode/eisdgems_c.htm", handler='HkGemPageHandler', ref=task.url)  
        #newSH = Task(-1, url=urlparse.urljoin(task.url, link), handler='ClassPageHandler', ref=task.url)  
        #newSZ = Task(-1, url=urlparse.urljoin(task.url, link), handler='ClassPageHandler', ref=task.url)  
        output['newTasks'].append(newHK) 
        output['newTasks'].append(newHK2) 
        return output


if __name__ == '__main__':
    data = open('tmp').read()
    m = MainPageHandler()
    m.parserContent(data)

