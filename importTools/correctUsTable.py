#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-30 13:39:17 
# Copyright 2014 NONE rights reserved.


"""
by this prog, I import new data wa crawl into 
the table:


"""

import sys
import os
import util
import time
import re
import shutil
import json

import MySQLdb
import database
import db_config
_db = None
_all_classifications = {}

def update(allStocks):
    global _db
    allStocksDict = {}
    for stock in allStocks:
        allStocksDict[stock['symbol']] = stock

    for code in allStocksDict:
        stock = allStocksDict[code]
        stock['code'] = stock['symbol'].strip()
        jsonObj = json.loads(stock['json_info'])   
        jsonObj['code'] = stock['code']
        jsonObj['symbol'] = stock['code']
        oriSql = "update ori_stock_us set symbol=%s, json_info=%s where symbol=%s"
        _db.execute(oriSql, stock['code'], json.dumps(jsonObj), code)

def initDb():
    global _db
    try:
        _db = database.Connection(**(db_config.iz_db))
    except Exception, e:
        print "Exception:", e
        return False
    return True

def quitDb():
    _db.close()

def getAllStocks():
    sql = 'select * from ori_stock_us where mkt="us"'
    ret = _db.query(sql)
    return ret

if __name__ == '__main__':
    initDb()
    allStocks = getAllStocks()
    update(allStocks)
    quitDb()

