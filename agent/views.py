from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse

from agent.vector_db import VectorDBConnection
from agent.chroma_loader import ChromaDBLoader
from agent.chroma_fetcher import ChromaDBFetcher
from .serializers import ChromaLoadRequestSerializer


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


class ChromaFetchDataView(views.APIView):
    def get(self, request):
        fetcher = ChromaDBFetcher()
        data = dict(fetcher.fetch_all_data_all_collections())
        return JsonResponse(data)


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


class ChromaResetView(views.APIView):
    def get(self, request):
        chroma_client = VectorDBConnection.get_client()
        chroma_client.reset()
        return Response({"success": "Chroma Client has been reset."}, status=status.HTTP_200_OK)