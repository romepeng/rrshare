from re import I
import pandas as pd 
from rrshare.rqFetch.fetch_swl_index_daily_and_realtime import Swsindex


def sw_index_class(level="L1"):
    """
    swl L1, L2, class
    申万一，二，-分类
    """
    sw_level=f"level{level[-1]}"
    #print(sw_level)
     
    swl_spot = Swsindex().fetch_swsindex_L1_L2_realtime(level)
    print(swl_spot)
    df_swl = swl_spot.copy()
    df_swl["index_code"] = df_swl["index_symbol"] + ".SI" 
  
    df_swl["level"] = f"{level}"
    df_swl["name_level"] = df_swl["name"] + "_" + df_swl["level"]
    df_swl = df_swl[['index_symbol', 'index_code', 'index_symbol', 'level', 'name_level']]

    return df_swl


def sw_index_class_L1_L2():
    df = pd.DataFrame() 
    for level in ["L1", "L2"]:
        df = pd.concat([df,sw_index_class(level)])
    return df


if __name__ == "__main__":
    print(sw_index_class(level="L2"))
    print(sw_index_class("L1").columns)
    
    print(sw_index_class_L1_L2())