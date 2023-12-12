from rest_framework import serializers
from .models import Track,Playlist

class TrackSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Track
        fields = ['title', 'artist', 'duration']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Playlist
        fields = ['id','title', 'public']
