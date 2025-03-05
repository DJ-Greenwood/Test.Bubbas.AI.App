from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_home, name='home'),
    path('calendar/add/', views.add_calendar, name='add_calendar'),
    path('calendar/<int:calendar_id>/edit/', views.edit_calendar, name='edit_calendar'),
    path('calendar/<int:calendar_id>/delete/', views.delete_calendar, name='delete_calendar'),
    path('preferences/update/', views.update_preferences, name='update_preferences'),
    
    # OAuth routes
    path('oauth/google/', views.google_oauth, name='google_oauth'),
    path('oauth/outlook/', views.outlook_oauth, name='outlook_oauth'),
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
]