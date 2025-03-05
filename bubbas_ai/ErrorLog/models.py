# Create a new file: chatbot/services/error_logger.py
import traceback
import logging
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class ErrorLog(models.Model):
    error_type = models.CharField(max_length=255)
    error_message = models.TextField()
    stack_trace = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    url = models.CharField(max_length=2000, null=True, blank=True)
    method = models.CharField(max_length=10, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.error_type}: {self.error_message[:50]}"

class ErrorLogger:
    @staticmethod
    def log_error(error_type, error_message, request=None, user=None, stack_trace=None, extra_data=None):
        """
        Log an error to both the database and the logging system.
        
        Args:
            error_type: Type of error (auth, chat, api, etc.)
            error_message: Human-readable error message
            request: Django request object (optional)
            user: User object (optional)
            stack_trace: Stack trace string (optional)
            extra_data: Any additional data to log (optional)
        """
        try:
            # Get stack trace if not provided
            if stack_trace is None:
                stack_trace = traceback.format_exc()
            
            # Create error log entry
            error_log = ErrorLog(
                error_type=error_type,
                error_message=str(error_message),
                stack_trace=stack_trace if stack_trace != 'None\n' else None,
            )
            
            # Add user if available
            if user:
                error_log.user = user
            elif request and request.user.is_authenticated:
                error_log.user = request.user
            
            # Add request info if available
            if request:
                error_log.url = request.path
                error_log.method = request.method
                error_log.ip_address = ErrorLogger._get_client_ip(request)
                error_log.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            error_log.save()
            
            # Also log to Django's logging system
            logger.error(
                f"{error_type} Error: {error_message}\n"
                f"URL: {error_log.url}\n"
                f"User: {error_log.user}\n"
                f"IP: {error_log.ip_address}\n"
                f"{stack_trace if stack_trace != 'None\n' else ''}"
            )
            
            return error_log
            
        except Exception as e:
            # If error logging fails, fall back to standard logging
            logger.error(f"Error logging failed: {str(e)}")
            logger.error(f"Original error: {error_type} - {error_message}")
            return None
    
    @staticmethod
    def _get_client_ip(request):
        """Extract the client IP address from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip