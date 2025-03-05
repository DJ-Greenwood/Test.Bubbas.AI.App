from django import forms
from .models import UserCalendar, UserPreference

class UserCalendarForm(forms.ModelForm):
    """Form for adding/editing calendar integration"""
    class Meta:
        model = UserCalendar
        fields = ['calendar_type', 'calendar_name', 'is_primary']
        widgets = {
            'calendar_type': forms.Select(attrs={'class': 'form-control'}),
            'calendar_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'My Calendar'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserPreferenceForm(forms.ModelForm):
    """Form for user preferences"""
    class Meta:
        model = UserPreference
        fields = ['default_calendar', 'enable_calendar_suggestions', 'reminder_time_minutes', 'timezone']
        widgets = {
            'default_calendar': forms.Select(attrs={'class': 'form-control'}),
            'enable_calendar_suggestions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reminder_time_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 1440}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserPreferenceForm, self).__init__(*args, **kwargs)
        
        if user:
            # Limit default_calendar choices to this user's calendars
            self.fields['default_calendar'].queryset = UserCalendar.objects.filter(user=user, is_active=True)
            
            # Timezone choices (simplified - you might want to use pytz for a complete list)
            TIMEZONE_CHOICES = [
                ('America/New_York', 'Eastern Time (US & Canada)'),
                ('America/Chicago', 'Central Time (US & Canada)'),
                ('America/Denver', 'Mountain Time (US & Canada)'),
                ('America/Los_Angeles', 'Pacific Time (US & Canada)'),
                ('America/Anchorage', 'Alaska'),
                ('Pacific/Honolulu', 'Hawaii'),
                ('UTC', 'UTC'),
            ]
            self.fields['timezone'].widget = forms.Select(choices=TIMEZONE_CHOICES, attrs={'class': 'form-control'})