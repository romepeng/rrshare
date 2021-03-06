# streamlit app
""" streamlit.line_chart(data=None, width=0, height=0, use_container_width=True)
    streamlit.area_chart(data=None, width=0, height=0, use_container_width=True)
    streamlit.bar_chart(data=None, width=0, height=0, use_container_width=True)
    streamlit.pyplot(fig=None, clear_figure=True, **kwargs)
    streamlit.plotly_chart(figure_or_data, width=0, height=0, use_container_width=False, sharing='streamlit', **kwargs)
    streamlit.bokeh_chart(figure, use_container_width=False)
    streamlit.pydeck_chart(pydeck_obj=None)
    streamlit.deck_gl_chart(spec=None, **kwargs)
    streamlit.graphviz_chart(figure_or_dot, width=0, height=0)

    st.multiselect('Multiselect', [1,2,3])
    st.write('http://datacenter.eastmoney.com/securities/api/data/v1/get?callback=jQuery112305791870244468389_1618109280782&sortColumns=NOTICE_DATE%2CSECURITY_CODE&sortTypes=-1%2C-1&pageSize=50&pageNumber=1&reportName=RPT_PUBLIC_OP_NEWPREDICT&columns=ALL&token=894050c76af8597a853f5b408b759f5d&filter=(REPORT_DATE%3D%272021-06-30%27)')
    st.text_area('Area for textual entry')
    trade_date = st.date_input('Date input')
    st.write(trade_date)
    st.time_input('Time entry')
    st.file_uploader('File uploader')
    import streamlit.components.v1 as components
    #url_ths=f'http://data.10jqka.com.cn/financial/yjyg/'
    #url_ths =  "http://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/Index?type=soft&code=SZ300146#"
    # embed streamlit docs in a streamlit app
    #components.iframe(url_ths,  width=1400, height=700)    
    Create a static component
If your goal in creating a Streamlit Component is solely to display HTML code or render a chart from a Python visualization library, 
Streamlit provides two methods that greatly simplify the process: components.html() and components.iframe().
"""
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
    st.write('?????????????????????????????????_{level} ???????????????',data[1])
    st.dataframe(data[0],width=1400, height=900)
    

def swl_rs_valuation():
    df = pd.read_sql_table('swl1_rs_L1',conn) # swl1_rs_reaktime_L1
    df.rename(columns={'pct_change':'pct_chg'}, inplace=True)
    df = df.round(2)
    data = out_swl_item(df)
    
    st.write('?????????????????????????????????-L1??????: ',data[1])#: {df.trade_date.unique()}')
    st.dataframe(data[0], width=1400, height=900)

    for level in L:
        swl_rs_valuation_all(level)
    pass


def write_stock_RS_OH_MA_new():
    #st.text('???????????? ')
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
        st.text('????????????????????????')
        df = pd.read_sql_table(table_name,conn)
        df.rename(columns={'name':'cn_name'},inplace=True)
        df.drop_duplicates(subset=None,keep='first',inplace=True)
        data = out_df_items(df)
        
        df1 = data[0][cols]
        df2 = data[0][cols1]
        data_by_pctchg = df1.sort_values(by='pct_chg', ascending=False)
        st.write("????????????: ",data[1],data[2])
        #st.write(data[0])
        df2 = df2.dropna(axis=0,how='any')
        df2 = df2.sort_values(by='rs_5')
        #st.write(df2)
       
        st.write('??????', str(len(data[0][data[0].pct_chg > 9.90])),'???' , ',   ',\
                    '??????', str(len(data[0][data[0].pct_chg < -9.90])),'???' )
        st.write(data_by_pctchg, width=1200, height=600)
        
        st.write('????????????', str(len(df[df.OH >98])),'???' )
        st.write(df2[(df2.OH > 98)], width=1200, height=600)

        st.write('????????????', str(len(df[df.OL <2])),'???' )
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
        df.rename(columns={'name':'cn_name'},inplace=True)

        data = out_df_items(df)

        st.write('???????????? top', str(len(df)), '???')
        st.write(data[1], data[2])
        st.dataframe(df, width=1200, height=900)
    except Exception as e:
        print(e)


def stock_fundmentals(): #TODO
    #df = pd.read_sql_table('ROE_CF_SR_INC', conn)
    code = st.text_input('Input stock code:','300146')
    #code =st.multiselect('selects:',[1,2,3])
    #st.write([code])
    #st.text('?????????????????????')
    #st.write(df[df.code  == code].T)


def stock_infomation():
    st.write("wencai","http://www.iwencai.com/unifiedwap/home/index?qs=pc_~soniu~info~all~homepage~enter")
    st.write('concept','http://q.10jqka.com.cn/gn/')
    #x = st.slider('x')
    st.text('????????????')
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
    st.write('?????????', 'https://cls.cn')
    st.write('??????','https://xueqiu.com')

def other_info():
    st.write('HK','http://q.10jqka.com.cn/hk/indexYs/')
    st.write('US','http://q.10jqka.com.cn/usa/indexDefer/')
    st.write('????????????', 'https://www.sse.net.cn/index/singleIndex?indexType=ccfi')
    st.write('?????????????????????', 'https://www.cnpi.org.cn/index.html')
    st.write('global index ','http://q.10jqka.com.cn/global/')
    st.write('bond','https://cn.investing.com/rates-bonds/u.s.-10-year-bond-yield')
    st.write('myselect','http://quote.eastmoney.com/zixuan/?from=home')
    st.write("????????????", "https://www.jin10.com/")
    st.write("????????????","http://top.100ppi.com/zdb/detail-day---1.html")
    st.write('investing','https://hk.investing.com') 
    st.write("rome's blog", "https://rome.tk")
    st.write('cgf','https://suo.yt/sOaQn0f')

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

