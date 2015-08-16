#/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

from setup import iPapa
from bs4 import BeautifulSoup as BS
from iTask import Task
import urlparse
import os
import util
import time
import sys
import re

class ShStockBasicInfoHandler(object):
    def parse(self, task):
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        if status == 'OK':
            #dump list
            code = ret['stockBasicInfo']['code']
            keyOutputPath = iPapa.iTsOutputPath
            outputJsonLoc = os.path.join(keyOutputPath, 'sh_stock_basic_info_%s.json'%code)
            outputTxtLoc = os.path.join(keyOutputPath, 'sh_stock_basic_info_%s.txt'%code)
            if util.dump2JsonFile(ret['stockBasicInfo'], outputJsonLoc) != True:
                task.status = 'failed'

            if util.dumpDict2TxtFile(ret['stockBasicInfo'], outputTxtLoc) != True:
                task.status = 'failed'
        else:
            task.status = 'failed'
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        page = page.decode('gbk')
        ret = {'stockBasicInfo':{}, 'stockOtherInfo':{}}
        transMapCn2En = {
            u'公司代码': 'compCode',
            u'注册地址': 'registerAddr',
            u'法定代表人': 'legalRepresentative',
            u'董事会秘书姓名': 'boardSecretary',
            u'E-mail': 'E-mail',
            u'联系电话': 'phone',
            u'网址':'website',
            u'SSE行业': 'sseSector',
            u'是否上证180样本股': 'isSh180',
            u'是否境外上市': 'isOverseasListing',
            u'境外上市地': 'OverseasListingPlace'
        }

        try:
            soup = BS(page)           
            titleSpan = soup.find('span',  class_ ='pagetitle' ) 
            br = titleSpan.find('br')
            cmpNameAndCode = br.previous_element
            cmpName, code = re.split("\s+", cmpNameAndCode.strip())
            table = soup.find('table', width="100%", cellspacing="5", cellpadding="0", border="0")
            contentTd = table.find('td', class_="content", width="100%", valign="top")
            #contentTableList = contentTd.find_all('table', class="content", width="100%", bgcolor="#FFFFFF", align="center")
            tdList = contentTd.find_all('td', class_="content_b")
            for td in tdList:
                key = re.sub(r"\s+", "", td.text.strip().strip(':'))
                value = td.find_next_sibling('td').text.strip()
                if key == u'股票代码(A股/B股)':
                    valueList = re.split(r"\s*/\s*", value)
                    ret['stockBasicInfo']['code'] = valueList[0]
                    if len(valueList) == 1 or valueList[1] == '-':
                        ret['stockBasicInfo']['B_code'] = ''
                    else:
                        ret['stockBasicInfo']['B_code'] = valueList[1]
                elif key == u'上市日(A股/B股)':
                    valueList = re.split(r"\s*/\s*", value)
                    ret['stockBasicInfo']['A_IPO_date'] = valueList[0]
                    if len(valueList) == 1 or valueList[1] == '-':
                        ret['stockBasicInfo']['B_IPO_date'] = ''
                    else:
                        ret['stockBasicInfo']['B_IPO_date'] = valueList[1]
                elif key == u'可转债简称（代码）':
                    valueListMatch = re.search(ur"(\.+)\s*（(.+)）", value)
                    if valueListMatch != None:
                        groups = valueListMatch.groups()
                        ret['stockBasicInfo']['convertibleBondAbbr'] = groups[0]
                        ret['stockBasicInfo']['convertibleBondCode'] = groups[1]
                    else:
                        ret['stockBasicInfo']['convertibleBondAbbr'] = ''
                        ret['stockBasicInfo']['convertibleBondCode'] = ''
                elif key == u'公司简称(中/英)':
                    valueList = re.split(r"\s*/\s*", value)
                    ret['stockBasicInfo']['compNameAbbr'] = valueList[0]
                    if len(valueList) == 1 or valueList[1] == '-':
                        ret['stockBasicInfo']['compNameAbbrEn'] = ''
                    else:
                        ret['stockBasicInfo']['compNameAbbrEn'] = valueList[1]
                elif key == u'公司全称(中/英)':
                    valueList = value.split("\n")
                    ret['stockBasicInfo']['compNameCn'] = valueList[0]
                    ret['stockBasicInfo']['compNameEn'] = valueList[1]
                elif key == u'通讯地址（邮编）':
                    value = value.replace("\n", "")
                    valueListMatch = re.search(ur"(\.+)\s*（(.+)）", value)
                    if valueListMatch != None:
                        groups = valueListMatch.groups()
                        ret['stockBasicInfo']['contactAddr'] = groups[0]
                        ret['stockBasicInfo']['postcode'] = groups[1]
                    else:
                        ret['stockBasicInfo']['contactAddr'] = ''
                        ret['stockBasicInfo']['postcode'] = ''
                elif key.startswith(u'CSRC行业'):
                    valueList = re.split(r"\s*/\s*", value)
                    ret['stockBasicInfo']['sector'] = "/".join(valueList)
                    ret['stockBasicInfo']['sector1'] = valueList[0]
                    ret['stockBasicInfo']['sector2'] = valueList[1]
                    if valueList[2] == '-':
                        ret['stockBasicInfo']['sector3'] = valueList[1]
                    else:
                        ret['stockBasicInfo']['sector3'] = valueList[2]
                elif key == u'所属省/直辖市':
                    valueList = re.split(r"\s*/\s*", value)
                    ret['stockBasicInfo']['province'] = valueList[0]
                    if len(valueList) == 1 or valueList[1] == '-':
                        ret['stockBasicInfo']['city'] = ''
                    else:
                        ret['stockBasicInfo']['city'] = valueList[1]
                elif key == u'A股状态/B股状态':
                    valueList = re.split(r"\s*/\s*", value)
                    ret['stockBasicInfo']['A_status'] = valueList[0]
                    if len(valueList) == 1 or valueList[1] == '-':
                        ret['stockBasicInfo']['B_status'] = ''
                    else:
                        ret['stockBasicInfo']['B_status'] = valueList[1]
                else: 
                    if key in transMapCn2En:
                        ret['stockBasicInfo'][transMapCn2En[key]] = value.strip()
                    else:
                        ret['stockBasicInfo'][key] = value.strip()
        except Exception, e:
            util.printException()
            return (None, e)
        return (ret, 'OK')


if __name__ == '__main__':
    m = ShStockBasicInfoHandler()
    fdata = open('cases/sh_stock_info.html').read()
    print m.parseContent(fdata)

