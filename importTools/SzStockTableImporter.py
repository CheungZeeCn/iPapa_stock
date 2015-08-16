#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.


from bs4 import BeautifulSoup as BS
import os
import util
import re
import logging
import sys
import json

import MySQLdb
import database
import db_config
_db = None
_all_classifications = {}

class SzStockTableImporter(object):
    def importFile(self, fileName):
        data = open(fileName).read()
        ret, status = self.parseContent(data.decode('gbk'))
        if status != 'OK':
            return False
        #update A only
        allStockList = self.getAllAstocks()
        allStockDict = {}
        for s in allStockList:
            allStockDict[s['code']] = s

        for stock in ret['stockList']:
            code = stock['code']
            execReturn = 0
            if code != '': # "A market" stock
                if code not in allStockDict:
                    jsonStr = json.dumps(stock)
                    sql = 'insert into ori_stock_A_sz(`code`, `nameCn`, `comp_code`,'\
                            '`comp_name_cn`, `comp_name_en`, `sectorName`, `sectorCode`,'\
                            '`sector`, `region`, `province`, `city`, `json_info`) values('\
                            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' 
                     
                    execReturn = _db.execute(sql, code, stock['nameCn'], stock['compCode'], 
                        stock['compNameCn'], stock['compNameEn'],
                        stock['sectorName'], stock['sectorCode'], 
                        stock['sector'], stock['region'], 
                        stock['province'], stock['city'], jsonStr)
                else:
                    jsonStr = json.dumps(stock)
                    sql = 'update ori_stock_A_sz set `nameCn`=%s, `comp_code`=%s,'\
                            '`comp_name_cn`=%s, `comp_name_en`=%s, `sectorName`=%s,'\
                            ' `sectorCode`=%s,`sector`=%s, `region`=%s,'\
                            ' `province`=%s, `city`=%s, `json_info`=%s where `code`=%s'
                    execReturn = _db.execute(sql, stock['nameCn'], stock['compCode'], 
                        stock['compNameCn'], stock['compNameEn'],
                        stock['sectorName'], stock['sectorCode'], 
                        stock['sector'], stock['region'], 
                        stock['province'], stock['city'], jsonStr, code)
            
    def getAllAstocks(self):
        global _db
        sql = 'select * from ori_stock_A_sz'              
        return _db.query(sql)

    def parseContent(self, page):
        transMapCn2En = { \
            u'公司代码': 'compCode',
            u'公司简称': 'compNameAbbr',
            u'公司全称': 'compNameCn',
            u'英文名称': 'compNameEn',
            u'注册地址': 'regAddr',
            u'A股代码' : 'code',
            u'A股简称' : 'nameCn',
            u'A股上市日期': 'A_IPO_date',
            u'A股总股本': 'A_totalShares',
            u'A股流通股本':'A_circulationStock',
            u'B股代码': 'B_code',
            u'B股简称': 'B_nameCn',
            u'B股上市日期': 'B_IPO_date',
            u'B股总股本': 'B_totalShares',
            u'B股流通股本': 'B_circulationStock',
            u'地区': 'region',
            u'省份': 'province',
            u'城市': 'city',
            u'所属行业': 'sector',
            u'公司网址': 'webSite'
        }
        transMapEn2Cn = {}
        for k in transMapCn2En:
            transMapEn2Cn[transMapCn2En[k]] = k

        ret = {'stockList':[], 'headerList':[]}
        try:
            reEmpty = re.compile(r'\s+')
            soup = BS(page)           
            table = soup.find('table')
            trList  = table.find_all('tr')
            trHeader = trList[0]

            thList = trHeader.find_all('td')
            headerList = [ reEmpty.sub('', td.text.strip()) for td in thList ]
            ret['headerList'] = headerList

            for tr in trList[1:]: # for each stock
                tdList = tr.find_all('td')
                tdTextList = [ td.text.strip() for td in tdList ]
                
                stockDict = {}
                for i in range(len(tdTextList)):
                    enKey = transMapCn2En[headerList[i]]
                    value = tdTextList[i]
                    if enKey in ('A_totalShares', 'A_circulationStock', 'B_totalShares', 'B_circulationStock'):# pull out the ','
                        value = value.replace(",", "")
                    stockDict[enKey]  = tdTextList[i]        
                    
                #J 金融业
                if 'sector' in stockDict:
                    theSector = stockDict['sector']
                    stockDict['sectorCode'] = theSector[0]
                    stockDict['sectorName'] = theSector[1:]

                ret['stockList'].append(stockDict)
        except Exception, e:
            util.printException()
            return (None, e)

        return (ret, 'OK')


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
    inputFile = sys.argv[1]
    impObj = SzStockTableImporter()
    impObj.importFile(inputFile)
    quitDb()
    
    




