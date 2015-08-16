#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.


from bs4 import BeautifulSoup as BS
import os
import util
import time
import re
import logging
import sys
import json

import MySQLdb
import database
import db_config

util.initLog()

_db = None
_all_classifications = {}

theTime = time.time( ) - 3600*24
dayStr = time.strftime('%Y%m%d', time.localtime(theTime))


class ShStockTableImporter(object):
    def __init__(self):
        self.allStockList = []
        self.allStockDict = {}
        self.importStockDict = {}

    def getAllAstocks(self):
        global _db
        sql = 'select * from ori_stock_A_sh'              
        return _db.query(sql)

    def importDir(self, inputDir):
        global _db
        self.allStockList = self.getAllAstocks()
        self.allStockDict = {}
        for s in self.allStockList:
            self.allStockDict[s['code']] = s

        for f in os.walk(inputDir):
            loc = f[0] 
            locName = os.path.basename(loc)
            if locName.startswith(dayStr):
                logging.info("Importing dir: %s" %(f[0]))
                for fname in f[2]:     
                    if fname.startswith('sh_stock_list') and \
                        fname.endswith('.json'):
                        self.addStockListByFile(os.path.join(f[0],fname))
                        pass
                    elif fname.startswith('sh_stock_basic_info') and \
                        fname.endswith('.json'):
                        self.addStockInfoByFile(os.path.join(f[0],fname))
        self.dumpIntoMysql()

    def dumpIntoMysql(self):
        for code in self.importStockDict:
            stock = self.importStockDict[code]
            stock['sectorName'] = stock['sector3']
            jsonStr = json.dumps(stock)
            if code not in self.allStockDict:
                sql = 'insert into ori_stock_A_sh(`code`, `nameCn`, `comp_code`,'\
                        '`comp_name_cn`, `comp_name_en`, `sectorName`, '\
                        '`sector`, `sector1`, `sector2`, `sector3`, '\
                        '`province`, `city`, `json_info`) values('\
                        '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' 
                 
                print sql
                execReturn = _db.execute(sql, code, stock['nameCn'], stock['compCode'], 
                    stock['compNameCn'], stock['compNameEn'],
                    stock['sectorName'], stock['sector'], 
                    stock['sector1'], stock['sector2'], stock['sector3'], 
                    stock['province'], stock['city'], jsonStr)
                print execReturn

            else:
                jsonStr = json.dumps(stock)
                sql = 'update ori_stock_A_sh set `nameCn`=%s, `comp_code`=%s,'\
                        '`comp_name_cn`=%s, `comp_name_en`=%s, `sectorName`=%s,'\
                        '`sector`=%s,`sector1`=%s,`sector2`=%s,`sector3`=%s,'\
                        '`province`=%s, `city`=%s, `json_info`=%s where `code`=%s'
                print sql
                execReturn = _db.execute(sql, stock['nameCn'], stock['compCode'], 
                    stock['compNameCn'], stock['compNameEn'],
                    stock['sectorName'], stock['sector'], 
                    stock['sector1'], stock['sector2'], stock['sector3'], 
                    stock['province'], stock['city'], jsonStr, code)
                print execReturn


    def addStockListByFile(self, fname):
        stockList = util.loadJsonFile(fname)
        for stock in stockList:
            code = stock['code'] 
            name = stock['name']
            if code not in self.importStockDict:
                self.importStockDict[code] = {}
            self.importStockDict[code]['name'] = name
            self.importStockDict[code]['nameCn'] = name
    
    def addStockInfoByFile(self, fname):
        stockInfo = util.loadJsonFile(fname)
        code = stockInfo['code']   
        if code not in self.importStockDict:
            self.importStockDict[code] = {}
        self.importStockDict[code].update(stockInfo)
        

    

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

if __name__ == '__main__':
    initDb()
    inputDir = sys.argv[1]
    impObj = ShStockTableImporter()
    impObj.importDir(inputDir)
    quitDb()
