from django.urls import path
from . import views

urlpatterns = [
    # City URLs
    path('cities/', views.CityListView.as_view(), name='city-list'),

    # District URLs
    path('districts/', views.DistrictListView.as_view(), name='district-list'),
]
