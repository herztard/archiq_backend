from typing import Dict, Any
from langchain.schema import AIMessage
from django.db.models import Q
from properties.models import Property
from agent.agent_state import AgentState


def query_real_estate_db(state: AgentState) -> Dict[str, Any]:
    search_criteria = state.get("search_criteria", {})
    
    try:
        query = Property.objects.all().select_related(
            'block', 'block__complex', 'block__complex__district'
        )
        
        query = query.exclude(
            property_purchases__status__in=['RESERVED', 'PAID', 'COMPLETED']
        )

        # Floor range filters
        if search_criteria.get("min_floor") is not None:
            q = query.filter(floor__gte=search_criteria["min_floor"])
            if not q.exists():
                search_criteria.pop("min_floor", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов выше этажа "
                    f"{search_criteria.get('min_floor')}"  
                    ". Уберите или измените этот критерий."
                ))]}
            query = q


        if search_criteria.get("max_floor") is not None:
            q = query.filter(floor__lte=search_criteria["max_floor"])
            if not q.exists():
                search_criteria.pop("max_floor", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов ниже этажа "
                    f"{search_criteria.get('max_floor')}"  
                    ". Уберите или измените этот критерий."
                ))]}
            query = q

        # Area range filters
        if search_criteria.get("min_area") is not None:
            q = query.filter(area__gte=search_criteria["min_area"])
            if not q.exists():
                search_criteria.pop("min_area", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов с площадью от "
                    f"{search_criteria.get('min_area')}"  
                    " кв.м. Уберите или измените этот критерий."
                ))]}
            query = q
            
        if search_criteria.get("max_area") is not None:
            q = query.filter(area__lte=search_criteria["max_area"])
            if not q.exists():
                search_criteria.pop("max_area", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов с площадью до "
                    f"{search_criteria.get('max_area')}"  
                    " кв.м. Уберите или измените этот критерий."
                ))]}
            query = q

        # Room count filters
        if search_criteria.get("min_rooms") is not None:
            q = query.filter(rooms__gte=search_criteria["min_rooms"])
            if not q.exists():
                search_criteria.pop("min_rooms", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов с минимумом "
                    f"{search_criteria.get('min_rooms')}"  
                    " комнат. Уберите или измените этот критерий."
                ))]}
            query = q
            
        if search_criteria.get("max_rooms") is not None:
            q = query.filter(rooms__lte=search_criteria["max_rooms"])
            if not q.exists():
                search_criteria.pop("max_rooms", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов с максимумом "
                    f"{search_criteria.get('max_rooms')}"  
                    " комнат. Уберите или измените этот критерий."
                ))]}
            query = q

        # Price range filters
        if search_criteria.get("min_price") is not None:
            q = query.filter(price__gte=search_criteria["min_price"])
            if not q.exists():
                search_criteria.pop("min_price", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов с ценой от "
                    f"{search_criteria.get('min_price')}"  
                    " тг. Уберите или измените этот критерий."
                ))]}
            query = q
            
        if search_criteria.get("max_price") is not None:
            q = query.filter(price__lte=search_criteria["max_price"])
            if not q.exists():
                search_criteria.pop("max_price", None)
                state["search_criteria"] = search_criteria
                return {"messages": [AIMessage(content=(
                    "Извините, не найдено объектов с ценой до "
                    f"{search_criteria.get('max_price')}" 
                    " тг. Уберите или измените этот критерий."
                ))]}
            query = q

        # Final result compilation
        total = query.count()
        if total == 0:
            messages_content = "Извините, по вашим критериям объекты не найдены."
        else:
            limit = 5 if total > 5 else total
            results = query[:limit]
            lines = []
            for prop in results:
                lines.append(
                    f"property_id: {prop.id}. Адрес: {prop.block.complex.address}, ЖК: {prop.block.complex.name}, "
                    f"Район: {prop.block.complex.district.name}\n"
                    f"Цена: {prop.price}\n"
                    f"Цена за квадратный метр: {prop.price_per_sqm}\n"
                    f"Комнат: {prop.rooms}\n"
                    f"Площадь метр квадрат: {prop.area}\n"
                    f"Этаж квартиры: {prop.floor}\n"
                    f"Вид отопления: {prop.block.complex.heating_type}\n"
                    f"Пассажирский лифт: {"Имеется" if prop.block.complex.has_elevator_pass else "Отсутствует"}\n"
                    f"Грузовой лифт: {"Имеется" if prop.block.complex.has_elevator_cargo else "Отсутствует"}\n"
                    f"Срок сдачи: {prop.block.deadline_year} года, {prop.block.deadline_querter} квартал\n"
                    f"Статус строительства: {prop.block.building_status}\n"
                    f"Очередь: {prop.block.queue if prop.block.queue else "Отсутствует информация"}\n"
                )
            messages_content = "Найденные объекты недвижимости:\n" + "\n".join(lines)
            if total > limit:
                messages_content += f"\nИтого найдено: {total} объектов. Добавьте новые критерии, чтобы сузить поиск."

    except Exception as e:
        messages_content = f"Произошла ошибка при поиске объектов: {str(e)}"

    return {"messages": [AIMessage(content=messages_content)]}
