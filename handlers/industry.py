# -*- coding:utf-8  -*-

import xlrd
import xlwt
from dxb.handler import APIHandler
import libs.utils as utils

class IndustryListHandler(APIHandler):
    _model = 'industry.IndustryModel'
    def post(self):
        try:
            result = utils.init_response_data()
            workbook = xlrd.open_workbook(r'industry.xls')
            table= workbook.sheets()[0]
            nrows = table.nrows
            ncols = table.ncols
            _second_industry=[]
            for row in range(nrows):
                if  table.cell(row,0).value !='':
                    _second_industry=[]
                    industry_first=({
                        "mark":table.cell(row,0).value,
                        "first_industry":table.cell(row,4).value,
                        "enable_flag":1,
                    })
                    self.coll.insert_one(industry_first)
                elif table.cell(row,1).value !='':
                    second_industry={"code":str(table.cell(row,1).value).split('.')[0],"name":table.cell(row,4).value}
                    _second_industry.append(second_industry)
                    # second_industry[str(table.cell(row,1).value).split('.')[0]] = table.cell(row,4).value
                    industry_first["second_industry"]=_second_industry
                    self.coll.save(industry_first)

            result["data"]="ok"
        except Exception,e:
            result = utils.reset_response_data(0,unicode(e))
        self.finish(result)

    def get(self):
        try:
            result = utils.init_response_data()
            result["data"] =utils.dump(self.coll.find())
        except Exception,e:
            result = utils.re
        self.finish(result)


handlers = [
    (r"/api/industry/list",IndustryListHandler),
]
