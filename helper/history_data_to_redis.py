import multiprocessing
import sys
from datetime import datetime, timedelta
sys.path.insert(0, './knmi')
import pandas as pd
from knmi_loader import get_precipitation_data
import redis
import pyarrow as pa

context = pa.default_serialization_context()
r = redis.Redis(host='127.0.0.1', port=6379, db=0)

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
    start = datetime.now() - timedelta(365 * 3)
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
            except Exception as e:
                print(e)
            if end_temp > end:
                sys.exit(0)
            start = end_temp
            return_dict.clear()
    except Exception as e:
        print(e)
