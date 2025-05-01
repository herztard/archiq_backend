from django.urls import path
from . import views

urlpatterns = [
    path('residential-complexes/', views.ResidentialComplexListView.as_view(), name='residential-complex-list'),
    path('residential-complexes/<int:pk>/', views.ResidentialComplexDetailView.as_view(), name='residential-complex-detail'),
    path('residential-complexes/<int:pk>/photos/', views.ResidentialComplexPhotoListView.as_view(), name='residential-complex-photo-list'),
    path('residential-complexes/<int:pk>/photos/<int:photo_id>/', views.ResidentialComplexPhotoDetailView.as_view(), name='residential-complex-photo-detail'),
    path('residential-complexes/<int:pk>/upload-photo/', views.ResidentialComplexPhotoUploadView.as_view(), name='residential-complex-upload-photo'),
    
    path('blocks/', views.BlockListView.as_view(), name='block-list'),
    path('blocks/<int:pk>/', views.BlockDetailView.as_view(), name='block-detail'),
    
    path('properties/', views.PropertyListView.as_view(), name='property-list'),
    path('properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),
    
    path('properties/<int:property_id>/photos/', views.PropertyPhotoListView.as_view(), name='property-photo-list'),
    path('properties/<int:property_id>/photos/<int:photo_id>/', views.PropertyPhotoDetailView.as_view(), name='property-photo-detail'),
    path('properties/<int:property_id>/videos/', views.PropertyVideoListView.as_view(), name='property-video-list'),
    path('properties/<int:property_id>/videos/<int:video_id>/', views.PropertyVideoDetailView.as_view(), name='property-video-detail'),
]
