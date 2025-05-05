from properties.models import ResidentialComplex, Block, Property
from sales.models import PropertyPurchase


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
                
                # To store info about blocks with available apartments
                available_blocks = []
                total_available_apartments = 0
                
                for block in blocks:
                    # Count available apartments in this block
                    apartments_in_block = Property.objects.filter(
                        block=block,
                        category="APARTMENT",
                        price__isnull=False
                    ).exclude(
                        property_purchases__status__in=["PAID", "RESERVED", "COMPLETED"]
                    ).count()
                    
                    # If block has available apartments, add it to the list
                    if apartments_in_block > 0:
                        available_blocks.append({
                            "block_number": block.block_number,
                            "available_apartments": apartments_in_block
                        })
                        total_available_apartments += apartments_in_block

                details.append({
                    "name": residential_complex.name,
                    "total_available_apartments": total_available_apartments,
                    "available_blocks": available_blocks
                })

            return f"Список всех жилых комплексов: {details}"

        except Exception as e:
            print(e)
            return "Произошла ошибка при поиске жилых комплексов." 