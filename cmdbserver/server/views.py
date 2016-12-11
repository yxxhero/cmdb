from django.shortcuts import render,redirect
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
import json
# Create your views here.
def index(request):
    return render_to_response("index.html")    
def hostinfolist(request):
    hostinfo={"aaData":{"id": "id", "ip": "ip", "minionid": "minionid", "system": "system", "project": "project","location":"location","services":"services","status":"status","operat":"operation"}}
    return HttpResponse(json.dumps(hostinfo))
