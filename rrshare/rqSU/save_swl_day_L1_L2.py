import pandas as pd
import pickle

from rrshare.rqUtil import PgsqlClass
from rrshare.rqUtil import rq_util_get_last_tradedate
from rrshare.rqFetch import sw_index_daily, sw_index_daily_indicator
from rrshare.rqUtil.rqParameter import startDate, TS_DATE_FORMATE
from rrshare.rqFetch import sw_index_class_L1_L2, sw_index_class

#startDate = '2022-05-01'

def save_sw_index_daily_to_pickle(start_date=startDate, end_date=rq_util_get_last_tradedate()):
    """ daily = sw_index_daily(symbol="801995", start_date="2022-04-01", end_date="2022-05-11")
    indicator = sw_index_daily_indicator(symbol="801010", start_date="2022-04-01", end_date="2022-05-09")
    """
    sw_l1_12 = sw_index_class_L1_L2()
    swl1_l2_list = sw_l1_12['index_symbol'].values
  
    df = pd.DataFrame()
    for l in swl1_l2_list:
        sw_daily_one = sw_index_daily(symbol=l, start_date=start_date, end_date=end_date)
     
        df = df.append(sw_daily_one)
        print(df)
    df.to_pickle("~/.rrsdk/data/sw_index_day_L1_L2.cache.pkl")
    
    
def save_sw_index_daily_to_pgsql(start_date=startDate, end_date=rq_util_get_last_tradedate()):
    #df = pd.read_pickle("~/.rrsdk/data/sw_index_day_L1_L2.cache.pkl")
    sw_l1_12 = sw_index_class_L1_L2()
    swl1_l2_list = sw_l1_12['index_symbol'].values
  
    df = pd.DataFrame()
    for l in swl1_l2_list:
        sw_daily_one = sw_index_daily(symbol=l, start_date=start_date, end_date=end_date)
     
        df = df.append(sw_daily_one)
        print(df)
    df.to_pickle("~/.rrsdk/data/sw_index_day_L1_L2.cache.pkl")
  
    #df['index_symbol'] = df['index_code']
    df['index_code'] = df['index_code'] + ".SI"
 
    df.rename(columns={'date':'trade_date'}, inplace=True)
    #print(df)
    #print(sw_l1_12)
    data = pd.merge(df, sw_l1_12)
    data.drop(columns=["index_name"], inplace=True)
    #print(data)
    PgsqlClass().insert_to_psql(data, 'rrshare','sw_index_day',if_exists='replace')


if __name__ == '__main__':
    #save_sw_index_daily_to_pickle()
    save_sw_index_daily_to_pgsql()
   