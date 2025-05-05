from django.urls import path
from agent.views import (
    ChromaFetchDataView,
    ChromaDeleteCollectionsView,
    ChromaResetView,
    AgentChatView,
    ChromaLoadDataView
)

app_name = 'agent'

urlpatterns = [
    path('chroma/load_data/', ChromaLoadDataView.as_view(), name='chroma_load_data'),
    path('chroma/fetch_data/', ChromaFetchDataView.as_view(), name='chroma_fetch_data'),
    path('chroma/delete_collections/', ChromaDeleteCollectionsView.as_view(), name='chroma_delete_collections'),
    path('chroma/reset/', ChromaResetView.as_view(), name='chroma_reset'),
    path('chat/', AgentChatView.as_view(), name='agent-chat'),
] 