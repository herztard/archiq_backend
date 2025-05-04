from django.urls import path
from .views import BannerListCreateView

urlpatterns = [
    path('banners/', BannerListCreateView.as_view(), name='banner-list-create'),
]
