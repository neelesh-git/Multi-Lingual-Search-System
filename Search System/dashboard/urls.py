from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='dashboard'),
    path('getData',views.getData, name='getData')
]
