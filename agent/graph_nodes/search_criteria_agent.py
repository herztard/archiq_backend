from typing import Dict, Any, Optional
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
from pydantic import BaseModel

from archiq_backend import settings
from agent.graph_nodes.agent_state import AgentState

load_dotenv()

# Create a ChatOpenAI instance
model = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.0, api_key=settings.OPENAI_API_KEY)

class SearchCriteriaObject(BaseModel):
    min_floor: Optional[int] = None
    max_floor: Optional[int] = None

    min_area: Optional[float] = None
    max_area: Optional[float] = None

    min_price: Optional[float] = None
    max_price: Optional[float] = None

    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None


structured_llm = model.with_structured_output(SearchCriteriaObject, method="json_mode")

SYSTEM_MESSAGE = """
You are an AI assistant for a real estate search application. Your task is to interpret user queries about property searches and generate a JSON object representing the search criteria. The criteria should follow this structure:

{
    "min_floor": Optional[int],
    "max_floor": Optional[int],
    "min_area": Optional[float],
    "max_area": Optional[float],
    "min_price": Optional[float],
    "max_price": Optional[float],
    "min_rooms": Optional[int],
    "max_rooms": Optional[int]
}

Guidelines:
1. If the user's query indicates a brand‐new search (e.g., “I want 3 rooms in a different district”), discard all prior criteria and start fresh.
2. If it’s a follow‐up (e.g., “Actually, make it up to 120 m²” or “Also show me complexes in Alatau”), merge or overwrite only the specified fields.
3. For location, `district` and `residential_complex` are mutually exclusive: if the user specifies a complex, drop any previously set district; if they specify a district, drop any previously set complex.
4. For numeric ranges, use `min_` and `max_` prefixes appropriately.
5. Include only those fields mentioned or clearly implied.
6. Respond with exactly the JSON object—no extra text.
"""

def search_criteria_agent(state: AgentState) -> Dict[str, Any]:
    last_tool_call = state["messages"][-1].tool_calls[0]
    tool_call_id = last_tool_call["id"]
    user_query = last_tool_call["args"]["request"]

    current_criteria = state.get("search_criteria", {})
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": f"Current Criteria: {json.dumps(current_criteria, indent=2)}"},
        {"role": "user", "content": f"User Query: {user_query}"},
    ]

    try:
        response = structured_llm.invoke(messages)
        new_search_criteria = response.dict(exclude_none=True)
    except Exception as e:
        return {
            "search_criteria": current_criteria,
            "messages": [
                ToolMessage(content="Entering search criteria agent", tool_call_id=tool_call_id),
                AIMessage(content=f"Failed to parse search criteria. Error: {e}"),
            ],
        }

    response_message = "I've updated your search criteria based on your request. Here's what I understood:\n"
    for key, value in new_search_criteria.items():
        if value is not None:
            response_message += f"- {key.replace('_', ' ').capitalize()}: {value}\n"

    return {
        "search_criteria": new_search_criteria,
        "messages": [
            ToolMessage(content="Entering search criteria agent.", tool_call_id=tool_call_id),
            AIMessage(content=response_message),
        ],
    }