# coding: utf-8

from tkinter import PAGES
from tracemalloc import start
import requests
import json
import time
import pandas as pd
from rrshare.rqUtil import (rq_util_get_last_tradedate, rq_util_if_trade, rq_util_if_tradetime, is_tradeday_and_market_opened,
                            rq_util_get_trade_range, rq_util_date_today, is_before_tradetime_secs_cn, is_trade_time_secs_cn)
from rrshare.rqUtil.rqParameter import startDate


class Swsindex(object):
    """
    swl1_realtime :
    http://www.swsindex.com/idx0120.aspx?columnid=8832#
    industry class:
    http://www.swsindex.com/downloadfiles.aspx?swindexcode=SwClass&type=530&columnid=8892

    get sw industry index class and realtime quote from swsindex.com by post method.
    swl2 reltime spot: http://www.swsindex.com/idx0120.aspx?columnId=8833
    swl1_daily: http://www.swsindex.com/idx0130.aspx?columnid=8838#
    swl2_daily: http://www.swsindex.com/idx0200.aspx?columnid=8839&type=Day#
    """
    
    def __init__(self):
        
        self.url = 'http://www.swsindex.com/handler.aspx'
        self.headers = {
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
        
        self.swl1 = ('801010','801030','801040','801050','801080','801110','801120','801130','801140', \
                    '801150','801160','801170','801180','801200','801210','801230','801710','801720','801730', \
                '801740','801750','801760','801770','801780','801790','801880','801890','801950','801960','801970','801980')
        
        self.swl2 = ('801011','801012','801014','801015','801016','801017','801018','801019','801032','801033', \
            '801034','801036','801037','801038','801039','801043','801044','801045','801051','801053','801054',\
                '801055','801056','801072','801074','801076','801077','801078','801081','801082','801083','801084', \
            '801085','801086','801092','801093','801095','801096','801101','801102','801103','801104','801111','801112', \
            '801113','801114','801115','801116','801117','801124','801125','801126','801127','801128','801129','801131', \
            '801132','801133','801141','801142','801143','801145','801151','801152','801153','801154','801155','801156', \
            '801161','801163','801178','801179','801181','801183','801191','801193','801194','801202','801203','801204', \
            '801206','801207','801216','801217','801218','801219','801223','801231','801711','801712','801713','801721', \
            '801722','801723','801724','801726','801731','801733','801735','801736','801737','801738','801741','801742', \
            '801743','801744','801745','801764','801765','801766','801767','801768','801769','801782','801783','801784', \
            '801785','801786','801881','801951','801952','801961','801962','801963','801971','801972','801981','801982', \
            '801983','801991','801992','801993','801994','801995')
       
        self.page_swl1_realtime_nums = len(self.swl1) // 20 + 1
        self.page_swl2_realtime_nums = len(self.swl2) // 20 + 1


    def fetch_swsindex_L1_L2_realtime(self, level="L1"):
        """ level = L1 or L2  data from swsindex.com"""
        if level == "L1":
            page_nums = self.page_swl1_realtime_nums
            swl = self.swl1
            self.headers['Referer'] = 'http://www.swsindex.com/idx0120.aspx?columnid=8832'
        if level == "L2":
            page_nums = self.page_swl2_realtime_nums
            swl = self.swl2
            self.headers['Referer'] = 'http://www.swsindex.com/idx0120.aspx?columnid=8833'
        
        result = []
        for i in range(1,page_nums + 1):
            postdata = {
            'tablename': 'swzs',
            'key': 'L1',
            'p': '{}'.format(i),
            'where': f"L1 in{swl}",
            'orderby': '',
            'fieldlist': 'L1,L2,L3,L4,L5,L6,L7,L8,L11',
            'pagecount': f'{len(swl)}',
            'timed': '{}'.format(int(time.time()*1000))
            #其中页码p是变量，一共2页。timed也是变量，通过 time.time() 来获取时间戳然后将取值到千分位
            }
            req = requests.post(self.url, headers=self.headers, data=postdata)
            data = req.content.decode()
            data = data.replace("'",'"')
            data = json.loads(data)['root']
            #print(len(data))
            result.extend(data)
        
        df = pd.DataFrame(result)
        df.columns = ['index', 'name', 'pre_close', 'open', 'amount','high','low','close','vol' ]
        df['name'] = df['name'].apply(lambda x : x.split()[0])
        cols = ['pre_close', 'open', 'amount','high','low','close','vol']
        for i in cols:
            df[i] = pd.to_numeric(df[i], errors='coerce')
            
        df_swl = df.copy()
        df_swl["index_symbol"] = df_swl["index"]
        df_swl["index_code"] = df_swl["index"] + ".SI"
        df_swl["level"] = f"{level}"
        df_swl["name_level"] = df_swl["name"] + "_" + df_swl["level"]
        
        #print(df.dtypes)
        df_swl['change_pct'] = 0.00 if df_swl['close'].values[0] == 0 else 100*(df_swl['close'] / df_swl['pre_close'] -1) 
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        trade_time = date_time   if  is_tradeday_and_market_opened()  else rq_util_get_last_tradedate()
        df_swl['trade_date'] = trade_time
        df_swl = df_swl[['index_symbol', 'name', 'trade_date','pre_close', 'open', 'high','low','close','change_pct', \
            'vol','amount','index_code','name_level','level']]
        return df_swl.round(2)

        
    def fetch_swsindex_L1_L2_daily(self,level="L1", start_date=None, end_date=None,trade_date=None):
        """sw index daily L1 or L2 , just input trade_date or  start_date and end_date,data from swsindex.com  
        """
        if not trade_date:
            if not start_date:
                start_date = startDate
            if not end_date:
                end_date = rq_util_get_last_tradedate()
            
        if trade_date:
            start_date = trade_date
            end_date = trade_date   
        if level == "L1":
            page_nums = self.page_swl1_realtime_nums
            swl = self.swl1
            self.headers['Referer'] = 'http://www.swsindex.com/idx0200.aspx?columnid=8838&typeDay'
        if level == "L2":
            page_nums = self.page_swl1_realtime_nums
            swl = self.swl2
            self.headers['Referer'] = 'http://www.swsindex.com/idx0200.aspx?columnid=8839&typeDay'
              
        PAGES = len(swl) * len(rq_util_get_trade_range(start_date, end_date)) 
        page_nums = PAGES // 20 + 1
        #print(PAGES, page_nums)
        
        result = []
        for i in range(1,page_nums + 1):
            print(f"fecth data from {self.headers['Referer']} pages:  {i} totla pages: {page_nums}")
            postdata = {
            'tablename':'swindexhistory',
            'key': 'id',
            'p': '{}'.format(i),
            'where':  f"  swindexcode in{swl}  and BargainDate>='{start_date}' and  BargainDate<='{end_date}'",
            'orderby': 'swindexcode asc,BargainDate_1', 
            #"SwIndexCode,SwIndexName,BargainDate,CloseIndex,BargainAmount,Markup,TurnoverRate,PE,PB,MeanPrice,BargainSumRate,NegotiablesShareSum,NegotiablesShareSum2,DP",
            'fieldlist': 'SwIndexCode,SwIndexName,BargainDate,CloseIndex,BargainAmount,BargainSum,Markup,OpenIndex,MaxIndex,MinIndex',
            'pagecount': f'{PAGES}',
            'timed': '{}'.format(int(time.time()*1000))
            ##其中页码p是变量，一共2页。timed也是变量，通过 time.time() 来获取时间戳然后将取值到千分位
            }
            #print(postdata)
            req = requests.post(self.url, headers=self.headers, data=postdata)
            data = req.content.decode()
            data = data.replace("'",'"')
            data = json.loads(data)['root']
            #print(len(data))
            result.extend(data)
        df = pd.DataFrame(result)
        
        df.rename(columns={'SwIndexCode':'index_symbol' , 'SwIndexName':'name','BargainDate':'trade_date', 'BargainSum':'vol',
                'BargainAmount':'amount','CloseIndex':'close', 'OpenIndex':'open', 'MaxIndex':'high','MinIndex':'low',
                'Markup':'change_pct'}, inplace=True)
      
        df_swl = df.copy()
        df_swl["index_code"] = df_swl["index_symbol"] + ".SI" 
        
        df_swl["level"] = f"{level}"
        df_swl["name_level"] = df_swl["name"] + "_" + df_swl["level"]
        df_swl['trade_date'] = pd.to_datetime(df_swl['trade_date'],format="%Y%m%d %H:%M:%S")
        df_swl = df_swl[['index_symbol', 'name', 'trade_date', 'open', 'high','low','close','change_pct', \
            'vol','amount','index_code','name_level','level']]
        cols = ['open', 'amount','high','low','close','vol','change_pct']
        for i in cols:
            df_swl[i] = pd.to_numeric(df_swl[i], errors='coerce')
        return df_swl
           
           
    def fetch_swsindex_L1_L2_daily_valucation(self,level="L1", start_date=None, end_date=None,trade_date=None):
        """sw index daily L1 or L2 , just input trade_date or  start_date and end_date,data from swsindex.com """
        if not trade_date:
            if not start_date:
                start_date = startDate
            if not end_date:
                end_date = rq_util_get_last_tradedate()
        if trade_date:
            start_date = trade_date
            end_date = trade_date   
        if level == "L1":
            page_nums = self.page_swl1_realtime_nums
            swl = self.swl1
            self.headers['Referer'] = 'http://www.swsindex.com/idx0200.aspx?columnid=8838&typeDay'
        if level == "L2":
            page_nums = self.page_swl1_realtime_nums
            swl = self.swl2
            self.headers['Referer'] = 'http://www.swsindex.com/idx0200.aspx?columnid=8839&typeDay'
              
        PAGES = len(swl) * len(rq_util_get_trade_range(start_date, end_date)) 
        page_nums = PAGES // 20 + 1
        #print(PAGES, page_nums)
        
        result = []
        for i in range(1, page_nums + 1):
            print(f"fecth data from {self.headers['Referer']} pages:  {i} totla pages: {page_nums}")
            postdata = {
            'tablename':'swindexhistory',
            'key': 'id',
            'p': '{}'.format(i),
            'where':  f"  swindexcode in{swl}  and BargainDate>='{start_date}' and  BargainDate<='{end_date}'",
            'orderby': 'swindexcode asc,BargainDate_1', 
            'fieldlist': "SwIndexCode,SwIndexName,BargainDate,CloseIndex,BargainAmount,Markup,TurnoverRate,PE,PB,MeanPrice,BargainSumRate,NegotiablesShareSum,NegotiablesShareSum2,DP",
            'pagecount': f'{PAGES}',
            'timed': '{}'.format(int(time.time()*1000))
            ##其中页码p是变量，一共2页。timed也是变量，通过 time.time() 来获取时间戳然后将取值到千分位
            }
            #print(postdata)
            req = requests.post(self.url, headers=self.headers, data=postdata)
            data = req.content.decode()
            data = data.replace("'",'"')
            data = json.loads(data)['root']
            #print(len(data))
            result.extend(data)
        
        df = pd.DataFrame(result)
        df.rename(columns={'SwIndexCode':'index_symbol' , 'SwIndexName':'name','BargainDate':'trade_date', 'BargainSum':'vol',
                'BargainAmount':'amount','CloseIndex':'close', 'Markup':'change_pct'}, inplace=True)
        df_swl = df.copy()
        df_swl["index_code"] = df_swl["index_symbol"] + ".SI" 
        df_swl["level"] = f"{level}"
        df_swl["name_level"] = df_swl["name"] + "_" + df_swl["level"]
        df_swl['trade_date'] = pd.to_datetime(df_swl['trade_date'],format="%Y%m%d %H:%M:%S")
        cols = ['amount','close','change_pct']
        for i in cols:
            df_swl[i] = pd.to_numeric(df_swl[i], errors='coerce')
        return df_swl
        
         
    def get_swindex_name(self, out_type=dict):
        data1 = self.fetch_swsindex_L1_L2_realtime("L1")['index','name']
        data2 = self.fetch_swsindex__L1_L2_realtime("L2")[['index', 'name']]
        data = data1.append(data2)
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
            'fieldlist': 'stockcode,stockname',#newweight,beginningdate',
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
        # df.drop(columns=['newweight','beginningdate'], inplace=True)
        df['index_name'] = self.get_index_name(out_type=dict)[index] + '_L1'
        print(df)
        df.rename(columns={'stockcode': 'code','stockname':'name'}, inplace=True)
        return df


    def get_swl1_class(self):
        df_L1 = self.fetch_swsindex_L1_L2_realtime("L1")
        #print(df_L1)
        L1_INDEX = df_L1["index"].values
        
        df = pd.DataFrame()
        for l in L1_INDEX:
            print(f'index code: {l}')
            one = self.get_swl1_class_one(l)
            one['index'] = l
            df = df.append(one)
        return df


def get_sw_index_daily_L1_L2(start_date=None,end_date=None,trade_date=None):
    """ just input tradedate """
    df =pd.DataFrame()
    for l in ["L1","L2"]:
        print(f" sws index level: {l}")
        swl = Swsindex().fetch_swsindex_L1_L2_daily(level=l,start_date=start_date, end_date=end_date, trade_date=trade_date)
        df = df.append(swl)
    #print(df)
    return df


def get_sw_index_daily_valuation_L1_L2(start_date=None,end_date=None,trade_date=None):
    """ just input tradedate """
    df =pd.DataFrame()
    for l in ["L1","L2"]:
        print(f" sws index level: {l}")
        swl = Swsindex().fetch_swsindex_L1_L2_daily_valucation(level=l,start_date=start_date, end_date=end_date, trade_date=trade_date)
        df = df.append(swl)
    #print(df)
    return df

     
if __name__ == '__main__':
    swi = Swsindex()
    print(swi.fetch_swsindex_L1_L2_realtime("L1"))  # ok
    #print(swi.fetch_swsindex_L1_L2_daily(level='L1',trade_date='2022-06-01'))
    #print(swi.fetch_swsindex_L1_L2_daily(level='L1',start_date='2022-01-01', end_date='2022-01-20'))  # TODO
    print(swi.fetch_swsindex_L1_L2_daily_valucation(level='L1',trade_date='2022-06-01'))   
    #print(swi.get_swl1_class_one()) #pk
    #print(swi.get_swl1_class()) #ok
    #print(get_sw_index_daily_L1_L2(trade_date=startDate))
    #print(get_sw_index_daily_L1_L2(start_date="2022-05-02"))
    print(get_sw_index_daily_valuation_L1_L2(start_date='2022-06-01'))
    print(get_sw_index_daily_valuation_L1_L2(trade_date='2022-06-01'))    
 
