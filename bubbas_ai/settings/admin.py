from django.contrib import admin
from .models import UserCalendar, UserPreference

@admin.register(UserCalendar)
class UserCalendarAdmin(admin.ModelAdmin):
    list_display = ('user', 'calendar_type', 'calendar_name', 'is_primary', 'is_active', 'created_at')
    list_filter = ('calendar_type', 'is_primary', 'is_active', 'created_at')
    search_fields = ('user__username', 'calendar_name', 'calendar_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Calendar Details', {
            'fields': ('calendar_type', 'calendar_id', 'calendar_name')
        }),
        ('Settings', {
            'fields': ('is_primary', 'is_active')
        }),
        ('Authentication', {
            'fields': ('access_token', 'refresh_token', 'token_expiry'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'default_calendar', 'enable_calendar_suggestions', 'timezone', 'updated_at')
    list_filter = ('enable_calendar_suggestions', 'timezone')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Calendar Preferences', {
            'fields': ('default_calendar', 'enable_calendar_suggestions', 'reminder_time_minutes')
        }),
        ('Regional Settings', {
            'fields': ('timezone',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )