from django.urls import path
from . import hello

urlpatterns = [
    path('api/v1/hello-world-2', hello.hello)
]