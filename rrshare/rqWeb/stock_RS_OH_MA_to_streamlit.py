# streamlit app
from enum import unique
import time
import datetime
import streamlit as st
import pandas as pd
import numpy as np
from streamlit.components.v1 import components

from rrshare.rqUtil import (client_pgsql,read_data_from_pg,read_sql_from_pg)
from rrshare.rqUtil import  (rq_util_date_today,rq_util_get_pre_trade_date,rq_util_get_last_tradedate, trade_date_sse)
from rrshare.rqUtil import is_before_tradetime_secs_cn, is_trade_time_secs_cn, rq_util_if_trade


conn = client_pgsql('rrfactor')
lastTD = rq_util_get_last_tradedate()
today_ = rq_util_date_today().strftime('%Y-%m-%d') 
trade_date = today_  if today_ in trade_date_sse else rq_util_get_last_tradedate()
#now_ = datetime.datetime.now()

current = datetime.datetime.now()
year, month, day = current.year, current.month, current.day
start = datetime.datetime(year, month, day, 9, 23, 0)
noon_start = datetime.datetime(year, month, day, 12, 58, 0)

morning_end = datetime.datetime(year, month, day, 11, 31, 0)
end = datetime.datetime(year, month, day, 15, 2, 5)

st.write('last reload',current, 'last tradedate:',lastTD)

L = ['L1','L2','L3']

#print(current)
#print(current > start)
#print(current > noon_start)

def out_df_items(df):
    #df = df.round(2)
    date, time = df['trade_date'].values[0], df['time'].values[0]
    #date = df['trade_date'].values[0]
    df.drop(columns=['trade_date', 'time'], inplace=True)
    cols = list(df.columns)
    cols.remove('adj_factor')
    #print(cols)
    #cols.insert(1, "cn_name")
    df1 = df[cols]
    #print(df1.head())
    return df1, date, time


def out_swl_item(df):
    date_time = df['trade_date'].values[0]
    df.drop(columns=['trade_date'], inplace=True)
    return df, date_time


def swl_rs_valuation_all(level):
    table_name = f'swl_rs_valuation_{level}'
    df = pd.read_sql_table(table_name, conn)
    data = out_swl_item(df)
    st.write(f'申万行业相对强度和估值_{level} 更新时间：',data[1])
    st.dataframe(data[0],width=1400, height=900)
    

def swl_rs_valuation():
    df = pd.read_sql_table('swl1_rs_L1',conn) # swl1_rs_reaktime_L1
    df.rename(columns={'pct_change':'pct_chg'}, inplace=True)
    df = df.round(2)
    data = out_swl_item(df)
    
    st.write('申万行业相对强度和估值-L1实时: ',data[1])#: {df.trade_date.unique()}')
    st.dataframe(data[0], width=1400, height=900)

    for level in L:
        swl_rs_valuation_all(level)
    pass


def write_stock_RS_OH_MA_new():
    #st.text('相对强度 ')
    #table_name='stock_RS_OH_MA' if  current < start else 'stock_RS_OH_MA_new'
    table_name = 'stock_RS_OH_MA_new' 
    #print(table_name)
    cols = ['code', 'cn_name', 'close', 'pct_chg',
            #'ma5', 'ma10', 'ma20', 'ma60', 'ma120', 'ma250',
            'rs_5', 'rs_10', 'rs_20', 'rs_60', 'rs_120', 'rs_250',
            #'rt5', 'rt10', 'rt20', 'rt60', 'rt120', 'rt250',
            'H', 'L', 'OH', 'OL', 'swl_L1', 'swl_L2', 'swl_L3']
    cols1 = ['code','cn_name', 'close','pct_chg','OH',"OL","swl_L3",'rs_5', 'rs_10','rs_250']
    cols2= ['code','cn_name', 'close','pct_chg','ma20','ma250','rs_5','rs_20','rs_250','OH',"OL","swl_L3"]
    try:
        st.text('申万行业相对强度')
        df = pd.read_sql_table(table_name,conn)
        df.rename(columns={'name':'cn_name'},inplace=True)
        df.drop_duplicates(subset=None,keep='first',inplace=True)
        data = out_df_items(df)
        
        df1 = data[0][cols]
        df2 = data[0][cols1]
        data_by_pctchg = df1.sort_values(by='pct_chg', ascending=False)
        st.write("更新时间: ",data[1],data[2])
        #st.write(data[0])
        df2 = df2.dropna(axis=0,how='any')
        df2 = df2.sort_values(by='rs_5')
        #st.write(df2)
       
        st.write('涨停', str(len(data[0][data[0].pct_chg > 9.90])),'只' , ',   ',\
                    '跌停', str(len(data[0][data[0].pct_chg < -9.90])),'只' )
        st.write(data_by_pctchg, width=1200, height=600)
        
        st.write('一年新高', str(len(df[df.OH >98])),'只' )
        st.write(df2[(df2.OH > 98)], width=1200, height=600)

        st.write('一年新低', str(len(df[df.OL <2])),'只' )
        st.write(df2[df2.OL < 2], width=1200, height=600) 
  
        code = st.text_input('Input stock code:','600519')
        df1 = data[0][cols2]
        st.write(data[1], data[2])
        df_code = df1[df1.code == code]
        st.write(df_code)
    except Exception as e:
        print(e)    

        
def stock_select_PRS(table_name='stock_select_PRS'):
    try:
        df = pd.read_sql_table(table_name,conn)
        #df.rename(columns={'name':'cn_name'},inplace=True)
        print(df)
        data = out_df_items(df)

        st.write('相对强度 top', str(len(df)), '只')
        st.write(data[1], data[2])
        st.dataframe(df, width=1200, height=900)
    except Exception as e:
        print(e)


def stock_fundmentals(): #TODO
    #df = pd.read_sql_table('ROE_CF_SR_INC', conn)
    code = st.text_input('Input stock code:','300146')
    #code =st.multiselect('selects:',[1,2,3])
    #st.write([code])
    #st.text('股票基本面指标')
    #st.write(df[df.code  == code].T)


def stock_infomation():
    st.write("wencai","http://www.iwencai.com/unifiedwap/home/index?qs=pc_~soniu~info~all~homepage~enter")
    st.write('ths_data','https://data.10jqka.com.cn')
    #x = st.slider('x')
    st.text('业绩预告')
    #url_ths=f'http://data.10jqka.com.cn/financial/yjyg/ajax/yjyg/date/2021-03-31/board/YJYZ/field/enddate/ajax/{x}/free/1/'
    url_ths=f'http://data.10jqka.com.cn/financial/yjyg/'#2021-03-31/board/YJYZ/field/enddate/{x}/free/1/'
    st.write( url_ths)
    
    code=  st.text_input('Enter stock code:')
    def change_code(code='600519'):
        #em_code = 'SH600519'
        em_code =  'SZ' + str(code) if code < "333333" else 'SH' + str(code)
        #st.text(em_code)
        return em_code
    em_code = change_code(code)
    url = f"http://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/Index?type=soft&code={em_code}#"
    st.write(f'stock {em_code} info {url}')

    url_hsgt="https://emrnweb.eastmoney.com/hsgt/search?"
    st.write(f'hsgt {url_hsgt}')

    st.write('cfi','http://quote.cfi.cn/cfi_industrydetails.aspx?ctype=5day&dtype=zws')
    st.write('财联社', 'http://cls.cn')
    st.write('雪球','https://xueqiu.com')
    st.write('swsindex','http://www.swsindex.com/idx0120.aspx?columnId=8833')
    st.write('legulegu-估值','https://legulegu.com/stockdata/sw-industry-overview')

def other_info():
    st.write('HK','http://q.10jqka.com.cn/hk/indexYs/')
    st.write('US','http://q.10jqka.com.cn/usa/indexDefer/')
    st.write('航运指数', 'https://www.sse.net.cn/index/singleIndex?indexType=ccfi')
    st.write('中国新造船指数', 'https://www.cnpi.org.cn/index.html')
    st.write('global index ','http://q.10jqka.com.cn/global/')
    st.write('bond','https://cn.investing.com/rates-bonds/u.s.-10-year-bond-yield')
    st.write('myselect','http://quote.eastmoney.com/zixuan/?from=home')
    st.write("金十数据", "https://www.jin10.com/")
    st.write("商品价格","http://top.100ppi.com/zdb/detail-day---1.html")
    st.write('investing','https://hk.investing.com') 
    #st.write('cgf_v2ray','https://gitlab.com/api/v4/projects/30347863/repository/files/data%2Fnew%2Fv2yay-update.txt/raw?ref=main&private_token=glpat-9D-AL5GiX2modB2_XQZA')
    #st.write('cgw_clash','https://gitlab.com/api/v4/projects/30347863/repository/files/data%2Fnew%2Fclash-update.yaml/raw?ref=main&private_token=glpat-9D-AL5GiX2modB2_XQZA')


def main():
    selects = st.sidebar.selectbox(
    "Menu:",
    ("stock_PRS",
        "swl", 
        "stock_PRS_top",
    #    'stock_fundamental',
        'stock_infomation',
        'other_info'))
    
    if selects == 'swl':
        swl_rs_valuation()
    if selects == "stock_PRS_top":
        stock_select_PRS()
    if selects == 'stock_PRS':
        write_stock_RS_OH_MA_new()
    if selects == 'stock_infomation':
        stock_infomation()
    if selects == 'other_info':
        other_info()


if __name__ == "__main__":
    #write_stock_RS_OH_MA_new()
    main()

