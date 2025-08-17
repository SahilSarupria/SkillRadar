from django.urls import path
from . import views

urlpatterns = [
    # Example route (replace with your actual view)
    path('', views.index, name='analyzer-index'),
]
