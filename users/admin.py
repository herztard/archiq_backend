from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, OneTimePassword


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("id", "phone_number", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("id", "phone_number", "first_name", "last_name")
    ordering = ("phone_number",)


admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(OneTimePassword)
class OtpAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'code', 'created_at')
