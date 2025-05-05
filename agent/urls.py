from django.urls import path
from agent.views import (
    ChromaFetchDataView,
    ChromaDeleteCollectionsView,
    ChromaResetView,
    AgentChatView,
    ChromaLoadDataView,
    StateDeleteMessagesView,
    StateGetSimpleConversationView,
    StateGetMessagesView,
    StateGetGraphPngView
)

app_name = 'agent'

urlpatterns = [
    path('chroma/load_data/', ChromaLoadDataView.as_view(), name='chroma_load_data'),
    path('chroma/fetch_data/', ChromaFetchDataView.as_view(), name='chroma_fetch_data'),
    path('chroma/delete_collections/', ChromaDeleteCollectionsView.as_view(), name='chroma_delete_collections'),
    path('chroma/reset/', ChromaResetView.as_view(), name='chroma_reset'),
    path('chat/', AgentChatView.as_view(), name='agent-chat'),
    path('states/delete_all_messages/', StateDeleteMessagesView.as_view(), name='delete_all_messages'),
    path('states/get_simple_conversation/', StateGetSimpleConversationView.as_view(), name='get_simple_conversation'),
    path('states/get_messages/', StateGetMessagesView.as_view(), name='get_messages'),
    path('states/get_graph_png/', StateGetGraphPngView.as_view(), name='get_graph_png'),
] 