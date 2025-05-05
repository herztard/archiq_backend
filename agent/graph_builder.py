from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import tools_condition, ToolNode
from psycopg import OperationalError
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from django.conf import settings

from agent.agent_state import AgentState
from agent.search_database_agent import search_database_tools, search_database_agent_runnable
from agent.search_criteria_agent import search_criteria_agent
from agent.main_agent import main_agent_runnable, route_main_agent
from agent.criteria_db_query_node import query_real_estate_db
from agent.create_node import Assistant, back_to_main, create_tool_node

load_dotenv()

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

    db_credentials = settings.DATABASES['default']
    db_url = f"postgresql://{db_credentials['USER']}:{db_credentials['PASSWORD']}@{db_credentials['HOST']}:{db_credentials['PORT']}/{db_credentials['NAME']}"

    try:
        pool = ConnectionPool(conninfo=db_url, max_size=20, kwargs=connection_kwargs)
        validate_connection(pool)
        print("PostgreSQL connection pool validated successfully!")
    except Exception as e:
        print(f"PostgreSQL connection setup failed: {e}")

    checkpointer = PostgresSaver(pool)
    checkpointer.setup()
    return builder.compile(checkpointer=checkpointer)


def validate_connection(pool):
    """Validate the PostgreSQL connection pool"""
    conn = None
    try:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            if result is None:
                raise OperationalError("Health check query returned no result.")
    except Exception as e:
        raise OperationalError(f"Connection validation failed: {e}")
    finally:
        if conn:
            pool.putconn(conn)

