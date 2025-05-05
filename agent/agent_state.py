from typing import Annotated, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import TypedDict

class SearchCriteria(TypedDict):
    district: Optional[str]
    residential_complex: Optional[str]
    class_type: Optional[str]


    min_floor: Optional[int]
    max_floor: Optional[int]

    min_area: Optional[float]
    max_area: Optional[float]

    min_price: Optional[float]
    max_price: Optional[float]

    min_rooms: Optional[int]
    max_rooms: Optional[int]


def update_search_criteria(current: SearchCriteria, new: SearchCriteria) -> SearchCriteria:
    result = current.copy()

    complex_in_new = "residential_complex" in new
    district_in_new = "district" in new

    if complex_in_new and district_in_new:
        result["residential_complex"] = new["residential_complex"]
        result["district"] = new["district"]
    elif complex_in_new:
        result["residential_complex"] = new["residential_complex"]
        result.pop("district", None)
    elif district_in_new:
        result["district"] = new["district"]
        result.pop("residential_complex", None)

    other_keys = [
        "class_type",
        "min_floor", "max_floor",
        "min_area", "max_area",
        "min_price", "max_price",
        "min_rooms", "max_rooms",
    ]

    for key in other_keys:
        if key in new:
            result[key] = new[key]

    return result

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    search_criteria: Annotated[SearchCriteria, update_search_criteria]
    last_updated_keys: list[str]
    thread_id: str
