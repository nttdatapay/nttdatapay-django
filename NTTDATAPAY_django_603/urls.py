from django.urls import include, path
from . import views

urlpatterns = [
    path('',  views.payview),
    path('response/',  views.resp),
]