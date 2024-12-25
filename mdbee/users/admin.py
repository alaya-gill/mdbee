from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth.models import Permission
admin.site.register(Permission)


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    # form = UserChangeForm
    # add_form = UserCreationForm
    # fieldsets = (("User", {"fields": ("name",)}),) + auth_admin.UserAdmin.fieldsets
    fieldsets = (
        (None, {'fields': ('email','first_name', 'last_name', 'address', 'city', 'state',  'phone', 'is_superuser')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email','password1', 'password2', 'first_name', 'last_name', 'address', 'city', 'state',  'phone', 'is_superuser')
            }
        ),
    )
    list_display = ('email',  'is_staff', 'is_superuser', 'last_login')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    
    def save_model(self, request, obj, form, change):
        # Automatically set username to email if not provided
        if not obj.username:
            obj.username = obj.email
        obj.is_staff = True
        super().save_model(request, obj, form, change)
