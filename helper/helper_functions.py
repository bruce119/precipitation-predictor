import warnings
from datetime import datetime
warnings.filterwarnings("ignore")
import pandas as pd
import reverse_geocode
from numpy import int64
import  pyarrow as pa
from helper.redis_connector import create_redis_conn
from knmi.knmi_loader import get_precipitation_data
context = pa.default_serialization_context()

r = create_redis_conn()

def load_csv_data_cleaned(path):
    """Clean and load the  weatherstations-NL csv data
    Args:
        path (str): path to the file relative to the folder where the app is started from

    Return:
        dataFrame: containing lat,long, name and id of the weather stations.
    """
    station_info = pd.read_csv(path, header=None)
    station_info.rename(columns={0: 'lat', 1: 'long', 2: 'id', 3: 'Name'}, inplace=True)
    station_info['id'] = station_info['id'].astype(int64)
    station_info['lat'] = station_info['lat'].str.replace('N', '').str.strip().astype(float)
    station_info['long'] = station_info['long'].str.replace('E', '').str.strip().astype(float)
    return station_info


def get_data_from_db(start, end):
    if r.exists(end):
        df = context.deserialize(r.get(end))
    else:
        print('not found')
        df = get_precipitation_data(start, end)
        df['date_back'] = str(end)
        try:
            r.set(end, context.serialize(df[['STN', 'RH', 'date_back']]).to_buffer().to_pybytes())
            r.expire(end, 365 * 3 * 24 * 60 * 60)
        except Exception as e:
            print(e)
    df.drop('date_back', axis=1)
    df['STN'] = df['STN'].astype('int64')
    return df


def prepare_data(stations_location_data, precip_data):
    """Get columns required for prediction and merging the two dataFrames
    Args:
        stations_location_data (dataFrame): dataframe containing the stations lat, long, name and id data
        precip_data (dataframe): dataframe containing the Stations 'RH' and their id's
    Return:
        dataFrame, dataFrame:  id, lat,long of stations data and STN(id), RH value for different stations
    """
    stations_location_data = stations_location_data[['id', 'lat', 'long']]
    parsed_stations_data = precip_data[['STN', 'RH']]
    return stations_location_data, parsed_stations_data


def get_X_y(stations_location_data_raw, precip_data_raw):
    """Merge the stations dataframe and data from stations to return the list for prediction model
        Args:
            stations_location_data_raw (dataFrame): dataframe containing the stations lat, long, name and id data
            precip_data_raw (dataframe): dataframe containing the Stations 'RH' and their id's
        Return:
            list[list[float]], list[float]: list of long, lat and list of RH value for the long, lat
    """

    """
    -> Doing a left join while merging the dataframes because we want the data for the 34 stations provided in the csv.
    -> also dropping the NaN values as that can create some unnecessary bias in the fitting step of the Gaussian model. 
    """
    merged_data = stations_location_data_raw.merge(precip_data_raw, how='left', left_on='id', right_on='STN').dropna()
    X = merged_data[['lat', 'long']].values.tolist()
    # X = merged_data[['long', 'lat']].values.tolist()  # changed
    y = merged_data[['RH']].values.tolist()
    return X, y


def check_datetime(time):
    """check if datetime is correct and of the correct format

    Args:
        time (str): time of the format YYYYMMDDHH

    Returns:
        error/success code and the datetime object
    """
    format_YYYYMMDDHH = "%Y%m%d%H"
    try:
        if len(time) < 10:
            return 2, None
        date = datetime.strptime(time, format_YYYYMMDDHH)
        if date > datetime.now():
            return 3, None
        return 1, date
    except ValueError:
        return 4, None


def lat_long_validation(latitude, longitude, stations_location_data_raw):
    """tells if the latitude and the longitude provided fall in the Netherlands based on the stations lat long.
    Args:
        latitude (float): latitude of the location to predict
        longitude (float): longitude of the location to predict
        stations_location_data_raw (dataFrame): stations data containing the lat long data of them

    Returns:
        Bool: True if lat long is out of the Netherlands else false
    """
    if latitude > (max(stations_location_data_raw['lat'].tolist()) + 0.2) or \
            latitude < (min(stations_location_data_raw['lat'].tolist()) - 0.2) or \
            longitude > (max(stations_location_data_raw['long'].tolist()) + 0.2) or \
            longitude < (min(stations_location_data_raw['long'].tolist()) - 0.2):
        return True
    return False


def lat_long_validation_v2(lat, long):
    """uses an offline algorithm based on k-d tree to find country associated with the location

    Args:
        lat (float): latitude of the location to predict
        long (float): longitude of the location to predict

    Returns:
        Bool: True if lat long is out of the Netherlands else false

    """
    coords = (lat, long),
    if reverse_geocode.search(coords)[0]['country'] != 'Netherlands':
        return True
    return False
