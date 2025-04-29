import json
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langgraph.prebuilt import tools_condition
from typing import Literal, List, Dict


from agent.graph_nodes.prompts import SYSTEM_PROMPT
from archiq_backend import settings
from agent.graph_nodes.agent_state import AgentState
from agent.tools.general_tools import ToSearchCriteriaAgent, ToSearchDescriptiveDataAgent


load_dotenv()

llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.7, api_key=settings.OPENAI_API_KEY)

main_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

main_tools = [ToSearchCriteriaAgent, ToSearchDescriptiveDataAgent]

main_agent_runnable = main_agent_prompt | llm.bind_tools(main_tools, parallel_tool_calls=False)


def route_main_agent(state: AgentState) -> Literal[
    "__end__",
    "search_criteria_agent",
    "search_database_agent"
]:

    route = tools_condition(state)
    if route == "__end__":
        return "__end__"
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == ToSearchCriteriaAgent.__name__:
            return "search_criteria_agent"
        if tool_calls[0]["name"] == ToSearchDescriptiveDataAgent.__name__:
            return "search_database_agent"

    raise ValueError("Invalid route")