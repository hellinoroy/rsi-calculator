# better error
# env/path setup
from dotenv import load_dotenv
import os

# file setup
import json
import datetime

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

# loading env
load_dotenv()
apiKey = os.getenv("API_KEY")
# mock data
# apiKey = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"
# url = 'https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

headers = {
  'Accepts': 'application/json',
  "Accept-Encoding": "deflate, gzip",
  'X-CMC_PRO_API_KEY': apiKey,
}

# api error doesnt need to log the user
# log the user that cause API error
def checkApiError(data: dict) -> dict|None:
  if data["status"]["error_code"] != 0:
    err = {
          "timestamp": data['status']['timestamp'],
          "errorCode": data['status']['error_code'],
          "errorMessage": data['status']['error_message']
        }
    errDir = os.path.join(os.path.dirname(__file__), "apiErrors")
    # make dir if it doesnt exist
    os.makedirs(errDir, exist_ok=True)
    filename = os.path.join(errDir, f"{datetime.datetime.now(datetime.UTC).date()}.txt")

    with open(filename, 'a') as file:
      json.dump(err, file)
      file.write("\n")
    return data['status']['error_message']

   
def requestPrice(slug: str = "dogecoin") -> dict:
  # url = "https://sandbox-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
  url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

  parameters = {
    'convert': "USD",
    'slug': slug
  }

  session = Session()
  session.headers.update(headers)

  try:
    # get request
    response = session.get(url, params=parameters)
    data = json.loads(response.text)

    # check if theres request error
    errorCheck = checkApiError(data)
    if errorCheck:
      return errorCheck      
    return data
    
    
  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)

def requestUsage(user: str = "HOST") -> dict:
  url = "https://pro-api.coinmarketcap.com/v1/key/info"

  session = Session()
  session.headers.update(headers)

  try:
    # get request
    response = session.get(url)
    data = json.loads(response.text)

    # check if theres request error
    errorCheck = checkApiError(data, user)
    if errorCheck:
      return errorCheck
    
    # {'credits_used': 4, 'credits_left': 9996, 'credit_limit_monthly_reset_timestamp': '2025-03-01T00:00:00.000Z'}
    return {
      "credits_used": data["data"]["usage"]["current_month"]["credits_used"], 
      "credits_left": data["data"]["usage"]["current_month"]["credits_left"], 
      "credit_limit_monthly_reset_timestamp": data["data"]["plan"]["credit_limit_monthly_reset_timestamp"]}
    
  except (ConnectionError, Timeout, TooManyRedirects) as e:
  	print(e)

if __name__ == '__main__':
  requestPrice("dogecoin,bitcoin")