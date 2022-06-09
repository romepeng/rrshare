from rrshare.rqUtil import PgsqlClass
from rrshare.rqFetch import sw_index_class_L1_L2, sw_index_class


def save_sw_index_list():
    """ """
    for level in ["L1","L2"]:
        PgsqlClass().insert_to_psql(sw_index_class(level), 'rrshare',f'swl_list_{level}',if_exists='replace')
        
    PgsqlClass().insert_to_psql(sw_index_class_L1_L2(), 'rrshare','swl_list',if_exists='replace')


if __name__ == '__main__':
    save_sw_index_list()
   