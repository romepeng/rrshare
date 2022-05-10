import time

from rrshare.rqUtil import PgsqlClass
from rrshare.rqFetch import Swsindex

def save_swl2_realtime():
    swi_rt = Swsindex().get_swsindex_L2_realtime()
    print(swi_rt)
    PgsqlClass().insert_to_psql(swi_rt, 'rrshare','swl2_realtime',if_exists='replace')


if __name__ == '__main__':
    save_swl2_realtime()

    pass

