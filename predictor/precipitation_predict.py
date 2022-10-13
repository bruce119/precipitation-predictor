from helper.helper_functions import load_csv_data_cleaned, prepare_data, get_X_y
from knmi.knmi_loader import get_precipitation_data
from lib.kriging import Precipitation


def get_predicted_data(start, end, lat, long):
    """returns the predicted data for the lat long provided

    Args:
        start (str): start time for fetching the data from the weather stations(YYYYMMDDHH
        end (str): end time for fetching the data from the weather stations(YYYYMMDDHH)
        lat: (str)latitude of the location for which we are to predict the precipitation
        long: (str)longitude of the location for which we are to predict the precipitation

    Returns:
        float, float: precipitation (0.1 mm) for the lat long and the standard deviation is
                                                returned
    """
    stations_location_data_raw = load_csv_data_cleaned('./data/weatherstations-NL.csv')
    precip_data_raw = get_precipitation_data(start, end)
    stations_location_data_raw, precip_data_raw = prepare_data(stations_location_data_raw, precip_data_raw)
    X, y = get_X_y(stations_location_data_raw, precip_data_raw)
    model = Precipitation()
    model.fit(X, y)
    # return model.predict([[long, lat]])# changed
    return model.predict([[lat, long]])
