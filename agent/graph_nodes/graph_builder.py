from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import tools_condition, ToolNode
from psycopg import OperationalError, connect
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from archiq_backend import settings
from agent.graph_nodes.search_database_agent import search_database_tools, \
    search_database_agent_runnable
from agent.graph_nodes.agent_state import AgentState
from agent.graph_nodes.search_criteria_agent import search_criteria_agent
from agent.graph_nodes.main_agent import main_agent_runnable, route_main_agent
from agent.graph_nodes.criteria_db_query_node import query_real_estate_db
from agent.graph_nodes.create_node import Assistant, back_to_main, create_tool_node

def create_graph() -> CompiledGraph:
    builder = StateGraph(AgentState)

    # main agent
    builder.add_node("main_agent", Assistant(main_agent_runnable))

    builder.set_entry_point("main_agent")
    builder.add_conditional_edges("main_agent", route_main_agent)

    # search criteria agent
    builder.add_node("search_criteria_agent", search_criteria_agent)
    builder.add_node("query_real_estate_db", query_real_estate_db)

    # search database agent
    builder.add_node("search_database_agent", Assistant(search_database_agent_runnable, True))
    builder.add_node("tools", ToolNode(search_database_tools))

    builder.add_conditional_edges("search_database_agent", tools_condition)
    builder.add_edge("tools", "main_agent")

    builder.add_edge("search_criteria_agent", "query_real_estate_db")
    builder.add_edge("query_real_estate_db", "main_agent")

    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
        "row_factory": dict_row,
        "keepalives": 1,
        "keepalives_idle": 15,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }

    db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

    try:
        conn = connect(db_url, **connection_kwargs)
        validate_connection(conn)
        print("Direct connection validated successfully!")
        conn.close()
    except Exception as e:
        print("Direct connection failed or health check failed:", e)

    pool = ConnectionPool(conninfo=db_url, max_size=20, kwargs=connection_kwargs)
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()
    return builder.compile(checkpointer=checkpointer)

load_dotenv()

def validate_connection(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            if result is None:
                raise OperationalError("Health check query returned no result.")
    except Exception as e:
        raise OperationalError(f"Connection validation failed: {e}")


def ensure_active_connection(pool, db_url, connection_kwargs):
    try:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            print("Connection is active.")
        pool.putconn(conn)
        return pool
    except Exception as e:
        print("Connection inactive or closed; reinitializing connection pool...", e)
        pool.close()
        new_pool = ConnectionPool(conninfo=db_url, max_size=20, kwargs=connection_kwargs)
        return new_pool

