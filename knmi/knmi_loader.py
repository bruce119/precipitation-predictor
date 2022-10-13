import itertools
from io import StringIO
import pandas as pd

import requests


def get_raw_station_data(start, end):
    """Raw response of the KNMI API (only PRCP)

    Args:
        start (str): start time for fetching the data from the weather stations(YYYYMMDDHH
        end (str): end time for fetching the data from the weather stations(YYYYMMDDHH)

    Returns:
        text: response data from KNMI API
    """
    url = "https://www.daggegevens.knmi.nl/klimatologie/daggegevens"
    params = {"stns": "ALL", "start": start, "end": end, "vars": 'PRCP'}
    r = requests.post(url=url, data=params)
    r.raise_for_status()
    return r.text


def get_parsed_stations_data(raw: str):
    """process the raw response of KNMI API

    Args:
        raw (str): raw text data from KNMI API

    Returns:
        dataFrame: a dataframe containing processed KNMI API data
    """
    lines = raw.splitlines()
    csv_header = list(itertools.takewhile(lambda line: line.startswith("#") or line.startswith('"#'), lines))
    data_numeric = '\n'.join(lines[len(csv_header):]).replace(" ", "")
    data_header = csv_header.pop(-1).replace("#", "").replace(" ", "")
    data = data_header + "\n" + data_numeric
    data = pd.read_csv(StringIO(data), index_col=1, converters={'YYYYMMDD': pd.Timestamp})
    data['RH'] = data['RH'].apply(lambda x: 0.5 if x == -1 else x).fillna(0)
    data = data.groupby('STN').sum().reset_index()
    return data


def get_precipitation_data(start, end):
    """returns the final dataFrame for KNMI data

    Args:
        start (str): start time for fetching the data from the weather stations(YYYYMMDDHH
        end (str): end time for fetching the data from the weather stations(YYYYMMDDHH)

    Returns:
        dataFrame: a dataframe containing processed KNMI API data
    """
    raw_data = get_raw_station_data(start, end)
    return get_parsed_stations_data(raw_data)
