"""http://www.swsindex.com/idx0200.aspx?columnid=8838&type=Day  -- L1
http://www.swsindex.com/idx0200.aspx?columnid=8839&type=Day  --L2
"""

def sw_index_daily(level="L2"):
    
    Referer: http://www.swsindex.com/idx0200.aspx?columnid=8839&type=Day
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36
X-AjaxPro-Method: Ret
    result = []
           
        for i in range(1,3):
             postdata = {
            'tablename': 'swzs',
            'key': 'L1',
            'p': '{}'.format(i),
            'where': "L1 in('801012','801014','801015','801016','801017','801018','801032','801033','801034', \
                '801036','801037','801038','801039','801043','801044','801045','801051','801053','801054','801055', \
                '801056','801072','801074','801076','801077','801078','801081','801082','801083','801084','801085', \
                '801086','801092','801093','801095','801096','801101','801102','801103','801104','801111','801112','801113', \
                '801114','801115','801116','801124','801125','801126','801127','801128','801129','801131','801132','801133', \
                '801141','801142','801143','801145','801151','801152','801153','801154','801155','801156','801161','801163', \
                '801178','801179','801181','801183','801191','801193','801194','801202','801203','801204','801206','801218', \
                '801219','801223','801231','801711','801712','801713','801721','801722','801723','801724','801726','801731', \
                '801733','801735','801736','801737','801738','801741','801742','801743','801744','801745','801764','801765', \
                '801766','801767','801769','801782','801783','801784','801785','801881','801951','801952','801962','801963', \
                '801971','801972','801981','801982','801991','801992','801993','801994','801995')",
            'orderby': '',
            'fieldlist': 'L1,L2,L3,L4,L5,L6,L7,L8,L11',
            'pagecount': '124',
            'timed': '{}'.format(int(time.time()*1000))
            ##其中页码p是变量，一共2页。timed也是变量，通过 time.time() 来获取时间戳然后将取值到千分位
            }
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
        df['chg_pct'] = 0.00 if df['close'].values[0] == 0 else 100*(df['close']/ df['pre_close'] -1) 
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #trade_time = #TODO
        print(rq_util_date_today())
        print(rq_util_if_trade(rq_util_date_today()))
        trade_time = date_time if rq_util_if_tradetime() else rq_util_get_last_tradedate() # TODO
        print(trade_time)
        df['trade_date'] = trade_time 
        return df.round(2)
    
       


if __name__ == "__main__":
    
    pass
