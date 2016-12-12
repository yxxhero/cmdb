from django.shortcuts import render,redirect
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
import json
from forms import userregister
# Create your views here.
def index(request):
    return render_to_response("index.html")    
def login(request):
    return render_to_response("signin.html")
def register(request):
    form=userregister()
    return render_to_response("signup.html",{"user":form})
