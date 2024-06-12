from django.contrib import admin
from .models import User, SpotifyToken
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.


class UserAdmin(BaseUserAdmin):
    list_display = ('spotify_id', 'spotify_display_name', 'spotify_email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('spotify_id', 'password')}),
        ('Personal info', {'fields': ('spotify_display_name', 'spotify_email')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('spotify_id', 'spotify_display_name', 'spotify_email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('spotify_id',)
    ordering = ('spotify_id',)
    filter_horizontal = ()

    def save_model(self, request, obj, form, change):
        obj.save()


class SpotifyTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token', 'refresh_token', 'expires_in')
    search_fields = ('user__spotify_id', 'access_token', 'refresh_token', 'expires_in')
    list_filter = ('expires_in',)


admin.site.register(SpotifyToken, SpotifyTokenAdmin)
admin.site.register(User, UserAdmin)
