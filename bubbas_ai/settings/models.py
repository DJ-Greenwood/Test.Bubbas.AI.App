from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserCalendar(models.Model):
    """Model to store user calendar integration details"""
    CALENDAR_TYPES = (
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook'),
        ('apple', 'Apple iCalendar'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendars')
    calendar_type = models.CharField(max_length=20, choices=CALENDAR_TYPES)
    calendar_id = models.CharField(max_length=255, blank=True, null=True)
    calendar_name = models.CharField(max_length=100)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', 'calendar_name']
        unique_together = ['user', 'calendar_id', 'calendar_type']
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_calendar_type_display()} - {self.calendar_name}"

class UserPreference(models.Model):
    """Model to store general user preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    default_calendar = models.ForeignKey(UserCalendar, on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name='default_for')
    enable_calendar_suggestions = models.BooleanField(default=True)
    reminder_time_minutes = models.IntegerField(default=30)
    timezone = models.CharField(max_length=50, default='America/Chicago')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create a UserPreference record when a new User is created"""
    if created:
        UserPreference.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    """Update the UserPreference when the User is updated"""
    instance.preferences.save()
    