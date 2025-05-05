from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.conf import settings
from psycopg import OperationalError
from langchain_core.messages import HumanMessage, ToolMessage
from typing import cast
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from agent.vector_db import VectorDBConnection
from agent.chroma_loader import ChromaDBLoader
from agent.chroma_fetcher import ChromaDBFetcher
from .serializers import ChromaLoadRequestSerializer
from agent.serializers import QueryCreateSerializer, QueryResponseSerializer
from agent.graph_builder import create_graph
from agent.agent_state import AgentState


@extend_schema(
    tags=["ChromaDB"],
    description="Load data from SQL table into ChromaDB collection",
    request=ChromaLoadRequestSerializer,
    responses={200: {"description": "Data loaded successfully"}}
)
class ChromaLoadDataView(views.APIView):
    def post(self, request):
        serializer = ChromaLoadRequestSerializer(data=request.data)
        if serializer.is_valid():
            loader = ChromaDBLoader()
            loader.load_data(
                table=serializer.validated_data['table'],
                sql_table=serializer.validated_data['sql_table'],
                id_column=serializer.validated_data['id_column'],
                text_columns=serializer.validated_data['text_columns'],
                metadata_columns=serializer.validated_data.get('metadata_columns'),
                column_names=serializer.validated_data.get('column_names', {})
            )
            return Response({'status': 'Data loaded successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["ChromaDB"],
    description="Fetch all data from all ChromaDB collections",
    responses={200: {"description": "Data retrieved successfully"}}
)
class ChromaFetchDataView(views.APIView):
    def get(self, request):
        fetcher = ChromaDBFetcher()
        data = dict(fetcher.fetch_all_data_all_collections())
        return JsonResponse(data)


@extend_schema(
    tags=["ChromaDB"],
    description="Delete all collections from ChromaDB",
    responses={200: {"description": "Collections deleted"}}
)
class ChromaDeleteCollectionsView(views.APIView):
    def post(self, request):
        chroma_client = VectorDBConnection.get_client()
        collections = chroma_client.list_collections()
        print("Найденные коллекции:", collections)

        for collection_name in collections:
            chroma_client.delete_collection(name=collection_name)
            print(f"Коллекция '{collection_name}' удалена.")

        print("Оставшиеся коллекции:", chroma_client.list_collections())
        return Response({'status': 'Collections deleted'}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["ChromaDB"],
    description="Reset ChromaDB client",
    responses={200: {"description": "ChromaDB client reset"}}
)
class ChromaResetView(views.APIView):
    def get(self, request):
        chroma_client = VectorDBConnection.get_client()
        chroma_client.reset()
        return Response({"success": "Chroma Client has been reset."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Agent"],
    description="Chat with the AI agent system",
    request=QueryCreateSerializer,
    responses={200: QueryResponseSerializer},
    examples=[
        OpenApiExample(
            "Chat Request Example",
            value={
                "query": "What properties are available in Almaty?",
                "user_details": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "johndoe",
                    "user_telegram_id": 123456789
                },
                "message_details": {
                    "chat_id": 123456789,
                    "created_at": "2023-05-22T10:30:00Z"
                }
            },
            request_only=True,
        ),
        OpenApiExample(
            "Chat Response Example",
            value={"result": "I found several properties in Almaty. Here are the details..."},
            response_only=True,
        ),
    ],
)
class AgentChatView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = QueryCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query_data = serializer.validated_data
        user_details = query_data.get('user_details', {})
        question = query_data.get('query', '')
        
        print("User Telegram ID:", user_details.get('user_telegram_id'))
        print("First Name:", user_details.get('first_name'))
        print("Last Name:", user_details.get('last_name'))
        print("Username:", user_details.get('username'))
        print("Query:", question)
        
        # Get or create graph
        if not hasattr(self, 'graph'):
            self.graph = create_graph()
        
        config = {
            "configurable": {
                "thread_id": str(user_details.get('user_telegram_id', '')),
            }
        }
        
        try:
            response = self.process_single_question(self.graph, question, config)
        except OperationalError as e:
            print("OperationalError during graph invocation:", e)
            self.graph = create_graph()
            response = self.process_single_question(self.graph, question, config)
        
        print("Response:", response)
        
        response_serializer = QueryResponseSerializer({"result": response})
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    def get_human_approval(self, tool_call):
        # In a real API, you might not use this interactive approach
        # For now, auto-approve all tool calls
        return "yes"
    
    def process_single_question(self, graph, question, config):
        """Process a single question and return the response."""
        state = cast(
            AgentState,
            {
                "messages": [HumanMessage(content=question)],
                "thread_id": str(config["configurable"]["thread_id"]),
                "search_criteria": {},
                "last_updated_keys": []
            }
        )
        
        for event in graph.stream(input=state, config=config, stream_mode="values"):
            if "messages" in event:
                # For logging purposes
                print(f"Agent: {event['messages'][-1].content}")
        
        snapshot = graph.get_state(config)
        
        while snapshot.next:
            last_message = snapshot.values["messages"][-1]
            if last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    user_input = self.get_human_approval(tool_call)
                    
                    if user_input.strip().lower() == "yes":
                        result = graph.invoke(None, config)
                    else:
                        result = graph.invoke(
                            {
                                "messages": [
                                    ToolMessage(
                                        tool_call_id=last_message.tool_calls[0]["id"],
                                        content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                                    )
                                ]
                            },
                            config,
                        )
                    snapshot = graph.get_state(config)
        
        return snapshot.values["messages"][-1].content