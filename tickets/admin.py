from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Ticket, Announcement, Profile

# --- 1. USER & PROFILE INTEGRATION ---

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Department Information'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    
    # We display the department in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_department')

    def get_department(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.department
        return "No Profile"
    
    get_department.short_description = 'Department'

# Unregister the default and register our version
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