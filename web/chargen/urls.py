# file mygame/web/chargen/urls.py

from django.conf.urls import url
from django.urls import path
from web.chargen import views

app_name = 'chargen'
urlpatterns = [
        path('', views.index, name='index'),
        path('<int:app_id>/', views.detail, name='detail'),
        path('create/', views.creating, name='creating'),
        ]
