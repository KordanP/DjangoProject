from django.urls import path
from . import hello
from .views import playlist_list, playlist_detail, create_playlist, get_public_playlists, get_available_playlists, \
    playlist_tracks, delete_track_from_playlist, delete_playlist, update_playlist, update_track, \
    change_track_playlist, create_track, add_track_to_playlist, get_all_tracks

urlpatterns = [
    path('api/v1/hello-world-2', hello.hello),
    path('playlists', playlist_list, name='playlist_list'),
    path('playlists/<int:playlist_id>', playlist_detail, name='playlist_detail'),
    path('playlists/tracks/<int:playlist_id>', playlist_tracks, name='playlist_tracks'),
    path('playlists/create', create_playlist, name='create_playlist'),
    path('playlists/public', get_public_playlists, name='public_playlists'),
    path('playlists/available', get_available_playlists,name='available_playlists'),
    path('track/add', create_track,name='create_track'),
    path('track/all', get_all_tracks,name='get_all_tracks'),
    path('playlists/addTrack/<int:track_id>/<int:playlist_id>', add_track_to_playlist,name='add_track_to_playlist'),
    path('playlists/deleteTrack/<int:playlist_id>/<int:track_id>', delete_track_from_playlist,name='delete_track_from_playlist'),
    path('playlists/delete/<int:playlist_id>', delete_playlist,name='delete_playlist'),
    path('playlists/update/<int:playlist_id>', update_playlist,name='update_playlist'),
    path('playlists/tracks/update', update_track,name='update_track'),
    path('playlists/tracks/change', change_track_playlist,name='change_track_playlist'),
]
