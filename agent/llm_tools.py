from properties.models import ResidentialComplex, Block, Property
from sales.models import PropertyPurchase
from location.models import District
from .vector_searcher import VectorSearcher
import ast


class MainAgentTools:

    @staticmethod
    def search_for_all_residential_complexes() -> str:
        """
        Ищет все жилые комплексы в базе данных и возвращает список с информацией о жилых комплексах
        и количеством доступных квартир в продаже рядом с ними.
        """

        try:
            residential_complexes = ResidentialComplex.objects.all()
            if not residential_complexes:
                return "Нет доступных жилых комплексов."

            details = []
            for residential_complex in residential_complexes:
                blocks = Block.objects.filter(complex=residential_complex)
                
                available_blocks = []
                total_available_apartments = 0
                
                for block in blocks:
                    apartments_in_block = Property.objects.filter(
                        block=block,
                        category="APARTMENT",
                        price__isnull=False
                    ).exclude(
                        property_purchases__status__in=["PAID", "RESERVED", "COMPLETED"]
                    ).count()
                    
                    if apartments_in_block > 0:
                        available_blocks.append({
                            "block_number": block.block_number,
                            "available_apartments": apartments_in_block
                        })
                        total_available_apartments += apartments_in_block

                details.append({
                    "name": residential_complex.name,
                    "district": residential_complex.district.name if residential_complex.district else "Не указан",
                    "address": residential_complex.address,
                    "class_type": residential_complex.class_type,
                    "construction_technology": residential_complex.construction_technology,
                    "heating_type": residential_complex.heating_type,
                    "ceiling_height": str(residential_complex.ceiling_height),
                    "down_payment": str(residential_complex.down_payment) if residential_complex.down_payment else "Не указан",
                    "installment_plan": residential_complex.installment_plan or "Не указан",
                    "description_short": residential_complex.description_short or "",
                    "location": {
                        "link_on_map": residential_complex.link_on_map or None,
                    },
                    "total_available_apartments": total_available_apartments,
                    "available_blocks": available_blocks
                })

            return f"Список всех жилых комплексов: {details}"

        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске жилых комплексов."

    @staticmethod
    def search_districts() -> str:
        """
        Ищет доступные районы в нашей БД.
        """
        try:
            districts = District.objects.all().order_by('id')
            if not districts:
                return "Нет доступных районов."

            details = []
            for district in districts:
                complexes = ResidentialComplex.objects.filter(district=district)
                details.append({
                    "name": district.name,
                    "city": district.city.name,
                    "residential_complexes": complexes.count()
                })

            return f"Список всех районов: {details}"
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске районов."

    @staticmethod
    def search_specific_districts(district_name: str) -> str:
        """
        Ищет информацию по конкретному району по его названию.
        В базе данных названия районов начинаются с заглавной буквы.
        """
        try:
            district = District.objects.filter(name=district_name).first()
            if not district:
                return "Район не найден."

            complexes = ResidentialComplex.objects.filter(district=district)
            available_apartments = Property.objects.filter(
                block__complex__district=district,
                category="APARTMENT",
                price__isnull=False
            ).exclude(
                property_purchases__status__in=["PAID", "RESERVED", "COMPLETED"]
            ).count()

            details = {
                "name": district.name,
                "city": district.city.name,
                "description": district.description or "Описание отсутствует",
                "total_complexes": complexes.count(),
                "available_apartments": available_apartments
            }

            return f"Информация о районе: {details}"
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске района."

    @staticmethod
    def search_for_residential_complex_description(complex_name: str) -> str:
        """Ищет описание жилого комплекса (ЖК) по названию"""
        try:
            raw_vector_res = VectorSearcher(collection_name="residential_complexes_names", top_k=3).search_vector(complex_name)

            if not raw_vector_res:
                return f"Нет данных о жилом комплексе {complex_name} в векторном хранилище."

            print("raw_vector_res:", raw_vector_res.response)

            resp_ids = ast.literal_eval(raw_vector_res.response)
            residential_complex = ResidentialComplex.objects.filter(id__in=resp_ids).first()
            if not residential_complex:
                return f"Нет данных о жилом комплексе {complex_name}."

            return f"Описание жилого комплекса {complex_name}: {residential_complex.description_full or residential_complex.description_short}."
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске описания жилого комплекса."

    @staticmethod
    def search_for_res_complex_address(complex_name: str) -> str:
        """Ищет адрес жилого комплекса (ЖК) по названию"""
        try:
            raw_vector_res = VectorSearcher(collection_name="residential_complexes_names", top_k=3).search_vector(complex_name)

            if not raw_vector_res:
                return f"Нет данных о жилом комплексе {complex_name} в векторном хранилище."
            print("raw_vector_res:", raw_vector_res.response)

            resp_ids = ast.literal_eval(raw_vector_res.response)
            residential_complex = ResidentialComplex.objects.filter(id__in=resp_ids).first()
            if not residential_complex:
                return f"Нет данных о жилом комплексе {complex_name}."

            return f"Адрес жилого комплекса {complex_name}: {residential_complex.address}. Ссылка на 2GIS - {residential_complex.link_on_map}."
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске адреса жилого комплекса."

    @staticmethod
    def search_for_res_complex_constr_tech(complex_name: str) -> str:
        """Ищет о системе строительства жилого комплекса (ЖК) по названию"""
        try:
            raw_vector_res = VectorSearcher(collection_name="residential_complexes_names", top_k=3).search_vector(complex_name)

            if not raw_vector_res:
                return f"Нет данных о жилом комплексе {complex_name} в векторном хранилище."
            print("raw_vector_res:", raw_vector_res.response)

            resp_ids = ast.literal_eval(raw_vector_res.response)
            residential_complex = ResidentialComplex.objects.filter(id__in=resp_ids).first()
            if not residential_complex:
                return f"Нет данных о жилом комплексе {complex_name}."

            return f"Система строительства жилого комплекса {complex_name}: {residential_complex.construction_technology}."
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске информации о системе строительства."

    @staticmethod
    def search_for_res_complex_ceiling_height(complex_name: str) -> str:
        """Ищет о высоте потолках жилого комплекса (ЖК) по названию"""
        try:
            raw_vector_res = VectorSearcher(collection_name="residential_complexes_names", top_k=3).search_vector(complex_name)

            if not raw_vector_res:
                return f"Нет данных о жилом комплексе {complex_name} в векторном хранилище."
            print("raw_vector_res:", raw_vector_res.response)

            resp_ids = ast.literal_eval(raw_vector_res.response)
            residential_complex = ResidentialComplex.objects.filter(id__in=resp_ids).first()
            if not residential_complex:
                return f"Нет данных о жилом комплексе {complex_name}."

            return f"Высота потолков жилого комплекса {complex_name}: {residential_complex.ceiling_height}."
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске информации о высоте потолков."

    @staticmethod
    def search_for_res_complex_link_on_map(complex_name: str) -> str:
        """Ищет ссылку на карте жилого комплекса (ЖК) по названию"""
        try:
            raw_vector_res = VectorSearcher(collection_name="residential_complexes_names", top_k=3).search_vector(complex_name)

            if not raw_vector_res:
                return f"Нет данных о жилом комплексе {complex_name} в векторном хранилище."
            print("raw_vector_res:", raw_vector_res.response)

            resp_ids = ast.literal_eval(raw_vector_res.response)
            residential_complex = ResidentialComplex.objects.filter(id__in=resp_ids).first()
            if not residential_complex:
                return f"Нет данных о жилом комплексе {complex_name}."

            return f"Ссылка на карте жилого комплекса {complex_name}: {residential_complex.link_on_map}."
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске ссылки на карте."

    @staticmethod
    def search_for_res_complex_probs(complex_name: str) -> str:
        """Ищет квартиры в ЖК по названию Жилого Комплекса"""
        try:
            raw_vector_res = VectorSearcher(collection_name="residential_complexes_names", top_k=3).search_vector(complex_name)

            if not raw_vector_res:
                return f"Нет данных о жилом комплексе {complex_name} в векторном хранилище."
            print("raw_vector_res:", raw_vector_res.response)

            resp_ids = ast.literal_eval(raw_vector_res.response)
            properties = Property.objects.filter(
                block__complex_id__in=resp_ids,
                category="APARTMENT",
                price__isnull=False
            ).exclude(
                property_purchases__status__in=["PAID", "RESERVED", "COMPLETED"]
            ).select_related('block', 'block__complex', 'block__complex__district')

            if not properties:
                return "Нет доступных квартир."

            details = []
            for prop in properties:
                block = prop.block
                complex_obj = block.complex
                detail = (
                    f"Номер: {prop.number}\n"
                    f"Жилой комплекс: {complex_obj.name}\n"
                    f"Адрес: {complex_obj.address}\n"
                    f"Район: {complex_obj.district.name}\n"
                    f"Цена: {prop.price}\n"
                    f"Цена за квадратный метр: {prop.price_per_sqm}\n"
                    f"Комнат: {prop.rooms}\n"
                    f"Площадь: {prop.area} м²\n"
                    f"Этаж квартиры: {prop.floor}\n"
                    f"Вид отопления: {complex_obj.heating_type}\n"
                    f"Пассажирский лифт: {complex_obj.has_elevator_pass}\n"
                    f"Грузовой лифт: {complex_obj.has_elevator_cargo}\n"
                    f"Срок сдачи: {block.deadline_year} года, {block.deadline_querter} квартал\n"
                    f"Статус строительства: {block.building_status}\n"
                    f"Очередь: {block.queue}\n"
                )

                details.append(detail)
            details_str = "; ".join(details)
            return f"Найдены квартиры в ЖК {complex_name}: {details_str}"
        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске квартир." 