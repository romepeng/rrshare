# coding: utf-8
import requests
import json
import time
import pandas as pd


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
    "where": "",
    "orderby": "",
    "fieldlist": "L1,L2,L3,L4,L5,L6,L7,L8,L11",
    "pagecount": "28",
    "timed": "",
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



def get_swl1_class_one(index='801010'):
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

    
def sw_index_spot(level='L1'):
    """
    申万二级行业-实时行情数据
    http://www.swsindex.com/idx0120.aspx?columnId=8833
    :return: 申万二级行业-实时行情数据
    :rtype: pandas.DataFrame
    """
    result = []
    if level == 'L1':
        N = 3
        N_pages = 28
        SWL_INDEX = SWL1_INDEX
    elif level == 'L2':
        N= 8
        N_pages = 124
        SWL_INDEX = SWL2_INDEX
    else:
        print("No thix sw index level !")
    for i in range(1, N):
        payload = swl_payload
        payload.update({"p": i})
        payload.update({"pagecount": f"{N_pages}"})
        payload.update({"timed": int(time.time() * 1000)})
        payload.update({"where": f"L1 in{SWL_INDEX}"})
        r = requests.post(sw_url, headers=sw_headers, data=payload)
        data = r.content.decode()
        data = data.replace("'", '"')
        data = json.loads(data)
        result.extend(data["root"])
    temp_df = pd.DataFrame(result)
    temp_df["L2"] = temp_df["L2"].str.strip()
    temp_df.columns = ["index_code", "index_name", "pre_close", "open", "amount", "high", "low", "close", "vol"]
    return temp_df.round(2)    
      

if __name__ == '__main__':
    print(sw_index_spot(level="L2"))
    pass
