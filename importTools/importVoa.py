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

import MySQLdb
import database
import db_config
_db = None
_all_classifications = {}

theTime = time.time( ) - 3600*24

outputPath = "/Users/cheungzee/izhuomi/izhuomi/izhuomiAligner/output/"
izhuomiDir = "/Users/cheungzee/opdir/bstrp/izhuomi-data"
monStr = time.strftime('%Y%m', time.localtime(theTime))
monUrl = 'izhuomi-data/' + monStr + '/'
copyToPath = os.path.join(izhuomiDir, monStr)

def update():
    global _db, _all_classifications
    #find today's keyfiles 
    date = util.getDateStamp(theTime) 
    for f in os.walk(outputPath):
        if os.path.basename(f[0]).startswith('_content_') and f[1] == []:
            #print f
            key = os.path.basename(f[0])
            meta = util.loadJsonFile(os.path.join(f[0], 'meta.json'))
            if meta:
                #got cha
                classification = 'VOA, ' + meta['siteTitle'] 
                cId = 0
                #check classification
                if classification not in _all_classifications:
                    cId = insertClassification(classification, classification)
                    _all_classifications = getAllClassification()
                else:
                    cId = _all_classifications[classification]['id']
                name = meta['title'] 
                url = os.path.join(monUrl, key)
                ori_url = meta['url']
                ori_pub_date = meta['date']
                if re.match("\d+/\d+/\d+", ori_pub_date):
                    ori_pub_date = util.timeStr2timeStr(ori_pub_date, "%m/%d/%Y", "%Y-%m-%d")
                if 'content.jpg' in f[2]:
                    contentPic = 'content.jpg'
                    contentPicCaption = meta['contentPicCaptions'][0]
                elif 'content.png' in f[2]:
                    contentPic = 'content.png'
                    contentPicCaption = meta['contentPicCaptions'][0]
                else:
                    contentPic = None;
                    contentPicCaption = None;

                #for v in (classification, cId, name, url, ori_url, ori_pub_date, contentPic, contentPicCaption):
                #    #print v
                #    pass
                # cp
                dest = os.path.join(copyToPath, key)
                src = f[0]
                if os.path.isdir(dest):  
                    shutil.rmtree(dest) 
                shutil.copytree(f[0], dest) 
                # insert it
                #sql = "insert into %s(name, classification, url, ori_url, ori_pub_date, contentPic, contentPicCaption) "\
                #        "values('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                #        ('iz', name, classification, url, ori_url, ori_pub_date, contentPic, contentPicCaption)
                oriSql = "insert into iz_article(name, classification, classification_id, url, ori_url, ori_pub_date, "\
                        "contentPic, contentPicCaption) "\
                        " values(%s, %s, %s, %s, %s, %s, %s, %s)" 
                _db.execute(oriSql, name, classification, cId, url, ori_url, ori_pub_date, contentPic, contentPicCaption)

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
    _all_classifications = getAllClassification()
    update()
    ret = getAllClassification()
    quitDb()

