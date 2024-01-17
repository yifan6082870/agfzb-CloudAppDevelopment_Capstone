import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

watson_url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/11a55720-8653-43ce-8cb8-2f15c06d1836"
watson_api = "zcK0uOFHSYkpn8x3MLOBrH4b29As3lWEI2wOYlh3IThB"

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print(json_data)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    print(json_payload)
    try:
        # Call get method of requests library with URL and parameters
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    print(json_data)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealers_by_id(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=kwargs['id'])
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative


def get_dealer_reviews_from_cf(url, **kwargs):
    result = []
    json_result = get_request(url, id=kwargs['dealer_id'])
    if json_result:
        reviews = json_result
        for review in reviews:
            dealer_review = DealerReview(
                id = review["id"],
                dealership = review["dealership"],
                name = review["name"],
                purchase = review["purchase"],
                review = review["review"],
                purchase_date = review["purchase_date"],
                car_make = review["car_make"],
                car_model = review["car_model"],
                car_year = review["car_year"],
                sentiment = ""
            )
            dealer_review.sentiment = analyze_review_sentiments(dealer_review.review)
            result.append(dealer_review)
    return result

def analyze_review_sentiments(text):
    body = {"text": text, "features": {"sentiment": {"document": True}}}
    response = requests.post(
        watson_url + "/v1/analyze?version=2019-07-12",
        headers={"Content-Type": "application/json"},
        json=body,  # Use json parameter for automatic conversion
        auth=HTTPBasicAuth("apikey", watson_api),
    )

    # Check if request was successful
    if response.status_code == 200:
        sentiment = response.json()["sentiment"]["document"]["label"]
        return sentiment
    return "N/A"

