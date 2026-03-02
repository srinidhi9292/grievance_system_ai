from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Complaint, DuplicateMapping, ComplaintTimeline, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'address')}),
    )
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority_level', 'priority_score', 'status', 'is_duplicate', 'created_at']
    list_filter = ['category', 'priority_level', 'status', 'is_duplicate']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['category', 'priority_score', 'priority_level', 'sentiment_score', 'sentiment_label', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(DuplicateMapping)
class DuplicateMappingAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'master_complaint', 'similarity_score', 'detected_at']
    list_filter = ['detected_at']


@admin.register(ComplaintTimeline)
class ComplaintTimelineAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'status', 'updated_by', 'timestamp']
    list_filter = ['status']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read']
