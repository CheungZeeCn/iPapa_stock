#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-02-05 16:03:29 
# Copyright 2014 NONE rights reserved.

import setup
# import config class
from setup import iPapa
#import logger
#import logging
from iManager import WorkManager
from iTask import Task
import conf


# start the program

if __name__ == '__main__':
    # 1. setup first task or tasks
    seedTask = Task(1, url='https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/invest/company/profile_page_c.asp?WidCoID=08003&WidCoAbbName=&Month=&langcode=c', handler='HkStockInfoCnPageHandler')
    #seedTask = Task(1, url='https://sc.hkex.com.hk/gb/www.hkex.com.hk/chi/invest/company/profile_page_c.asp?WidCoID=00001&WidCoAbbName=&Month=&langcode=c', handler='HkStockInfoCnPageHandler')
    seedTask['key'] = '0000'
    m = WorkManager(seedTask, conf.iWorkThreadNum, conf.iParserThreadNum, False)
    m.start() 

#https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/chi/invest/company/profile_page_c.asp?WidCoID=08003&WidCoAbbName=&Month=&langcode=c
