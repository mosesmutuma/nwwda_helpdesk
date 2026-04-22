from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

# --- CUSTOM REDIRECT FOR ADMIN LOGOUT ---
def admin_logout_redirect(request):
    from django.contrib.auth import logout
    logout(request)
    # Redirects Admin back to the Admin Login screen with the 'next' parameter
    # This ensures the subsequent login stays in the admin dashboard
    return redirect('/admin/login/?next=/admin/')

# Hijack the Admin Site's logout function directly
admin.site.logout = admin_logout_redirect

urlpatterns = [
    # 1. ADMIN PASSWORD RESET
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url='/admin/login/?next=/admin/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # 2. ADMIN URLS
    # FIX: Point explicitly to Jazzmin's login template to avoid the 500 error
    path('admin/login/', auth_views.LoginView.as_view(
        template_name='admin/login.html',
        extra_context={'next': '/admin/'}
    )),
    path('admin/', admin.site.urls),
    
    # 3. APP URLS
    path('', include('tickets.urls')),
    
    # 4. STAFF LOGIN
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # Handles the default redirect error
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html')),
    
    # 5. STAFF LOGOUT
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]