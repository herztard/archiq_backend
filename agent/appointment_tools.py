from typing import Optional
from django.contrib.auth import get_user_model
from applications.models import Application
from properties.models import Property, ResidentialComplex

User = get_user_model()

class AppointmentTools:
    @staticmethod
    def create_property_application(
        name: str,
        phone_number: str,
        property_id: Optional[int] = None,
        complex_id: Optional[int] = None,
    ) -> str:
        """
        Create a new application for a property or residential complex.
        
        Args:
            name: The full name of the applicant
            phone_number: Phone number in format +7XXXXXXXXXX
            property_id: ID of a specific property (optional)
            complex_id: ID of a residential complex (optional)
        
        Returns:
            str: Confirmation message about the application submission
        """
        try:
            if not name or not phone_number:
                return "Для создания заявки необходимы имя и номер телефона."
            
            if not phone_number.startswith('+'):
                phone_number = f"+{phone_number}"
                
            if not (property_id or complex_id):
                return "Для создания заявки необходимо указать ID квартиры или жилого комплекса."
            
            property_obj = None
            complex_obj = None
            
            if property_id:
                try:
                    property_obj = Property.objects.get(id=property_id)
                except Property.DoesNotExist:
                    return f"Недвижимость с ID {property_id} не найдена."
            
            if complex_id:
                try:
                    complex_obj = ResidentialComplex.objects.get(id=complex_id)
                except ResidentialComplex.DoesNotExist:
                    return f"Жилой комплекс с ID {complex_id} не найден."
            
            user = None
            try:
                user = User.objects.filter(phone_number=phone_number).first()
            except Exception as e:
                print(e)
                pass
            
            application = Application.objects.create(
                name=name,
                phone_number=phone_number,
                property=property_obj,
                residential_complex=complex_obj,
                status='NEW',
                user=user
            )

            user_info = f" и привязана к вашему аккаунту" if user else ""
            
            return (
                f"Заявка №{application.id} успешно создана{user_info}. "
                f"Наш менеджер свяжется с вами по номеру {phone_number} "
                f"в ближайшее время."
            )
            
        except Exception as e:
            return f"Произошла ошибка при создании заявки: {str(e)}"

