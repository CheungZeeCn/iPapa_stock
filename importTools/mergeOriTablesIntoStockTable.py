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
import logging
_db = None
_all_StocksDict = {}


def mergeAll():
    isOK = mergeUs() 
    if isOK == True:
        logging.info("merge US OK")
    else:
        logging.error("merge US FAILED")

    isOK = mergeSh() 
    if isOK == True:
        logging.info("merge sh OK")
    else:
        logging.error("merge sh FAILED")

    isOK = mergeSz() 
    if isOK == True:
        logging.info("merge sz OK")
    else:
        logging.error("merge sz FAILED")

    isOK = mergeHk() 
    if isOK == True:
        logging.info("merge hk OK")
    else:
        logging.error("merge hk FAILED")

    return True

def mergeHk():
    global _all_StocksDict
    isOK = True
    oriHkStocks = getAllOriHkStocks()
    updateCounter = 0
    insertCounter = 0
    for stock in oriHkStocks:
        code = stock['code']
        stock['mkt'] = 'hk'
        stock['nameCn'] = stock['cnName']
        stock['trade_market'] = 'HK'
        stock['market'] = 'hk'
        jsonStr = json.dumps(stock)

        if code not in _all_StocksDict:
            #print "insert", code, 'mkt'
            sql = "insert into stock(`code`, mkt, trade_market, market, plate, sector1, sector2, sector3, nameCn, json_info)"\
                "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            ret = _db.execute(sql, stock['code'], stock['mkt'], stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameCn'], jsonStr)
            insertCounter += 1
        else:
            #print "update", code, 'mkt'
            sql = "update stock set trade_market=%s, market=%s, plate=%s, sector1=%s, sector2=%s, sector3=%s, nameCn=%s, `json_info`=%s where `code`=%s and `mkt`=%s"
            ret = _db.execute(sql, stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameCn'], jsonStr, stock['code'], stock['mkt'])
            updateCounter += 1
    logging.info("update hk done: update %s, insert %s" % (updateCounter, insertCounter))
    return isOK

def mergeSz():
    global _all_StocksDict
    isOK = True
    oriSzStocks = getAllOriSzStocks()
    updateCounter = 0
    insertCounter = 0
    for stock in oriSzStocks:
        code = stock['code']
        stock['plate'] = 'main'
        stock['mkt'] = 'sz'
        stock['trade_market'] = 'A'
        stock['market'] = 'sz'
        stock['sector1'] = stock['sectorName']
        stock['sector2'] = stock['sectorName']
        stock['sector3'] = stock['sectorName']
        jsonStr = json.dumps(stock)

        if code not in _all_StocksDict:
            #print "insert", code, 'mkt'
            sql = "insert into stock(`code`, mkt, trade_market, market, plate, sector1, sector2, sector3, nameCn, json_info)"\
                "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            ret = _db.execute(sql, stock['code'], stock['mkt'], stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameCn'], jsonStr)
            insertCounter += 1
        else:
            #print "update", code, 'mkt'
            sql = "update stock set trade_market=%s, market=%s, plate=%s, sector1=%s, sector2=%s, sector3=%s, nameCn=%s, `json_info`=%s where `code`=%s and `mkt`=%s"
            ret = _db.execute(sql, stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameCn'], jsonStr, stock['code'], stock['mkt'])
            updateCounter += 1
    logging.info("update sz done: update %s, insert %s" % (updateCounter, insertCounter))
    return isOK

def mergeSh():
    global _all_StocksDict
    isOK = True
    oriShStocks = getAllOriShStocks()
    updateCounter = 0
    insertCounter = 0
    for stock in oriShStocks:
        code = stock['code']
        stock['plate'] = 'main'
        stock['mkt'] = 'sh'
        stock['trade_market'] = 'A'
        stock['market'] = 'sh'
        jsonStr = json.dumps(stock)

        if code not in _all_StocksDict:
            #print "insert", code, 'mkt'
            sql = "insert into stock(`code`, mkt, trade_market, market, plate, sector1, sector2, sector3, nameCn, json_info)"\
                "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            ret = _db.execute(sql, stock['code'], stock['mkt'], stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameCn'], jsonStr)
            insertCounter += 1
        else:
            #print "update", code, 'mkt'
            sql = "update stock set trade_market=%s, market=%s, plate=%s, sector1=%s, sector2=%s, sector3=%s, nameCn=%s, `json_info`=%s where `code`=%s and `mkt`=%s"
            ret = _db.execute(sql, stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameCn'], jsonStr, stock['code'], stock['mkt'])
            updateCounter += 1
    logging.info("update sh done: update %s, insert %s" % (updateCounter, insertCounter))
    return isOK

def mergeUs():
    global _all_StocksDict
    isOK = True
    oriUsStocks = getAllOriUsStocks()
    updateCounter = 0
    insertCounter = 0
    for stock in oriUsStocks:
        code = stock['symbol']
        stock['code'] = code
        sector1 = stock['sector'] if stock['sector'] != 'n/a' else ''
        sector2 = stock['industry'] if stock['industry'] != 'n/a' else ''
        stock['sector1'] = sector1
        stock['sector2'] = sector2
        stock['sector3'] = sector2
        stock['mkt'] = 'gb_'
        stock['market'] = ''
        stock['trade_market'] = 'US'
        stock['plate'] = 'main'

        jsonStr = json.dumps(stock)

        if code not in _all_StocksDict:
            #print "insert", code, 'mkt'
            sql = "insert into stock(`code`, mkt, trade_market, market, plate, sector1, sector2, sector3, nameEn, json_info)"\
                "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            ret = _db.execute(sql, stock['code'], stock['mkt'], stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameEn'], jsonStr)
            insertCounter += 1
        else:
            #print "update", code, 'mkt'
            sql = "update stock set mkt=%s, trade_market=%s, market=%s, plate=%s, sector1=%s, sector2=%s, sector3=%s, nameEn=%s, `json_info`=%s where `code`=%s and mkt='gb_'"
            ret = _db.execute(sql, stock['mkt'], stock['trade_market'], stock['market'], stock['plate'], stock['sector1'], stock['sector2'], stock['sector3'], stock['nameEn'], jsonStr, stock['code'])
            # print sql % (stock['sector1'], stock['sector2'], stock['sector3'], stock['nameEn'], jsonStr, stock['code']) + "",
            updateCounter += 1
    logging.info("update sh done: update %s, insert %s" % (updateCounter, insertCounter))
    return isOK

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
    sql = 'select * from stock'
    ret = _db.query(sql)
    return ret

def getAllOriUsStocks():
    sql = 'select * from ori_stock_us'
    ret = _db.query(sql)
    return ret

def getAllOriSzStocks():
    sql = 'select * from ori_stock_A_sz'
    ret = _db.query(sql)
    return ret

def getAllOriShStocks():
    sql = 'select * from ori_stock_A_sh'
    ret = _db.query(sql)
    return ret

def getAllOriHkStocks():
    sql = 'select * from ori_stock_hk'
    ret = _db.query(sql)
    return ret

if __name__ == '__main__':
    initDb()
    allStocks = getAllStocks()
    for stock in allStocks:
        _all_StocksDict[stock['code']] = stock
       
    util.initLog()
    mergeAll()
    quitDb()

