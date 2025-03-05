from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'last_activity')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at', 'last_activity')
    readonly_fields = ('created_at', 'last_activity')