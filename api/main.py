from datetime import datetime, timedelta
from typing import Union, Optional

import pytz
from fastapi import FastAPI

from helper.helper_functions import check_datetime, load_csv_data_cleaned, lat_long_validation, lat_long_validation_v2
from predictor.precipitation_predict import get_predicted_data
from response.error_response import ErrorResponse
from response.success_response import PrecipitationResponse

app = FastAPI()

@app.get("/precipitation")
def read_data(
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
        time: Union[str, None] = None
):
    """
    start the fast API to start serving

    Args:
        latitude: (str)latitude of the location for which we are to predict the precipitation
        longitude: (str)longitude of the location for which we are to predict the precipitation
        time: (str)time at which we want to predict the precipitation must be of the form YYYYMMDD

    Returns:
        Json response for failure or success as defined in response folder
    """

    """
    Check for validating if proper parameters are present or not in the query parameters.
    parameters that should be present:- latitude, longitude, time.
    """
    if (not latitude) or (not longitude) or (not time):
        e_response = ErrorResponse()
        e_response.error_code = 401
        e_response.error_message = "Latitude/Longitude/time parameter is incorrect"
        e_response.correct_params = "Please provide proper latitude/longitude/time in query params like " \
                                    "latitude=52.48&longitude=6.2&time=2022101001 "
        return e_response.return_json()

    """
    Check for validation of the latitude and longitude provided in the query params:
        1. if they are float convertible or not(of type float or not).
        2. if the fall in the desired location i.e. Netherlands.
            -> Two different approaches explained in lat_long_validation,lat_long_validation_v2 in helper module 
               under helper_functions.
    """
    try:
        latitude, longitude = float(latitude), float(longitude)
        stations_location_data_raw = load_csv_data_cleaned('./data/weatherstations-NL.csv')

        if lat_long_validation_v2(latitude, longitude):
            e_response = ErrorResponse()
            e_response.error_code = 401
            e_response.error_message = "Latitude/Longitude does not belong to the desired area"
            e_response.correct_params = "The Latitude/Longitude should belong Netherlands ex:- (lat- 52.48, Long- 6.2)"
            return e_response.return_json()
    except Exception as e:
        print(e)
        e_response = ErrorResponse()
        e_response.error_code = 401
        e_response.error_message = "Latitude/Longitude should be of type float"
        e_response.correct_params = "Latitude/Longitude should be like - latitude=52.48&longitude=6.2"
        return e_response.return_json()

    """
    Check for validation of time provided in the query params
        check_datetime function returns code based on time provided to it:-
        1. if code is 1 then time is proper and of the valid format.
        2. if code is 2 then time is not formatted properly(proper formatYYYYMMDDHH).
        3. if code is 3 then a future time has been provided.
        4. if code is 4 then there is some other issue with the time provided and needs to be rechecked.
    
    finally the last exception handles any other misc errors such as someone gives in the time for present etc and logs
    it for future checks.
    """
    try:
        code, time_val = check_datetime(time)
        if code == 1:
            start_time = (time_val - timedelta(days=1)).strftime('%Y%m%d%H')
            end_time = time_val.strftime('%Y%m%d%H')
            pred_precip, std_dev = get_predicted_data(start_time, end_time, latitude, longitude)
            s_response = PrecipitationResponse()
            s_response.success_code = 200
            s_response.precipitation_value = pred_precip if pred_precip > 0.5 else 0.5
            s_response.std_dev = std_dev
            return s_response.return_json()
        elif code == 2:
            e_response = ErrorResponse()
            e_response.error_code = 401
            e_response.error_message = "Time must be of type YYYYMMDDHH"
            e_response.correct_params = "ex:- 2022010112"
            return e_response.return_json()
        elif code == 3:
            e_response = ErrorResponse()
            e_response.error_code = 401
            e_response.error_message = "Given time is grater than current time"
            e_response.correct_params = "Time provided should be anytime before today"
            return e_response.return_json()
        else:
            e_response = ErrorResponse()
            e_response.error_code = 401
            e_response.error_message = "Please Check the time properly"
            e_response.correct_params = "check if the time is before today and of the format YYYYMMDDHH like 2022010112"
            return e_response.return_json()
    except Exception as e:
        e_response = ErrorResponse()
        e_response.error_code = 500
        e_response.error_message = "INTERNAL SERVER ERROR"
        e_response.error_message = "KNMI did not produce any data please check the time and lat/long input"
        return e_response.return_json()
