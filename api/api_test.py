
from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)
"""
Full array of test cases for almost all possible scenarios to validate the API. 
"""


def test_read_main():
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = client.get("/precipitation?latitude=52.18&longitude=4.42&time=2022010110", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "Success", "body": {"code": 200, "predicted_precipitation(0.1 mm)": 0.5,
                                                             "standard_deviation": [1.5004933962662892]}}


def test_failure_params_main():
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = client.get("/precipitation?lattude=50.81&longitude=6.2&time=2022010101", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "Failure",
                               "error": {"code": 401, "message": "Latitude/Longitude/time parameter is incorrect",
                                         "correction": "Please provide proper latitude/longitude/time in query params "
                                                       "like latitude=52.48&longitude=6.2&time=2022101001 "}}


def test_failure_area_main():
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = client.get("/precipitation?latitude=500.81&longitude=6.2&time=2022010101", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "Failure", "error": {"code": 401,
                                                              "message": "Latitude/Longitude does not belong to the "
                                                                         "desired area",
                                                              "correction": "The Latitude/Longitude should belong "
                                                                            "Netherlands ex:- (lat- 52.48, "
                                                                            "Long- 6.2)"}}


def test_failure_param_value_main():
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = client.get("/precipitation?latitude=50asd.81&longitude=6.2&time=2022010101", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "Failure",
                               "error": {"code": 401, "message": "Latitude/Longitude should be of type float",
                                         "correction": "Latitude/Longitude should be like - "
                                                       "latitude=52.48&longitude=6.2"}}


def test_failure_datetime_type_main():
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = client.get("/precipitation?latitude=52.181&longitude=4.42&time=202201010", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "Failure", "error": {"code": 401, "message": "Time must be of type YYYYMMDDHH",
                                                              "correction": "ex:- 2022010112"}}


def test_failure_datetime_greater_main():
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = client.get("/precipitation?latitude=52.18&longitude=4.42&time=2023010101", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "Failure",
                               "error": {"code": 401, "message": "Given time is grater than current time",
                                         "correction": "Time provided should be anytime before today"}}


def test_failure_datetime_incorrect_main():
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = client.get("/precipitation?latitude=52.18&longitude=4.42&time=2023010s101", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "Failure", "error": {"code": 401, "message": "Please Check the time properly",
                                                              "correction": "check if the time is before today and of "
                                                                            "the format YYYYMMDDHH like 2022010112"}}


