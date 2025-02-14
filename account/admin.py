from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'subject', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'subject')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('محتوا', {
            'fields': ('subject', 'message', 'response')
        }),
        ('وضعیت', {
            'fields': ('status', 'created_at')
        }),
    )