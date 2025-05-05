from rest_framework import serializers
from typing import List, Dict, Optional
from datetime import datetime


class ChromaLoadRequestSerializer(serializers.Serializer):
    table = serializers.CharField(help_text="Name of the collection to create in ChromaDB")
    sql_table = serializers.CharField(help_text="Name of SQL table to fetch data from")
    id_column = serializers.CharField(help_text="Name of the ID column in the SQL table")
    text_columns = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of column names containing text data to be vectorized"
    )
    column_names = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        help_text="Dictionary mapping database column names to display names",
        required=False,
        default=dict
    )
    metadata_columns = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of column names to include as metadata",
        required=False,
        allow_empty=True,
        allow_null=True
    )


class UserDetailsSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)
    username = serializers.CharField(required=False, allow_null=True)
    user_telegram_id = serializers.IntegerField(required=False, allow_null=True)


class QueryDetailsSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class QueryCreateSerializer(serializers.Serializer):
    query = serializers.CharField()
    user_details = UserDetailsSerializer()
    message_details = QueryDetailsSerializer()


class QueryResponseSerializer(serializers.Serializer):
    result = serializers.CharField()


# State management serializers
class StateBaseSerializer(serializers.Serializer):
    thread_id = serializers.CharField()


class StateDeleteSerializer(StateBaseSerializer):
    pass


class StateOutSerializer(StateBaseSerializer):
    result = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()


class StateMessagesOutSerializer(StateBaseSerializer):
    messages = serializers.ListField(child=serializers.CharField()) 