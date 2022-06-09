#!/usr/bin/python
from configparser import ConfigParser

from rrshare.rqUtil.rqLogs import rq_util_log_info
from rrshare.rqUtil.config_setting import get_path_file_name

def get_config_ini(section='rrshare',filename='config.ini'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(get_path_file_name(path_name='setting',file_name=filename))
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    #rq_util_log_info(db)
    return db

database_uri = get_config_ini('pgsql_rrshare')
rq_util_log_info(database_uri)