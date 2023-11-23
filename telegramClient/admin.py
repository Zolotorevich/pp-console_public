from django.contrib import admin

# Register your models here.
from .models import TelegramChannels

class TelegramChannelsAdmin(admin.ModelAdmin):
    list_display = ['name', 'link', 'defaultTime']
    
admin.site.register(TelegramChannels, TelegramChannelsAdmin)