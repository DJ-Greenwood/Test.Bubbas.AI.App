# Add this to your chatbot/admin.py file

from django.contrib import admin
from .models import ErrorLogger

@admin.register(ErrorLogger)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'error_type', 'user', 'short_message', 'url', 'created_at', 'resolved')
    list_filter = ('error_type', 'resolved', 'created_at')
    search_fields = ('error_message', 'stack_trace', 'url', 'user__username', 'user__email')
    readonly_fields = ('error_type', 'user', 'error_message', 'stack_trace', 'url', 'method', 
                      'ip_address', 'user_agent', 'created_at')
    
    fieldsets = (
        ('Error Information', {
            'fields': ('error_type', 'error_message', 'stack_trace', 'created_at')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Request Information', {
            'fields': ('url', 'method')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolution_notes')
        }),
    )
    
    def short_message(self, obj):
        if obj.error_message:
            return obj.error_message[:50] + ('...' if len(obj.error_message) > 50 else '')
        return '-'
    short_message.short_description = 'Error Message'
    
    def has_add_permission(self, request):
        return False  # Prevent adding error logs manually