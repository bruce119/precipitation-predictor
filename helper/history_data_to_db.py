import multiprocessing
import sys
from datetime import datetime, timedelta
sys.path.insert(0, './knmi')
import pandas as pd
import sqlite3
from knmi_loader import get_precipitation_data

conn = sqlite3.connect('./data/knmi_database')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS precip_history_data 
            (STN text, 
             RH float, 
             date_back text
             );''')
c.execute('''CREATE INDEX IF NOT EXISTS date_index_recent ON precip_history_data(date_back);''')
conn.commit()
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
                df[['STN', 'RH', 'date_back']].to_sql('precip_history_data', conn, if_exists='append', index=False)
            except Exception as e:
                print(e)
            if end_temp > end:
                sys.exit(0)
            start = end_temp
            return_dict.clear()
    except Exception as e:
        print(e)
conn.close()
