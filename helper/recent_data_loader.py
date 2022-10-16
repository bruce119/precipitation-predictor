import sys
sys.path.insert(0, './knmi')
import multiprocessing
import warnings
from datetime import datetime, timedelta
from knmi_loader import get_precipitation_data
import pandas as pd
import pyarrow as pa


context = pa.default_serialization_context()
warnings.filterwarnings("ignore")
from redis_connector import create_redis_conn

r = create_redis_conn()

date_delete = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y%m%d%H")
key_arr = r.keys()
delete_keys = [i.decode() for i in key_arr if i == date_delete.encode()]
for key in delete_keys:
    r.delete(key)


def worker(return_dict, start, end):
    """worker function"""
    frame = get_precipitation_data(start, end)
    frame['date_back'] = end
    return_dict[start + end] = frame


def prepare_time(start_temp, n):
    lis = []
    for j in range(1, n + 1):
        end_temp = start_temp + timedelta(hours=1)
        lis.append([start_temp.strftime('%Y%m%d%H'), end_temp.strftime('%Y%m%d%H')])
        start_temp = end_temp

    return lis, start_temp


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []
    start = datetime.now() - timedelta(days=2)
    start, end = start, datetime.now()
    n = 24
    try:
        while start <= end:
            lis, end_temp = prepare_time(start, n)
            print(f"INFO:- started for {start.strftime('%Y%m%d%H')} till {end_temp.strftime('%Y%m%d%H')}")
            for i in lis:
                print(i)
                p = multiprocessing.Process(target=worker, args=(return_dict, i[0], i[1]))
                jobs.append(p)
                p.start()

            for proc in jobs:
                proc.join()
            df = pd.concat(return_dict.values())
            try:
                r.set(end_temp.strftime('%Y%m%d%H'),
                      context.serialize(df[['STN', 'RH', 'date_back']]).to_buffer().to_pybytes())
                r.expire(end_temp.strftime('%Y%m%d%H'), 365 * 3 * 24 * 60 * 60)
            except Exception as e:
                print(e)
            if end_temp > end:
                sys.exit(0)
            start = end_temp
            return_dict.clear()
    except Exception as e:
        print(e)
