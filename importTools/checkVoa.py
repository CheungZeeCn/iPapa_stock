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


theTime = time.time( ) - 3600*24

outputPath = "../output/"
izhuomiDir = "/Users/cheungzee/opdir/bstrp/izhuomi-data"
monStr = time.strftime('%Y%m', time.localtime(theTime))
monUrl = 'izhuomi-data/' + monStr + '/'
copyToPath = os.path.join(izhuomiDir, monStr)

def check(dirName):
    #find today's keyfiles 
    tsDir = dirName
    report = {}
    okKeys = []
    for f in os.walk(os.path.join(outputPath, tsDir)):
        if os.path.basename(f[0]).startswith('_content_') and f[1] == []:
            error = []
            print f
            meta = None
            key = os.path.basename(f[0])
            if 'meta.json' not in  f[2]:
                error.append("no meta file !")
            else:
                meta = util.loadJsonFile(os.path.join(f[0], 'meta.json'))
                if 'isIgnore' in meta and meta['isIgnore'] == True:
                    report[key] = ["ignored:%s" % meta['ignoreMsg'], ]
                    okKeys.append(key)
                    continue
                    
            if 'content.html' not in  f[2]:
                error.append("no content file !")
            if 'content.mp3' not in f[2]:
                error.append("no mp3 file !")
            if '__zipPic__.jpg' not in f[2] and '__zipPic__.png' not in f[2]:
                error.append("no zipPic file !")

            meta = util.loadJsonFile(os.path.join(f[0], 'meta.json'))
            if meta:
                #check embPic:
                for picName in meta['embPics']:
                    if util.getUrlFileName(picName) not in f[2]:
                        error.append("no embPic %s !" % (util.getUrlFileName(picName)))
            if error != []:
                report[key] = error
            else:
                okKeys.append(key)
            
                

    return (report, okKeys)


def initDb():
    global _db
    try:
        _db = database.Connection(**iz_db)
    except Exception, e:
        print "Exception:", e
        return False
    return True

def quitDb():
    _db.close()

if __name__ == '__main__':
    report, okKeys = check(sys.argv[1])
    for k in report:
        print k, report[k]
    with open('doneKey.list', 'w') as f:
        for k in okKeys:
            f.write("%s\n"%k) 

