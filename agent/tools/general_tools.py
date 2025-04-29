from pydantic import BaseModel, Field


class ToSearchCriteriaAgent(BaseModel):
    """Передает работу специализированному агенту по поиску недвижимости и сбору критериев поиска. Вызывай этот инструмент ВСЕГДА, когда юзер даёт хоть один критерий."""

    request: str = Field(
        description="Any additional information or requests from the user regarding their search criteria."
    )

class ToSearchDescriptiveDataAgent(BaseModel):
    """Передает работу специализированному агенту по поиску в базе данных ответов, на вопросы касающиеся справочного характера о жилых комплексах, районах, средней стоимости и так далее."""

    request: str = Field(
        description="Any additional information or requests from the user regarding questions of a reference nature."
    )


class CompleteOrEscalate(BaseModel):
    """Инструмент, позволяющий отметить текущую задачу как выполненную и/или передать управление
    диалогом главному помощнику, который может перенаправить диалог в зависимости от потребностей пользователя."""

    cancel: bool = True
    reason: str

    class Config:
        schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            }
        }