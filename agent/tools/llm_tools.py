import ast
import requests
from icecream import ic
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from sqlalchemy.orm import Session
from sqlalchemy import asc

class MainAgentTools:

    ##############################
    ###       PROPERTIES       ###
    ##############################

    @staticmethod
    def search_districts() -> str:
        """Ищет доступные районы в нашей БД."""
        try:
            return "SOMETHING"
        except Exception as e:
            print(e)
        finally:
            pass