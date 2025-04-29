# app/services/tools_manager.py
from agent.tools.llm_tools import MainAgentTools
import inspect


def get_main_tools_list() -> list:
    functions = inspect.getmembers(MainAgentTools, predicate=inspect.isfunction)
    functions_list = [func for name, func in functions if not name.startswith('__')]
    return functions_list

def get_database_tools_list() -> list:
    functions = inspect.getmembers(MainAgentTools, predicate=inspect.isfunction)
    functions_list = [func for name, func in functions if not name.startswith('__')]
    return functions_list