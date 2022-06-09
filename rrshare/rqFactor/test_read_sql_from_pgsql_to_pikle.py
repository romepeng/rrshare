import time
import datetime
import pickle
import pandas as pd
import polars as pl 
import connectorx as cx
import numpy as np
from decimal import Decimal
import warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.INFO, format=' %(asctime)s- %(levelname)s-%(message)s')

from rrshare.rqUtil import (rq_util_log_debug, rq_util_log_expection,
                                                     rq_util_log_info)
from rrshare.rqUtil import (rq_util_date_today, rq_util_get_trade_range, rq_util_get_last_tradedate, rq_util_get_pre_trade_date)
from rrshare.rqUtil import (PERIODS, is_trade_time_secs_cn)
from rrshare.rqUtil import (client_pgsql, read_data_from_pg, read_sql_from_pg)
from rrshare.rqUtil.rqSql import uri 

table_name = 'stock_day_adj_fillna'
sql = f"""
SELECT * FROM {table_name}
WHERE trade_date >= '2021-05-01'
"""

client_rrshare = client_pgsql('rrshare')
client_rrfactor = client_pgsql('rrfactor')
#conn, protocol() = rewrite_conn(conn, protocol)
uri_rrshare = uri 
print(uri_rrshare)

t1 = time.perf_counter()  # taste 648 mins
#df = pd.read_sql_query(sql,con=client_rrshare)
#df = pl.read_sql(sql,uri_rrshare)
df = cx.read_sql(uri_rrshare, sql,  partition_num=10)
#df = pl.read_sql(sql, client_rrshare, partition_on="partition_col", partition_num=10)  
#df = pl.from_pandas(pd.read_sql(sql, con=client_rrshare))  
df.to_pickle("~/.rrsdk/data/stock_day_20210502.pkl")
#df = pd.read_pickle("~/.rrsdk/data/stock_day_20210501.pkl")
print(df[df['ts_code'] == '000792.SZ'])

t2 = time.perf_counter()
print(f"{t2 - t1 =}")

#pl.read_sql(query, uri, partition_on="partition_col", partition_num=10)  