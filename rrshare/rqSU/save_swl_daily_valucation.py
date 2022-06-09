# coding: utf-8
import pandas as pd
import numpy as np
import os
import time
import datetime
import pymongo
import tushare as ts
from sqlalchemy import create_engine
import psycopg2  
import warnings
warnings.filterwarnings("ignore")

from rrshare.rqUtil.rqLogs import (rq_util_log_debug, rq_util_log_expection,
                                     rq_util_log_info)
from rrshare.rqUtil.rqCode import (rq_util_code_tosrccode, rq_util_code_tostr)
from rrshare.rqUtil.rqDate_trade import rq_util_get_trade_range
from rrshare.rqUtil.rqDate import (rq_util_date_str2int,rq_util_date_int2str)

from rrshare.rqUtil import (PgsqlClass, rq_util_get_last_tradedate)
from rrshare.rqFetch import (pro, fetch_stock_day_adj_fillna_from_tusharepro)


from rrshare.rqFetch import (fetch_stock_bar_hfq_from_tusharepro, fetch_stock_list_tusharepro)
from rrshare.rqUtil.rqParameter import startDate
from rrshare.rqFetch.fetch_swl_index_daily_and_realtime import Swsindex, get_sw_index_daily_L1_L2,get_sw_index_daily_valuation_L1_L2

lastTD = rq_util_get_last_tradedate()
print(lastTD)

def create_pgsql_table(tabel_name='', tsql='', db_name='rrshare'):
    try:
        PgsqlClass().create_table(tabel_name, tsql)
    except Exception as e:
        print(e)

def client_pgsql(database='rrshare'):
    try:
        return PgsqlClass().client_pg(db_name=database)
    except Exception as e:
        print(e)

def save_data_to_postgresql(name_biao,data,if_exists='replace',client=client_pgsql()):
        data.to_sql(name_biao,client,index=False,if_exists=if_exists)
    
def load_data_from_postgresql(mes='',client=client_pgsql()):
    res=pd.read_sql(mes,client)
    return res

def read_data_from_pg(table_name='', client=client_pgsql()):
    res = pd.read_sql_table(table_name, client)
    return res


def rq_fetch_stock_list_pg(name_biao='stock_list'):
    mes='select * from '+name_biao+";"    
    try:   
        t=time.time()        
        res=load_data_from_postgresql(mes=mes)
        t1=time.time()
        rq_util_log_info('load '+ name_biao+ ' success,take '+str(round(t1-t,2))+' S')              
    except Exception as e:
        print(e)
        res=None
    return res


def rq_save_stock_list_pg():
    stock_list_l= pro.stock_basic(exchange_id='', is_hs='',list_status='L' , fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')  
    #stock_list_D= pro.stock_basic(exchange_id='', is_hs='',list_status='D' , fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')  
    #stock_list_P= pro.stock_basic(exchange_id='', is_hs='',list_status='P' , fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')          
    #stock_list=pd.concat([stock_list_l,stock_list_D],axis=0)
    #stock_list=pd.concat([stock_list_l,stock_list_P],axis=0)
    stock_list = stock_list_l
    stock_list['code']=stock_list['symbol']
    #print(df)
    try:   
        t=time.time()    
        save_data_to_postgresql('stock_list',stock_list)
        t1=time.time()
        rq_util_log_info('save stock_list data success,take '+str(round(t1-t,2))+' S') 
    except Exception as e:        
        print(e) 


def rq_save_swl_day_pg(start_date=startDate, table_name='swl_day'): #from 2015-01-04
    #table_name='swl_day'
    t = time.localtime(time.time())
    if int(time.strftime('%H%M%S',t))<160000:   #晚上9点之后在更新当天数据，以免不及时
        t = time.localtime(time.time()-3600*24)
        tS = time.strftime("%Y-%m-%d", t)
    else:
        tS = time.strftime("%Y-%m-%d", t)
    end_date=tS
    print(end_date)
    try:
        mes=f'select distinct trade_date FROM {table_name};'
        #mes='SELECT DISTINCT trade_date FROM swl_day;'
        trade_data_pg = load_data_from_postgresql(mes).trade_date.tolist()
        #print(trade_data_pg[-3:])
        for i in range(len(trade_data_pg)):
            trade_data_pg[i]=trade_data_pg[i].strftime("%Y-%m-%d")
            #trade_data_pg = list(map(lambda x: x.strftime('%Y-%m-%d'), trade_data_pg))
            #print(len(trade_data_pg))
            #print(trade_data_pg[-1:])
    except: #第一次运行
        trade_data_pg=list()
        #print(trade_data_pg[-3:])
    if isinstance(start_date,int):
        start_date=rq_util_date_int2str(start_date)
    elif len(start_date)==8:
        start_date=start_date[0:4]+'-'+start_date[4:6]+'-'+start_date[6:8]
        #print(start_date)
    trade_date=rq_util_get_trade_range(start_date,end_date)
    #print(trade_date)
    trade_date2=list(set(trade_date).difference(set(trade_data_pg))) #差集 在trade_date 中 不在trade_data_pg
    trade_date2.sort()
    print(trade_date2)

    if len(trade_date2)==0:
        rq_util_log_info('swl day is up to date and does not need to be updated')
    for i in trade_date2:
        print(i)
        try:
            t=time.time()
            df = get_sw_index_daily_L1_L2(trade_date=i)
            save_data_to_postgresql(table_name, df, 'append')
            t1=time.time()
            tt = round((t1-t),4)
            time.sleep(1)
            rq_util_log_info(f'save {i} {table_name} success,take {tt}S')
        except Exception as e:
            print(e)


def rq_save_swl_day_valucation_pg(start_date=startDate, table_name='swl_day_valuation'): #from 2015-01-04
    t = time.localtime(time.time())
    if int(time.strftime('%H%M%S',t))<160000:   #晚上4点之后在更新当天数据，以免不及时
        t = time.localtime(time.time()-3600*24)
        tS = time.strftime("%Y-%m-%d", t)
    else:
        tS = time.strftime("%Y-%m-%d", t)
    end_date=tS
    print(end_date)
    try:
        mes=f'select distinct trade_date FROM {table_name};'
        #mes='SELECT DISTINCT trade_date FROM swl_day;'
        trade_data_pg = load_data_from_postgresql(mes).trade_date.tolist()
        #print(trade_data_pg[-3:])
        for i in range(len(trade_data_pg)):
            trade_data_pg[i]=trade_data_pg[i].strftime("%Y-%m-%d")
            #trade_data_pg = list(map(lambda x: x.strftime('%Y-%m-%d'), trade_data_pg))
            #print(len(trade_data_pg))
            #print(trade_data_pg[-1:])
    except: #第一次运行
        trade_data_pg=list()
        #print(trade_data_pg[-3:])
    if isinstance(start_date,int):
        start_date=rq_util_date_int2str(start_date)
    elif len(start_date)==8:
        start_date=start_date[0:4]+'-'+start_date[4:6]+'-'+start_date[6:8]
        #print(start_date)
    trade_date=rq_util_get_trade_range(start_date,end_date)
    #print(trade_date)
    trade_date2=list(set(trade_date).difference(set(trade_data_pg))) #差集 在trade_date 中 不在trade_data_pg
    trade_date2.sort()
    print(trade_date2)

    if len(trade_date2)==0:
        rq_util_log_info('swl day is up to date and does not need to be updated')
    for i in trade_date2:
        print(i)
        try:
            t=time.time()
            df = get_sw_index_daily_valuation_L1_L2(trade_date=i)
            save_data_to_postgresql(table_name, df, 'append')
            t1=time.time()
            tt = round((t1-t),4)
            time.sleep(1)
            rq_util_log_info(f'save {i} {table_name} success,take {tt}S')
        except Exception as e:
            print(e)


if __name__ == '__main__':          
    #rq_save_stock_list_pg()
    rq_save_swl_day_pg()
    rq_save_swl_day_valucation_pg() 

