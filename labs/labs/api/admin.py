from django.contrib import admin
from .models import Track, Playlist

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'duration')
    search_fields = ('title', 'artist')
    list_filter = ('artist',)

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'public')
    search_fields = ('title', 'owner__username')
    list_filter = ('public',)
    filter_horizontal = ('tracks',)