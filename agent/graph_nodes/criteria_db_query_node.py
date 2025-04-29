from typing import Dict, Any
import ast
from langchain.schema import AIMessage
from agent.graph_nodes.agent_state import AgentState



def query_real_estate_db(state: AgentState) -> Dict[str, Any]:
    search_criteria = state.get("search_criteria", {})
    messages_content = "NO DATA, INSTANCE NOT WORKING FOR NOW"
    return {"messages": [AIMessage(content=messages_content)]}
