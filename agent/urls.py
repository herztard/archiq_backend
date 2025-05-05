from django.urls import path
from .views import (
    ChromaLoadDataView,
    ChromaFetchDataView,
    ChromaDeleteCollectionsView,
    ChromaResetView
)

app_name = 'vector_search'

urlpatterns = [
    path('chroma/load_data/', ChromaLoadDataView.as_view(), name='chroma_load_data'),
    path('chroma/fetch/', ChromaFetchDataView.as_view(), name='chroma_fetch_data'),
    path('chroma/delete_collections/', ChromaDeleteCollectionsView.as_view(), name='chroma_delete_collections'),
    path('chroma/reset/', ChromaResetView.as_view(), name='chroma_reset'),
] 