from django.contrib import admin
from .models import Profile, Subscribe, SendedGroups

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "external_id")
    list_display_links = ("id", "external_id")

@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ("id", "profile",'group_subscribe')
    list_display_links = ("id", "profile",'group_subscribe')

@admin.register(SendedGroups)
class SendedGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "date",'group')
    list_display_links = ("id", "date",'group')