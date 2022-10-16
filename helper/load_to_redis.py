import sqlite3
import warnings
import sys
sys.path.insert(0, './knmi')
import pandas as pd
import pyarrow as pa
import redis

warnings.filterwarnings("ignore")

r = redis.Redis(host='127.0.0.1', port=6379, db=0)
conn = sqlite3.connect('./data/knmi_database')
c = conn.cursor()


c.execute('Select * from precip_history_data')
context = pa.default_serialization_context()


chunk_size = 1000
while True:
    result = c.fetchmany(chunk_size)
    if not result:
        sys.exit("Complete")
    else:
        for row in result:
            if r.exists(row[2]):
                row_df = pd.DataFrame((row,), columns=['STN', 'RH', 'date_back'])
                df_get = context.deserialize(r.get(row[2]))
                if row[0] not in df_get['STN']:
                    concat_df = pd.concat([df_get, row_df])
                    r.set(row[2], context.serialize(concat_df).to_buffer().to_pybytes())
            else:
                print('pushing Key:- ', row[2])
                df_set = pd.DataFrame((row,), columns=['STN', 'RH', 'date_back'])
                r.set(row[2], context.serialize(df_set).to_buffer().to_pybytes())
