from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from ErrorLog.services.error_logger import ErrorLogger

def register_view(request):
    """View for user registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Bubbas.ai, {user.username}!")
            return redirect('chatbot:chat')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                    ErrorLogger.log_error(f"Registration error in field {field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """View for user login"""
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                return redirect('chatbot:chat')
            else:
                messages.error(request, "Invalid username or password.")
                ErrorLogger.log_error("Invalid username or password during login.")
        else:
            messages.error(request, "Invalid username or password.")
            ErrorLogger.log_error("Invalid login form submission.")
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """View to handle user logout"""
    logout(request)
    messages.info(request, "You've been successfully logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    """View for user profile"""
    return render(request, 'accounts/profile.html')