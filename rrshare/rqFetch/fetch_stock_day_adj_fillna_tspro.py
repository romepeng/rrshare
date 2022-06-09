# coding: utf-8
import pandas as pd
import numpy as np
import time
import tushare as ts

from rrdata.rrdatad.stock.tusharepro import pro
from rrshare.rqFetch.fetch_basic_tusharepro import fetch_delist_stock, fetch_stock_list_tusharepro
from rrshare.rqUtil.rqLogs import rq_util_log_debug, rq_util_log_info, rq_util_log_expection
from rrshare.rqUtil.rqParameter import startDate


def fetch_stock_day_adj_onetradedate_tsro(trade_date=None):
    trade_date = trade_date.replace('-', '') #兼容设置以防日期格式为2001-10-20格式
    lastEx = None
    retry =3
    for _ in range(retry):
        try:
            df_daily=pro.query('daily',trade_date=trade_date)
            df_daily = df_daily.drop(columns='change')
            df_daily['amount'] = (10*df_daily['amount']).apply(lambda x : round(x,2))
            df_daily['avg'] =  (df_daily['amount'] / df_daily['vol']).apply(lambda x : round(x,2))
            #df_daily_basic=pro.query('daily_basic',trade_date=trade_date)
            df_factor=pro.query('adj_factor',trade_date=trade_date)
            break 
        except Exception as ex:
            lastEx = ex
            rq_util_log_info("[{}]TuSharePro数据异常: {}, retrying...".format(trade_date, ex))
        else:
            rq_util_log_info("[{}]TuSharePro异常: {}, retried {} times".format(trade_date,lastEx, retry))
            return None
    
    delist_code = fetch_delist_stock(trade_date)
    #print(delist_code)
    res=pd.merge(df_factor,df_daily,how='left').sort_values(by='ts_code')
    res['symbol']=res['ts_code'].apply(lambda x:x[:6]) #x[7:9].lower()
    res['trade_date'] = pd.to_datetime(res['trade_date'])
    
    res=res[~res['symbol'].isin(delist_code)]
    res.fillna({'pct_chg':0,'vol':0,'amount':0}, inplace=True)
    #print(res)
    return res

   
if __name__ == "__main__":
    import time
    t1 = time.perf_counter()
    print(fetch_stock_day_adj_onetradedate_tsro('2021-01-07'))
    
    t2 = time.perf_counter()
    t = t2 - t1
    print(f"times:  --- {t}")
    

