from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User, ContactMessage


def login_view(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('shop_orders:order_history')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')


def register(request):
    """
    User registration view
    """
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        country = request.POST.get('country')
        
        # Basic validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            country=country
        )
        
        messages.success(request, 'Your account has been created successfully. You can now log in.')
        return redirect('shop_accounts:login')
    
    # Check if there's a referral parameter
    sponsor_username = request.GET.get('ref', '')
    
    context = {
        'sponsor': sponsor_username
    } if sponsor_username else {}
    
    return render(request, 'accounts/register.html', context)


@login_required
def profile(request):
    """
    User profile view
    """
    return render(request, 'accounts/profile.html')


@login_required
def edit_profile(request):
    """
    Edit user profile view
    """
    if request.method == 'POST':
        # Update user profile
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.country = request.POST.get('country', user.country)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('shop_accounts:profile')
    
    return render(request, 'accounts/edit_profile.html')




def about(request):
    """
    About page view
    """
    return render(request, 'accounts/about.html')


def contact(request):
    """
    Contact page view
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Always save the contact message to the database first
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Create email content for admin notification
        admin_email_subject = f"ShopEarn Contact Form: {subject}"
        
        # Create HTML email content for admin
        admin_html_message = render_to_string('emails/contact_email.html', {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
        })
        
        # Create plain text version for admin
        admin_plain_message = strip_tags(admin_html_message)
        
        # Create confirmation email for user
        user_email_subject = "Thank you for contacting ShopEarn"
        
        # Create HTML email content for user
        user_html_message = render_to_string('emails/contact_confirmation.html', {
            'name': name,
            'subject': subject,
            'message': message,
        })
        
        # Create plain text version for user
        user_plain_message = strip_tags(user_html_message)
        
        # Send emails
        email_sent = False
        try:
            # Send notification to admin
            send_mail(
                admin_email_subject,
                admin_plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],  # Use the email from settings
                html_message=admin_html_message,
                fail_silently=True,  # Use True in production to prevent exceptions
            )
            
            # Send confirmation to user
            send_mail(
                user_email_subject,
                user_plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],  # Send to the user who submitted the form
                html_message=user_html_message,
                fail_silently=True,  # Use True in production to prevent exceptions
            )
            
            email_sent = True
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
        except BadHeaderError:
            messages.error(request, 'Invalid header found. Please try again.')
        except Exception as e:
            # Even with fail_silently=True, catch any other exceptions just in case
            # But still show a success message since we saved to the database
            messages.success(request, 'Your message has been received. Thank you for contacting us!')
            print(f"Email error: {str(e)}")  # Log the error
        
        return redirect('shop_accounts:contact')
    
    return render(request, 'accounts/contact.html')


