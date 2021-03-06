# coding: utf-8
import requests
import json
import time
import pandas as pd

from rrshare.rqUtil import rq_util_get_last_tradedate, rq_util_if_trade, rq_util_if_tradetime, rq_util_date_today

SWL1_INDEX = ('801010','801030','801040','801050','801080','801110','801120','801130','801140','801150','801160','801170','801180','801200','801210', \
              '801230','801710','801720','801730','801740','801750','801760','801770','801780','801790','801880','801890','801950','801960','801970','801980')

SWL2_INDEX = ('801012','801014','801015','801016','801017','801018','801032','801033','801034','801036','801037','801038','801039','801043','801044', \
            '801045','801051','801053','801054','801055','801056','801072','801074','801076','801077','801078','801081','801082','801083','801084','801085','801086', \
            '801092','801093','801095','801096','801101','801102','801103','801104','801111','801112','801113','801114','801115','801116','801124','801125','801126', \
            '801127','801128','801129','801131','801132','801133','801141','801142','801143','801145','801151','801152','801153','801154','801155','801156','801161', \
            '801163','801178','801179','801181','801183','801191','801193','801194','801202','801203','801204','801206','801218','801219','801223','801231','801711', \
            '801712','801713','801721','801722','801723','801724','801726','801731','801733','801735','801736','801737','801738','801741','801742','801743','801744', \
            '801745','801764','801765','801766','801767','801769','801782','801783','801784','801785','801881','801951','801952','801962','801963','801971','801972', \
            '801981','801982','801991','801992','801993','801994','801995')

# sw-cons
sw_cons_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Length": "34",
    "Content-Type": "text/plain; charset=UTF-8",
    # "Cookie": "ASP.NET_SessionId=i55eaz55142xdxfx0bkqp145",
    "Host": "www.swsindex.com",
    "Origin": "http://www.swsindex.com",
    "Referer": "http://www.swsindex.com/idx0210.aspx?swindexcode=801010",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "X-AjaxPro-Method": "ReturnContent",
}

# sw-url
sw_url = "http://www.swsindex.com/handler.aspx"

# sw-payload
swl_payload = {
    "tablename": "swzs",
    "key": "L1",
    "p": "1",
    "where": "L1 in()",
    "orderby": "",
    "fieldlist": "L1,L2,L3,L4,L5,L6,L7,L8,L11",
    "pagecount": "28",
    "timed": "",
}

payload = {
            'tablename': 'swzs',
            'key': 'L1',
            'p': f'{i}',
            'where': f"L1 in {SWL_INDEX}",  
             #SWL1_INDEX, SWL2_INDEX
            'orderby': '',
            'fieldlist': 'L1,L2,L3,L4,L5,L6,L7,L8,L11',
            'pagecount': '28',
            'timed': '{}'.format(int(time.time()*1000))
            ##????????????p??????????????????2??????timed????????????????????? time.time() ?????????????????????????????????????????????
            }

# sw-headers
sw_headers = {
    'Accept': 'application/json, text/javascript, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded',
    'DNT': '1',
    'Host': 'www.swsindex.com',
    'Origin': 'http://www.swsindex.com',
    'Pragma': 'no-cache',
    'Referer': 'http://www.swsindex.com/idx0120.aspx?columnid=8832',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

headers= {
            'Accept': 'application/json, text/javascript, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Length': '227',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'ASP.NET_SessionId=l0zdjg2sww1yrfitod5trjuq',
            'Host': 'www.swsindex.com',
            'Origin': 'http://www.swsindex.com',
            'Proxy-Connection': 'keep-alive',  
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
            }


class Swsindex(object):
    """http://www.swsindex.com/idx0120.aspx?columnid=8832#
    industry class:
    http://www.swsindex.com/downloadfiles.aspx?swindexcode=SwClass&type=530&columnid=8892

    get sw industry index class and realtime quote from swsindex.com by post method.
    """
    
    def __init__(self):
        self.url = 'http://www.swsindex.com/handler.aspx'
        self.headers = headers


    def get_swsindex_L1_realtime(self):
        result = []
        for i in range(1,3):
            postdata = payload.update({"where" : f"L1 in{SWL1_INDEX}"})
            print(postdata)
            self.headers['Referer'] = 'http://www.swsindex.com/idx0120.aspx?columnid=8832'
            #print(self.headers)
            req = requests.post(self.url, headers=self.headers, data=postdata)
            data = req.content.decode()
            data = data.replace("'",'"')
            data = json.loads(data)['root']
            #print(len(data))
            result.extend(data)
        df = pd.DataFrame(result)
        
        df.columns = ['index', 'name', 'pre_close', 'open', 'amount','high','low','close','vol' ]
        cols = ['pre_close', 'open', 'amount','high','low','close','vol']
        for i in cols:
            df[i] = pd.to_numeric(df[i], errors='coerce')
        df['name'] = df['name'].apply(lambda x : x.split()[0])
        #print(df.dtypes)
        df['pct_change'] = 0.00 if df['close'].values[0] == 0 else 100*(df['close']/ df['pre_close'] -1) 
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #trade_time = #TODO
        trade_time = date_time if rq_util_if_trade else rq_util_get_last_tradedate() # TODO
        print(trade_time)
        df['trade_date'] = trade_time 
        return df.round(2)

      
    def get_index_name(self, out_type=dict):
        
        data = self.get_swsindex_L1_realtime()[['index', 'name']]
        if out_type == dict:
            data.set_index('index', inplace=True)
            return data.to_dict()['name']
        
        return data 


    def get_swl1_class_one(self,index='801010'):
        """http://www.swsindex.com/idx0210.aspx?swindexcode=801010
        """
        self.headers['Referer'] = 'http://www.swsindex.com/idx0210.aspx?swindexcode={}'.format(index)
        result = []
        for i in range(1, 100):
            postdata={
            'tablename': 'SwIndexConstituents',
            'key': 'id',
            'p': '{}'.format(i),
            'where': 'SwIndexCode={} and IsReserve =0 and  NewFlag=1'.format(index),
            'orderby': 'StockCode, BeginningDate_0',
            'fieldlist': 'stockcode,stockname,newweight,beginningdate',
            'pagecount': '92',
            'timed': '{}'.format(int(time.time()*1000))
            }
            #print(postdata)
            
            req = requests.post(self.url, headers=self.headers, data=postdata)
            data = req.content.decode()
            data = data.replace("'",'"')
            data = json.loads(data)['root']
            #print(len(data))
            if not len(data):
                break
            result.extend(data)
        df = pd.DataFrame(result)
        df.drop(columns=['newweight','beginningdate'], inplace=True)
        df['index_name'] = self.get_index_name(out_type=dict)[index] + '_L1'
        df.rename(columns={'stockcode': 'code','stockname':'name'}, inplace=True)
        return df


    def get_swl1_class(self):
        L1_INDEX = list(SWL1_INDEX)
        df = pd.DataFrame()
        for l in L1_INDEX:
            print(f'index code: {l}')
            one = self.get_swl1_class_one(l)
            one['index'] = l
            df = df.append(one)
        return df

    
  def sw_index_second_spot() -> pd.DataFrame:
    """
    ??????????????????-??????????????????
    http://www.swsindex.com/idx0120.aspx?columnId=8833
    :return: ??????????????????-??????????????????
    :rtype: pandas.DataFrame
    """
    result = []
    for i in range(1, 8):
        payload = {
            "tablename": "swzs",
            "key": "L1",
            "p": "1",
            "where": "L1 in('801012','801014','801015','801016','801017','801018','801032','801033','801034','801036','801037','801038','801039','801043','801044', \
            '801045','801051','801053','801054','801055','801056','801072','801074','801076','801077','801078','801081','801082','801083','801084','801085','801086', \
            '801092','801093','801095','801096','801101','801102','801103','801104','801111','801112','801113','801114','801115','801116','801124','801125','801126', \
            '801127','801128','801129','801131','801132','801133','801141','801142','801143','801145','801151','801152','801153','801154','801155','801156','801161', \
            '801163','801178','801179','801181','801183','801191','801193','801194','801202','801203','801204','801206','801218','801219','801223','801231','801711', \
            '801712','801713','801721','801722','801723','801724','801726','801731','801733','801735','801736','801737','801738','801741','801742','801743','801744', \
            '801745','801764','801765','801766','801767','801769','801782','801783','801784','801785','801881','801951','801952','801962','801963','801971','801972', \
            '801981','801982','801991','801992','801993','801994','801995')",
            "orderby": "",
            "fieldlist": "L1,L2,L3,L4,L5,L6,L7,L8,L11",
            "pagecount": "124",
            "timed": "",
        }
        payload.update({"p": i})
        payload.update({"timed": int(time.time() * 1000)})
        r = requests.post(sw_url, headers=sw_headers, data=payload)
        data = r.content.decode()
        data = data.replace("'", '"')
        data = json.loads(data)
        result.extend(data["root"])
    temp_df = pd.DataFrame(result)
    temp_df["L2"] = temp_df["L2"].str.strip()
    temp_df.columns = ["index_code", "index_name", "pre_close", "open", "amount", "high", "low", "close", "vol"]
    """
    temp_df["?????????"] = pd.to_numeric(temp_df["?????????"])
    temp_df["?????????"] = pd.to_numeric(temp_df["?????????"])
    temp_df["?????????"] = pd.to_numeric(temp_df["?????????"])
    temp_df["?????????"] = pd.to_numeric(temp_df["?????????"])
    temp_df["?????????"] = pd.to_numeric(temp_df["?????????"])
    temp_df["?????????"] = pd.to_numeric(temp_df["?????????"])
    temp_df["?????????"] = pd.to_numeric(temp_df["?????????"])
    """
    return temp_df.round(2)    
      

if __name__ == '__main__':
    swi = Swsindex()
    #print(swi.url)
    #print(swi.headers)
    print(swi.get_swsindex_L1_realtime())  # ok
    print(swi.get_index_name())
    print(swi.get_swl1_class_one()) #pk
    #print(swi.get_swl1_class()) #ok
   
    pass
