from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Ticket, Announcement, Profile, Feedback

# --- 1. USER & PROFILE INTEGRATION ---

class CustomUserChangeForm(UserChangeForm):
    # We override the password field representation completely with a hidden widget
    password = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False,
        label="Password Management"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We replace the text description block to render a clean, beautifully styled button link
        if 'password' in self.fields:
            self.fields['password'].help_text = mark_safe(
                '<div style="margin-top: -10px; padding: 5px 0;">'
                '   <a href="../password/" class="button" style="background: #10b981; '
                '   color: #fff; padding: 8px 16px; border-radius: 6px; font-weight: 600; '
                '   display: inline-block; text-decoration: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"> '
                '   Change / Reset Password</a>'
                '   <p style="margin-top: 10px; color: var(--body-quiet-fg, #888); font-size: 0.85rem;">'
                '   Raw passwords are securely hashed. There is no way to view the plain text password.</p>'
                '</div>'
            )

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    
    # We display the department in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_department')

    def get_department(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.department
        return "No Profile"
    
    get_department.short_description = 'Department'

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Department Information'

# Ensure the profile inline is correctly linked
UserAdmin.inlines = (ProfileInline,)

# Unregister the default and register our version safely
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, UserAdmin)

# --- 2. TICKET MANAGEMENT ---
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_by', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    list_display_links = ('title',)

    # Removes the "ADD TICKET" button from the admin portal
    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj: return ('title', 'description', 'created_by', 'created_at')
        return ('created_at',)

    fieldsets = (
        ("Ticket Details", {'fields': ('title', 'description', 'created_by')}),
        ("Management", {'fields': ('status', 'priority')}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        super().save_model(request, obj, form, change)

# --- 3. ANNOUNCEMENTS ---
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('display_full_message', 'created_at')
    ordering = ('-created_at',)
    def display_full_message(self, obj): return obj.full_announcement
    display_full_message.short_description = 'Announcement Content'

# --- 4. STAFF SYSTEM FEEDBACK (THEME COMPATIBLE) ---
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('get_user_display', 'get_stars', 'short_description', 'formatted_date')
    list_filter = ('rating', 'created_at')
    search_fields = ('description', 'user__username')
    list_per_page = 20

    # Removes the "ADD FEEDBACK" button from the admin portal
    def has_add_permission(self, request):
        return False

    # Custom Column: Pill badges for star ratings (keeps black text inside bright badges)
    @admin.display(ordering='rating', description='Staff Rating')
    def get_stars(self, obj):
        badge_styles = {
            1: ("#fef2f2", "#dc2626", "⭐"),              # Critical Red
            2: ("#fff7ed", "#ea580c", "⭐⭐"),            # Orange
            3: ("#fefce8", "#ca8a04", "⭐⭐⭐"),          # Warm Yellow
            4: ("#f0fdf4", "#16a34a", "⭐⭐⭐⭐"),        # Soft Green
            5: ("#ecfeff", "#0891b2", "⭐⭐⭐⭐⭐")       # Vibrant Cyan
        }
        bg, text_color, stars = badge_styles.get(obj.rating, ("#f1f5f9", "#64748b", "No Rating"))
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 10px; '
            'border-radius: 20px; font-weight: 700; font-size: 0.85rem; '
            'display: inline-block; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">{}</span>',
            bg, text_color, stars
        )

    # Custom Column: Highlighted user link tags matching dark/light background dynamics
    @admin.display(ordering='user', description='Submitted By')
    def get_user_display(self, obj):
        if obj.user:
            return format_html(
                '<strong style="color: var(--link-fg, #3b82f6);"><i class="bi bi-person-fill"></i> {}</strong>', 
                obj.user.username
            )
        return format_html(
            '<span style="color: var(--body-quiet-fg, #888); font-style: italic; background: rgba(128,128,128,0.1); '
            'padding: 3px 8px; border-radius: 6px;">Anonymous Staff</span>'
        )

    # Custom Column: Adapts smoothly to dark or light themes using theme variables
    @admin.display(description='Comments')
    def short_description(self, obj):
        if obj.description and len(obj.description) > 75:
            return format_html('<span style="color: var(--body-fg, inherit);">{}...</span>', obj.description[:75])
        return format_html('<span style="color: var(--body-fg, inherit);">{}</span>', obj.description)

    # Custom Column: Highly visible submission timestamp elements
    @admin.display(ordering='created_at', description='Submitted On')
    def formatted_date(self, obj):
        return format_html(
            '<span style="color: var(--body-fg, inherit); font-weight: 500;">{}</span>', 
            obj.created_at.strftime("%d %b %Y, %I:%M %p")
        )