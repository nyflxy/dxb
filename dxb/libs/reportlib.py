
# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-04-26
#
from tornado.options import options
import utils
import dxb.consts as consts
import xlwt
import os.path
import re
import time
import os
import pdb


tall_style = xlwt.easyxf('font:height 300,bold true, name Arial, colour_index black;borders: left 1,right 1,top 1,bottom 1; align: wrap on, vert center, horiz center;')#报表大标题样式
styleTitle = xlwt.easyxf('font:bold true, name Arial, colour_index black;borders: left 1,right 1,top 1,bottom 1; align: wrap on, vert center, horiz center;')#报表标题行样式
styleContext = xlwt.easyxf(' align: vert center, horiz center;borders: left 1,right 1,top 1,bottom 1')#报表内容样式

def export_excel(report_china_name=[],result=[],fieldlist=[],namelist=[],addfieldlist=[]):
    '''公用报表导出功能
    report_china_name : 报表中文名
    result : 数据集
    fieldlist : 字段列表 如遇（表中表用字典表示如{"order_goods":["sku","goods_name"]} ）
    namelist : 字段中文列表
    addfieldlist : 生成数据集之后需要增加的字段（注意要用小写）
    '''
    if(len(fieldlist) <= 0 or len(namelist) <= 0):
        return

    file_paths = []
    file_names = []

    report = xlwt.Workbook(encoding='utf-8')

    if(len(report_china_name) > 0):
        titleCount = 0
        for china_name in report_china_name: #大标题
            widths = []
            result_add = []
            if(len(addfieldlist) > 0 ):
                for g in result[titleCount]:
                    for addfield in addfieldlist[titleCount]:
                        g[addfield + '_desc'] = consts.get_status_from_value(getattr(consts,addfield.upper()),g[addfield])
                    result_add.append(g)
                result[titleCount] = result_add


            sheet =  report.add_sheet(china_name,cell_overwrite_ok=True)
            i = 0
            r = 0
            if(type(namelist[titleCount][0]) == list):
                sheet.write_merge(0,0,0,len(namelist[titleCount][0])-1,china_name,tall_style)
                lens = len(namelist[titleCount])
                r = lens - 1
                for lens_num in range(0,lens):
                    i = 0
                    oneNameList = namelist[titleCount][lens_num]
                    lastOneName = ""
                    k = 0
                    num = 0
                    for oneName in oneNameList:
                        widths.append(5)#设置默认值
                        flag = False
                        for len_num in range(lens_num+1,lens):
                            nameLists = namelist[titleCount][len_num]
                            if nameLists[num] == oneName:
                                flag = True
                        if flag :
                            sheet.write_merge(lens_num+1,lens_num+1+lens-1,i,i,oneName,styleTitle)
                        if oneName != lastOneName:
                            if k > 0:
                                sheet.write_merge(lens_num+1,lens_num+1,i-k-1,i-1,lastOneName,styleTitle)
                            else:
                                sheet.write(lens_num+1,i,oneName,styleTitle)
                            k = 0
                            widths[i]=calcalateLen(oneName,widths[i])#列宽
                        else:
                            k += 1
                            sheet.write_merge(lens_num+1,lens_num+1,i-k,i,lastOneName,styleTitle)
                        i += 1
                        lastOneName = oneName

                        num += 1
            else:
                sheet.write_merge(0,0,0,len(namelist[titleCount])-1,china_name,tall_style)
                for name in namelist[titleCount]: #当行标题行
                    widths.append(5)#设置默认值
                    sheet.write(1,i,name,styleTitle)
                    widths[i]=calcalateLen(name,widths[i])#列宽
                    i = i + 1
            i = 2 + r#行
            sheet.panes_frozen= True # 固定表头
            sheet.horz_split_pos= i # horz_split_pos行用 vert_split_pos 列用
            num = 2#行号
            for r in result[titleCount]:#结果集
                height = 0#用于合并list
                height2 = 0
                k = 1#列
                for field in fieldlist[titleCount]:#计算出合并单元格列
                    if(type(field) == dict):
                        for fe in field: #字典型数据列
                            if(type(r[fe]) == list): #字典型数据列对应的list对象
                                height = len(r[fe]) - 1
                            if(type(r[fe]) == dict):
                                height2

                sheet.write_merge(i,i+height,0,0,num-1,styleContext)
                for field in fieldlist[titleCount]:#数据列
                    if(type(field) != dict):#非字典型数据列
                        p = r.get(field,'')
                        if("+" in field): #单个列包含字段相加
                            gs =  field.split("+")
                            p = reduce(lambda x,y : x + y ,[r.get(gg,'') for gg in gs])

                        sheet.write_merge(i,i + height ,k,k,p,styleContext)
                        widths[k]=calcalateLen(p,widths[k]);#列宽
                        k = k + 1
                    else:
                        for fe in field: #字典型数据列
                            for fie_list in field[fe]: #字典型数据列对应的字段
                                j = i
                                s = r[fe]
                                if(type(r[fe]) == list): #字典型数据列对应的list对象
                                    for g in r[fe]:#循环list对象
                                        if("*" in fie_list): #循环单个列包含字段相乘算法
                                            gs =  fie_list.split("*")
                                            p = reduce(lambda x,y : x * y,[g[gg] for gg in gs])
                                            sheet.write(j,k,p,styleContext)
                                            widths[k]=calcalateLen(p,widths[k]);#列宽
                                        elif("+" in fie_list): #循环单个列包含字段相加
                                            gs =  fie_list.split("+")
                                            p = reduce(lambda x,y : x + y ,[g[gg] for gg in gs])
                                            sheet.write(j,k,p,styleContext)
                                            widths[k]=calcalateLen(p,widths[k]);#列宽
                                        else:
                                            if(fie_list in "goods_type"): #循环单个列字典查找中文名
                                                sheet.write(j,k,options.goods_type[g.get(fie_list,"")],styleContext)
                                                widths[k]=calcalateLen(options.goods_type[g.get(fie_list,"")],widths[k]);#列宽
                                            else: #循环单个列
                                                sheet.write(j,k,g.get(fie_list,""),styleContext)
                                                widths[k]=calcalateLen(g.get(fie_list,""),widths[k]);#列宽
                                        j = j + 1
                                elif(type(r[fe]) == dict): #字典型数据列对应的字典对象
                                    if("+" in fie_list): #循环单个列包含字段相加
                                            gs =  fie_list.split("+")
                                            p = reduce(lambda x,y : x + y ,[r[fe].get(gg,'') for gg in gs])
                                            sheet.write_merge(i,i + height,k,k,p,styleContext)
                                            widths[k]=calcalateLen(p,widths[k]);#列宽
                                    else:
                                        sheet.write_merge(i,i + height,k,k,r[fe].get(fie_list,''),styleContext)
                                        widths[k]=calcalateLen(r[fe].get(fie_list,''),widths[k]);#列宽
                                k = k + 1
                i = i + height + 1
                num = num + 1
            for i in range(len(widths)):#设置列宽
                width = 256 * widths[i]
                if width >= 65536:
                    width = 60000
                sheet.col(i).width = width
            titleCount = titleCount + 1

        file_name ='%s.xls'% china_name
        path = os.path.join(options['file_download_store_url'])
        file_path = os.path.join(path,file_name)
        if not os.path.exists(path):
            os.makedirs(path)
        report.save(file_path)
        file_paths.append(file_path)
        file_names.append(file_name)
    result = {"file_path":file_paths,"filename":file_names,"report_data":report}
    return result


def calcalateLen(param,len):
    """
    :rtype: 调整报表宽度
    """
    sum = 0
    if(param != ''):
        if(type(param) != str):
            param = str(param)
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        for l in list(param):
            match = zhPattern.search(l)
            if match:
                sum = sum + 2
            else:
                sum = sum + 1
        if(sum > len):
            return sum
    return len