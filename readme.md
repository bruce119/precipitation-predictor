This document contains the steps to set up the python environment by creating a virtualenv and installing the packages 
## instructions to use the API(written with FastAPI)

* step 0: Make sure redis is running locally on `127.0.0.1` and port `6379`, or the file `helper/redis_connector.py` would need to be changed

* step 1: change to precipitation-prediction-api directory `cd precipitation-predictor`

* Step 2: Create the virtualenv [link](https://docs.python.org/3/library/venv.html) or `python3 -m venv venv_folder_name`

* Step 3: Activate the virtualenv `source venv_folder_name/bin/activate`

* Step 4: Use the requirements.txt file to install all the required packages needed for both the API and for the assignment.ipynb notebook `pip install -r requirements.txt`
  * optional step - (if you want to load historical data(`2019-10-17` to `2022-10-19`) from `knmi_database` already present in `/data` folder to redis): run `python helper/load_to_redis.py`  NB:- (will take some time)
  * optional step - (if you want to load 3 years historical data directly to redis and db from knmi-API): run `python helper/history_data_to_db_and_redis.py`
  * optional step - (if you want to load 3 years historical data to db from today, then load it to redis ): First run `python helper/history_data_to_db.py` then run `python helper/load_to_redis.py`   NB:- (will take some time) 
  * optional step - (if you want to run 3 years historical load and load directly to redis from knmi-API):  run `python helper/history_data_to_redis.py`
  

* Step 5: Run the command `sh run_app.sh` to start the FastAPI application

* Step 6: To see the api in action head over to your browser and use this url  'http://0.0.0.0:8080/precipitation?latitude=52.20&longitude=5.90&time=2022010621'
or http://0.0.0.0:8080/precipitation?latitude=52.20&longitude=5.90

* optional: To run the tests Run the command `pytest api/api_test.py`

### The tests will automatically run and check if all systems are operational before running the API.
#### used uvicorn server to run with 5 workers for speeding up the response time. 
#### * Stress Test with locust can also be done by running `locust -f stress_test/stress_test.py` and then going to the link provided(make sure the API is running before doing this). In the host section put `http://0.0.0.0:8080`.

The end :)
