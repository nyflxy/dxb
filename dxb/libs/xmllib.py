#coding=utf-8
import pdb
from xml.parsers.expat import ParserCreate

try:
    import json
except:
    import simplejson as json


class Xml2Json:
    LIST_TAGS = ['COMMANDS']

    def __init__(self, data=None):
        self._parser = ParserCreate()
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        self.result = None
        if data:
            self.feed(data)
            self.close()

    def feed(self, data):
        self._stack = []
        self._data = ''
        self._parser.Parse(data, 0)

    def close(self):
        self._parser.Parse("", 1)
        del self._parser

    def start(self, tag, attrs):
        tag = tag.lower()
        assert attrs == {}
        assert self._data.strip() == ''
        self._stack.append([tag])
        self._data = ''

    def end(self, tag):
        tag = tag.lower()
        last_tag = self._stack.pop()
        assert last_tag[0] == tag
        if len(last_tag) == 1:  # leaf
            data = self._data
        else:
            if tag not in Xml2Json.LIST_TAGS:
                # build a dict, repeating pairs get pushed into lists
                data = {}
                for k, v in last_tag[1:]:
                    if k not in data:
                        data[k] = v
                    else:
                        el = data[k]
                        if type(el) is not list:
                            data[k] = [el, v]
                        else:
                            el.append(v)
            else:  # force into a list
                data = [{k: v} for k, v in last_tag[1:]]
        if self._stack:
            self._stack[-1].append((tag, data))
        else:
            self.result = {tag: data}
        self._data = ''

    def data(self, data):
        self._data = data

if __name__ == '__main__':
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<RSP>
<DATA>

<ORDERLIST>
<ITEM>
<ORDERNO>订单号</ORDERNO>
<KEY>浙江虞南红食品有限公司</KEY>
<KEYTYPE>2</KEYTYPE>
<FINISHTIME>2014-07-09 18:35:59</FINISHTIME>
</ITEM>
</ORDERLIST>

<BASIC>
<ITEM>
<ENTNAME>浙江虞南红食品有限公司</ENTNAME>
<FRNAME>徐如根</FRNAME>
<REGNO>330682000053425</REGNO>
<REGCAP>2000.000000</REGCAP>
<REGCAPCUR>人民币</REGCAPCUR>
<ESDATE>2009-08-11</ESDATE>
<OPFROM>2009-08-11</OPFROM>
<OPTO>9999-09-09</OPTO>
<ENTTYPE>有限责任公司(自然人投资或控股)</ENTTYPE>
<ENTSTATUS>吊销</ENTSTATUS>
<CANDATE/>
<REVDATE>2013-11-22</REVDATE>
<DOM>上虞市章镇工业区</DOM>
<ABUITEM>无</ABUITEM>
<CBUITEM>板栗收购、销售。</CBUITEM>
<OPSCOPE>板栗收购、销售。</OPSCOPE>
<OPSCOANDFORM>板栗收购、销售。</OPSCOANDFORM>
<REGORG>上虞市工商行政管理局</REGORG>
<ANCHEYEAR>2010</ANCHEYEAR>
<INDUSTRYPHY>批发和零售业</INDUSTRYPHY>
<INDUSTRYCO>其他食品批发</INDUSTRYCO>
＜RECCAP＞1000.000000＜/RECCAP＞
＜ORIREGNO＞330682000053424＜/ORIREGNO＞
＜INDUSTRYPHYNAME＞科学研究、技术服务和地质勘查业＜/INDUSTRYPHYNAME＞
<ANCHEDATE> 2013-11-22</ANCHEDATE>
</ITEM>
</BASIC>

</DATA>
</RSP>"""
    result = Xml2Json(xml).result;
    print(result)