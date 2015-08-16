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
from bs4 import BeautifulSoup as BS

import MySQLdb
import database
import db_config
_db = None
_all_classifications = {}

theTime = time.time( ) - 3600*24

outputPath = "/Users/cheungzee/izhuomi/izhuomi/izhuomiAligner/output/"
izhuomiDir = "/Users/cheungzee/opdir/bstrp/izhuomi-data"
izhuomiBase = "/Users/cheungzee/opdir/bstrp/"
monStr = time.strftime('%Y%m', time.localtime(theTime))
monUrl = 'izhuomi-data/' + monStr + '/'
copyToPath = os.path.join(izhuomiDir, monStr)

def update():
    global _db, _all_classifications
    '''
                oriSql = "insert into iz_article(name, classification, classification_id, url, ori_url, ori_pub_date, "\
                        "contentPic, contentPicCaption) "\
                        " values(%s, %s, %s, %s, %s, %s, %s, %s)" 
                _db.execute(oriSql, name, classification, cId, url, ori_url, ori_pub_date, contentPic, contentPicCaption)
    '''
    sql = "select * from iz_article"

    ret = _db.query(sql)
    for i in ret:
        filePath = os.path.join(izhuomiBase, i['url'], 'content.html')
        print filePath
        fText = ''
        with open(filePath) as f:
            fText = f.read()
        soup = BS(fText) 
        ret = soup.find_all('p')
        ab = '' 


        for p in ret[0:4]:
            if 'VOA' not in p.text and "I'm" not in p.text:
                ab += p.text.replace("\n", '')    
        rIndex = ab[:256].rfind(" ")
        ab = ab[:rIndex] 
        #update it
        sql = "UPDATE `iz`.`iz_article` SET `abstract`=%s WHERE `id`=%s" 
        _db.execute(sql, ab, i['id'])
          


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

def insertClassification(name, nameCn):
    print "增加分类:", name, nameCn
    sql = 'insert into iz_classifications(`classification`, `classification_cn`) values(%s, %s)'
    return _db.execute(sql, name, nameCn)


def getAllClassification():
    sql = 'select * from iz_classifications'
    ret = _db.query(sql)
    classifications = {}
    for c in ret:
        classifications[c['classification']] = c
    return classifications

if __name__ == '__main__':
    initDb()
    update()
    quitDb()

