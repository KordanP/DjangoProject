from django.urls import path
from . import hello
from .views import playlist_list, playlist_detail, create_playlist, get_public_playlists,get_available_playlists

urlpatterns = [
    path('api/v1/hello-world-2', hello.hello),
    path('playlists', playlist_list, name='playlist_list'),
    path('playlists/<int:playlist_id>', playlist_detail, name='playlist_detail'),
    path('playlists/create', create_playlist, name='create_playlist'),
    path('playlists/public', get_public_playlists, ),
    path('playlists/available', get_available_playlists, ),
]