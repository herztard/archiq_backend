from rest_framework import serializers
from typing import List, Dict, Optional


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