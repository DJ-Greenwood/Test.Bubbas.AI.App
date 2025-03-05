from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import UserCalendar, UserPreference
from .forms import UserCalendarForm, UserPreferenceForm
from ErrorLog.services.error_logger import ErrorLogger

@login_required
def settings_home(request):
    """Main settings dashboard view"""
    try:
        # Get user's calendars and preferences
        calendars = UserCalendar.objects.filter(user=request.user, is_active=True)
        
        try:
            preferences = UserPreference.objects.get(user=request.user)
        except UserPreference.DoesNotExist:
            # Create preferences if they don't exist
            preferences = UserPreference.objects.create(user=request.user)
        
        # Initialize forms
        calendar_form = UserCalendarForm()
        preference_form = UserPreferenceForm(instance=preferences, user=request.user)
        
        return render(request, 'settings/settings_home.html', {
            'calendars': calendars,
            'preferences': preferences,
            'calendar_form': calendar_form,
            'preference_form': preference_form,
        })
    except Exception as e:
        ErrorLogger.log_error("settings", f"Error loading settings page: {str(e)}", request=request, user=request.user)
        messages.error(request, "There was an error loading your settings.")
        return redirect('home')

@login_required
def add_calendar(request):
    """Add a new calendar integration"""
    if request.method == 'POST':
        try:
            form = UserCalendarForm(request.POST)
            if form.is_valid():
                calendar = form.save(commit=False)
                calendar.user = request.user
                
                # If this is set as primary, clear other primary flags
                if calendar.is_primary:
                    UserCalendar.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
                
                calendar.save()
                
                # Set up OAuth flow based on calendar type
                # This is a placeholder that would be expanded with actual OAuth implementation
                if calendar.calendar_type == 'google':
                    return redirect('settings:google_oauth')
                elif calendar.calendar_type == 'outlook':
                    return redirect('settings:outlook_oauth')
                else:
                    messages.success(request, f"Added new {calendar.get_calendar_type_display()} calendar successfully.")
                    return redirect('settings:home')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        except Exception as e:
            ErrorLogger.log_error("settings", f"Error adding calendar: {str(e)}", request=request, user=request.user)
            messages.error(request, "There was an error adding your calendar.")
    
    return redirect('settings:home')

@login_required
def edit_calendar(request, calendar_id):
    """Edit an existing calendar integration"""
    calendar = get_object_or_404(UserCalendar, id=calendar_id, user=request.user)
    
    if request.method == 'POST':
        try:
            form = UserCalendarForm(request.POST, instance=calendar)
            if form.is_valid():
                calendar = form.save(commit=False)
                
                # If this is set as primary, clear other primary flags
                if calendar.is_primary:
                    UserCalendar.objects.filter(user=request.user, is_primary=True).exclude(id=calendar.id).update(is_primary=False)
                
                calendar.save()
                messages.success(request, f"Updated {calendar.calendar_name} successfully.")
                return redirect('settings:home')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        except Exception as e:
            ErrorLogger.log_error("settings", f"Error editing calendar: {str(e)}", request=request, user=request.user)
            messages.error(request, "There was an error updating your calendar.")
    else:
        form = UserCalendarForm(instance=calendar)
    
    return render(request, 'settings/edit_calendar.html', {
        'form': form,
        'calendar': calendar,
    })

@login_required
@require_POST
def delete_calendar(request, calendar_id):
    """Delete a calendar integration"""
    try:
        calendar = get_object_or_404(UserCalendar, id=calendar_id, user=request.user)
        
        # Check if this calendar is the default in preferences
        preferences = UserPreference.objects.get(user=request.user)
        if preferences.default_calendar == calendar:
            preferences.default_calendar = None
            preferences.save()
        
        # Delete the calendar
        calendar_name = calendar.calendar_name
        calendar.delete()
        
        messages.success(request, f"Removed {calendar_name} from your calendars.")
        return redirect('settings:home')
    except Exception as e:
        ErrorLogger.log_error("settings", f"Error deleting calendar: {str(e)}", request=request, user=request.user)
        messages.error(request, "There was an error removing your calendar.")
        return redirect('settings:home')

@login_required
def update_preferences(request):
    """Update user preferences"""
    if request.method == 'POST':
        try:
            preferences = UserPreference.objects.get(user=request.user)
            form = UserPreferenceForm(request.POST, instance=preferences, user=request.user)
            
            if form.is_valid():
                form.save()
                messages.success(request, "Your preferences have been updated.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
        except Exception as e:
            ErrorLogger.log_error("settings", f"Error updating preferences: {str(e)}", request=request, user=request.user)
            messages.error(request, "There was an error updating your preferences.")
    
    return redirect('settings:home')

# Placeholder views for OAuth flow - these would be expanded with actual OAuth implementation
@login_required
def google_oauth(request):
    """Handle Google Calendar OAuth flow"""
    # This is a placeholder for the actual OAuth implementation
    messages.info(request, "Google Calendar integration is not fully implemented yet.")
    return redirect('settings:home')

@login_required
def outlook_oauth(request):
    """Handle Microsoft Outlook OAuth flow"""
    # This is a placeholder for the actual OAuth implementation
    messages.info(request, "Microsoft Outlook integration is not fully implemented yet.")
    return redirect('settings:home')

@login_required
def oauth_callback(request):
    """Handle OAuth callback from calendar providers"""
    # This is a placeholder for the actual OAuth callback handling
    provider = request.GET.get('provider', '')
    code = request.GET.get('code', '')
    
    try:
        # Process OAuth callback based on provider
        if provider == 'google':
            # Process Google OAuth callback
            messages.success(request, "Successfully connected to Google Calendar.")
        elif provider == 'outlook':
            # Process Outlook OAuth callback
            messages.success(request, "Successfully connected to Microsoft Outlook.")
        else:
            messages.warning(request, f"Unknown calendar provider: {provider}")
    except Exception as e:
        ErrorLogger.log_error("oauth", f"Error in OAuth callback for {provider}: {str(e)}", request=request, user=request.user)
        messages.error(request, "There was an error connecting to your calendar.")
    
    return redirect('settings:home')