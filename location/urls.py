from django.urls import path
from . import views

urlpatterns = [
    # City URLs
    path('cities/', views.CityListView.as_view(), name='city-list'),
    path('cities/<int:pk>/', views.CityDetailView.as_view(), name='city-detail'),
    
    # District URLs
    path('districts/', views.DistrictListView.as_view(), name='district-list'),
    path('districts/<int:pk>/', views.DistrictDetailView.as_view(), name='district-detail'),
]
