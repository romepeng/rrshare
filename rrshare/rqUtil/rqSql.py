# coding:utf-8
import asyncio
from http import client
import asyncpg
import psycopg2
from rrshare.rqUtil import setting


host = setting['IP_DATABASE_ALIYUN']
db_name = setting["DATABASE_RRSHARE"]
passwd = setting["PGSQL_PASSWORD"]
uri = f'postgresql://postgres:{passwd}@{host}:5432/{db_name}'

# connect client
def rq_util_sql_postgres_setting(uri=uri):
    # 使用uri代替ip,port的连接方式
    # 这样可以对postgresql进行加密:
    # uri=postgresql://user:passwor@ip:port/daatbase
    #with  psycopg2.connect(uri) as conn:
    client = psycopg2.connect(uri)
    #print(client)
    return client

def show_sql_conn_count():
    """ select state, count(*) from pg_stat_activity  where pid <> pg_backend_pid() group by 1 order by 1;"""
    sql = str("select count(*) from pg_stat_activity;")
    with  rq_util_sql_postgres_setting() as conn:
        print(conn)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        print(res)
        
    
    

if __name__ == '__main__':
    # test client
    print(rq_util_sql_postgres_setting())
    show_sql_conn_count()
