from django.http import HttpResponse
from requests import request

def index(request):
    return HttpResponse("Skills app working!")
