from fastapi import HTTPException, status

from agent.vector_searcher.chroma.loader import ChromaDBLoader


def load_data(request):
    try:
        loader = ChromaDBLoader()
        loader.load_data(
            table=request.table,
            sql_table=request.sql_table,
            id_column=request.id_column,
            text_columns=request.text_columns,
            column_names=request.column_names,
            metadata_columns=request.metadata_columns
        )
        return {"details": f"Данные {request.table} успешно загружены в ChromaDB."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
