#!/usr/bin/env pytho
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.


from setup import iPapa
from bs4 import BeautifulSoup as BS
import os
import urlparse
from iTask import Task
import util
import re
import logging

class SzStockInfoMainPageHandler(object):
    def __init__(self):
        self.reXHX = re.compile(r"(%s)_+"%"_"*12)

    def parse(self, task):
        print "SzStockInfoMainPageHandler parse", task.url, task['key']
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        meta = {}
        if status == 'OK':
            key = task['key']
            keyOutputPath = os.path.join(iPapa.iTsOutputPath, 'sz')
            #siteTile 
            meta['siteTitle'] = ret['siteTitle']
            #title
            meta['title'] = ret['title']
            # url
            meta['url'] = task.url
            # date
            meta['date'] = ret['date']
            #contentPics
            #record and new task to download it
            meta['contentPics'] = ret['contentPics']
            meta['contentPicCaptions'] = ret['contentPicCaptions']
            meta['embPics'] = ret['embPics']
            #create new tasks here
            if len(ret['contentPics']) and len(ret['contentPicCaptions']):
                picUrl = ret['contentPics'][0]
                #only the first pic here, ignore others now
                dest = os.path.join(key, util.getUrlFileName(picUrl)) 
                newT = Task(-1, url=picUrl, handler='PicHandler', taskType='media', ref=task.url, dest=dest)  
                newT['key'] = task['key']
                newT['picType'] = 'contentPic'
                newTasks.append(newT)

            #for content, we store it 
            contentLoc = os.path.join(keyOutputPath, 'content.html')
            util.writeFile(contentLoc, ret['content'])
            # contentMp3 
            if 'contentMp3' in ret:
                url = ret['contentMp3']
                dest = os.path.join(key, util.getUrlFileName(url)) 
                newT = Task(-1, url=url, handler='AudioHandler', taskType='media', ref=task.url, dest=dest)  
                newT['key'] = task['key']
                newT['audioType'] = os.path.splitext(dest)[1].upper()
                newTasks.append(newT)
            elif 'contentMp3Page' in ret: #always be with big file, we ignore it 
                #url = ret['contentMp3Page']
                #newT = Task(-1, url=urlparse.urljoin(task.url, url), handler='ContentMp3PageHandler', ref=task.url,) 
                #newT['key'] = task['key']
                #newTasks.append(newT)
                task.status = 'ignore' 
                meta['isIgnore'] = True
                meta['ignoreMsg'] = "Audio file is too big, we should ignore this now."
                task.msg = 'Audio file is too big, we should ignore this now.' 
            else:
                #Failed
                task.status = 'failed' 
                task.msg = 'failed in Findding a Audio' 

            # download here 
            # embPics
            for embPic in ret['embPics']:
                picUrl = embPic
                #only the first pic here, ignore others now
                dest = os.path.join(key, util.getUrlFileName(picUrl)) 
                newT = Task(-1, url=picUrl, handler='PicHandler', taskType='media', ref=task.url, dest=dest)  
                newT['key'] = task['key']
                newT['picType'] = 'embPic'
                newTasks.append(newT)

            # store meta file
            metaLoc = os.path.join(keyOutputPath, 'meta.json') 
            if util.dump2JsonFile(meta, metaLoc) != True:
                task.status = 'failed'    

        else:
            task.status = 'failed'
        if task.status == 'ignore': 
            return {}
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        ret = {'excelUrl':''}
        try:
            soup = BS(page)           
            td = soup.find('td', align="right", width="60px", valign="bottom") 
            print td
            print td.a['href']
        except Exception, e:
            util.printException()
            return (None, e)
        return (ret, 'OK')


if __name__ == '__main__':
    data = open("cases/sz_stock_list_main.html").read()
    m = SzStockInfoMainPageHandler()
    ret, status =  m.parseContent(data)
    for k in ret:
        print 'key', k
        print ret[k]

