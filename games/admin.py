from django.contrib import admin

# Register your models here.
from .models import Games, Weekly, Genre, GenreSynonym, SteamScore, SteamReview

class GamesAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'date']
    search_fields = ['title']

class GenreSynonymInline(admin.TabularInline):
    model = GenreSynonym
    extra = 3

class GenreAdmin(admin.ModelAdmin):
    search_fields = ["genre"]
    inlines = [GenreSynonymInline]

class GenreSynonymAdmin(admin.ModelAdmin):
    fields = ["owner", "synonym"]
    list_display = ["synonym", "owner"]
    search_fields = ["synonym"]

class SteamScoreAdmin(admin.ModelAdmin):
    list_display = ['owner', 'score', 'reviews']
    search_fields = ['owner']

class SteamReviewAdmin(admin.ModelAdmin):
    list_display = ['owner', 'good', 'author', 'approved']
    search_fields = ['owner']

admin.site.register(Games, GamesAdmin)
admin.site.register(Weekly)
admin.site.register(Genre, GenreAdmin)
admin.site.register(GenreSynonym, GenreSynonymAdmin)
admin.site.register(SteamScore, SteamScoreAdmin)
admin.site.register(SteamReview, SteamReviewAdmin)