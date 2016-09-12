# -*- coding: utf-8 -*-

"""
    alter by: daemon wnag
    alter on 2016-07-14
"""

import libs.modellib as model
import libs.utils as utils

class ProductModel(model.BaseModel,model.Singleton):
    __name = "dxb.product"

    def __init__(self):
        model.BaseModel.__init__(self,ProductModel.__name)

    def list(self,query_list={"enable_flag":1},page=1,page_size=15):
        length = self.get_coll().find(query_list).count()
        pager = utils.count_page(length,page,page_size)
        list = self.get_coll().aggregate([{"$match" : query_list},
                                               {"$sort":{"add_time" : -1}},
                                               {"$skip":pager['skip']},
                                               {"$limit":pager['page_size']}])
        return utils.dump(list),pager

    def create(self,product):
        self.vaildate(product)
        self.get_coll().save(product)

    def edit(self,product):
        if "_id" in product:
            _product = self.get_coll().find_one({"_id":product.get('_id','')})
        else:
            _product = self.get_coll().find_one({"sku":product.get('sku','')})

        if _product is None:
            raise ValueError(u"该商品不存在")
        _product.update(product)
        self.get_coll().save(_product)

    def vaildate(self,product):
        if self.is_exist(product['sku'],column='sku',is_objectid=False):
            raise ValueError(u"该SKU已经存在")

    def get_show_products(self,show_code):
        result = {}
        show_products = utils.dump(self.get_coll().find({"show_code":show_code,"enable_flag":1}))
        result['show_products'] = sorted(show_products,key = lambda x:x['sort'],reverse=True)
        if len(result['show_products']) != 0:
            result['show_code'] = show_code
            result['show_name'] = result['show_products'][0]['show_name']
        return result