from django.urls import path
from . import views

urlpatterns = [
    path('residential-complexes/', views.ResidentialComplexListView.as_view(), name='residential-complex-list'),
    path('residential-complexes/<int:pk>/', views.ResidentialComplexDetailView.as_view(), name='residential-complex-detail'),

    path('blocks/', views.BlockListView.as_view(), name='block-list'),
    path('blocks/<int:pk>/', views.BlockDetailView.as_view(), name='block-detail'),
    
    path('properties/', views.PropertyListView.as_view(), name='property-list'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),

]
