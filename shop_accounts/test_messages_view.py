from django.shortcuts import render, redirect
from django.contrib import messages

def test_messages(request):
    """View to test different message types"""
    
    # Add test messages
    messages.debug(request, "This is a debug message (styled as secondary)")
    messages.info(request, "This is an info message with important information")
    messages.success(request, "This is a success message indicating an operation completed successfully")
    messages.warning(request, "This is a warning message alerting you about something important")
    messages.error(request, "This is an error message indicating something went wrong")
    
    # Redirect to home page to display the messages
    return redirect('home')