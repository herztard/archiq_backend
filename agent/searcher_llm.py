from llama_index.llms.openai import OpenAI

from archiq_backend import settings

from llama_index.core import Settings

class SearcherLLM:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearcherLLM, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return


        self.llm = OpenAI(
            temperature=0.0,
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY
        )

        self.llm.system_prompt = "Найди документ, где значение поля 'text' семантически совпадает с запросом. Верни ID документов в формате списка, например, [1, 2, 3]."
        Settings.llm = self.llm
        self.initialized = True

    @classmethod
    def get_llm(cls):
        instance = cls()
        return instance.llm
