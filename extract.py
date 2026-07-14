import requests
import pandas
import os
from dotenv import load_dotenv

load_dotenv()

api_ID = os.getenv("api_ID")
api_key = os.getenv("api_key")

req = requests.get(f"http://api.adzuna.com/v1/api/jobs/gb/search/1?app_id={api_ID}&app_key={api_key}&results_per_page=20&what=javascript%20developer&content-type=application/json")

print(req.text)