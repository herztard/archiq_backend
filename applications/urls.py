from django.urls import path
from .views import ApplicationCreateView, ApplicationListView, ApplicationDetailView

app_name = 'applications'

urlpatterns = [
    path('apply/', ApplicationCreateView.as_view(), name='create_application'),
    
    path('', ApplicationListView.as_view(), name='list_applications'),
    path('<int:pk>/', ApplicationDetailView.as_view(), name='application_detail'),
] 