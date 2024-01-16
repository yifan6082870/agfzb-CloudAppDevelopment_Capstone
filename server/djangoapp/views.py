from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, "djangoapp/about.html", context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, "djangoapp/contact.html", context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request['username']
        psw = request['psw']
        user = authenticate(username=username, password=psw)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, "djangoapp/registration.html", context)
    else:
        username = request['username']
        firstname = request['firstname']
        lastname = request['lastname']
        psw = request['psw']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("We've got a new user {}".format(username))
        
        if user_exist:
            context['message'] = "This user is already registered"
            return render(request, "djangoapp/registration.html", context)
        else:
            user = User.objects.create_user(username=username,
                                            first_name=firstname,
                                            last_name=lastname,
                                            password=psw)
            login(request, user)
            return redirect("djangoapp:index")


# Update the `get_dealerships` view to render the index page with a list of dealerships
#def get_dealerships(request):
#    context = {}
#    if request.method == "GET":
#        return render(request, 'djangoapp/index.html', context)
#https://yifan6082870-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get
def get_dealerships(request):
    if request.method == "GET":
        url = "https://yifan6082870-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "http://127.0.0.1:5000/api/get_reviews"
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        review_list = "reviews: " + " ".join([r.review for r in reviews])
        sentimented_list = review_list + '</br>' + "sentiments: " + " ".join([r.sentiment for r in reviews])
        return HttpResponse(sentimented_list)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        review = {}
        url = "http://127.0.0.1:5000/api/post_review"
        #['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
        review["id"] = 100
        review["dealership"] = 11
        review["review"] = "Synergistic cohesive budgetary management"
        review["name"] = "Jason"
        review["purchase"] = False
        review["purchase_date"] = datetime.utcnow().isoformat()
        review["car_make"] = "BMW"
        review["car_model"] = "x3"
        review["car_year"] = 1994
        review["dealership"] = dealer_id
        json_payload = {}
        json_payload["review"] = review
        res = post_request(url, json_payload)
        return HttpResponse(res)

