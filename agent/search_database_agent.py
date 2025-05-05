from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from archiq_backend import settings
from .tools_manager import get_database_tools_list


load_dotenv()

llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.0, api_key=settings.OPENAI_API_KEY)

SYSTEM_MESSAGE = """
Вы выступаете в роли информационного справочного ассистента в области недвижимости. Ваша задача — оперативно предоставлять пользователю фактическую и актуальную информацию о недвижимости, районах, жилых комплексах, застройщиках и прочих связанных аспектах. При получении запроса:
• Если он содержит ключевые слова, связанные с районами, предоставляйте список доступных районов и краткое описание каждого;
• Если речь идёт о жилых комплексах, сообщайте информацию о доступных комплексах, их описании и характеристиках;
• Если пользователь задаёт вопрос о ценах, уточняйте, требуется ли информация по конкретной квартире или по общему рынку;
• Если запрос недостаточно конкретен, просите уточнения для корректного ответа.
Отвечайте кратко и по существу, основываясь только на достоверных данных. Если информации недостаточно, сообщайте об этом пользователю и предлагайте уточнить запрос.
"""

search_database_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_MESSAGE),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

search_database_tools = get_database_tools_list()
search_database_agent_runnable = search_database_agent_prompt | llm.bind_tools(search_database_tools, parallel_tool_calls=False)


# def route_database_tools(state: AgentState) -> Literal[
#     "__end__", "main_agent", "search_database_tools"]:
#     route = tools_condition(state)
#     if route == "__end__":
#         return "__end__"
#     tool_calls = state["messages"][-1].tool_calls
#     if tool_calls:
#         tool_name = tool_calls[0]["name"]
#         if tool_name in search_database_tools:
#             return "search_database_tools"
#
#     raise ValueError("Invalid route")