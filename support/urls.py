from django.urls import path
from .views import (
    ReportListView,
    ReportDetailView,
)

urlpatterns = [
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),

]
