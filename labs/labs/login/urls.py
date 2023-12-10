from django.urls import re_path,path
from . import views
from rest_framework.schemas import get_schema_view

urlpatterns = [

    re_path('login',views.login),
    re_path('signup',views.signup),
    re_path('test_token',views.test_token)
]