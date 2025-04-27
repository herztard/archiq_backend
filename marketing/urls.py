from django.urls import path
from .views import BannerListCreateView, BannerDetailView

urlpatterns = [
    path('banners/', BannerListCreateView.as_view(), name='banner-list-create'),
    path('banners/<int:pk>/', BannerDetailView.as_view(),       name='banner-detail'),
]
