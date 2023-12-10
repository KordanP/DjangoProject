from rest_framework import serializers
from .models import Track,Playlist

class TrackSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Track
        fields = ['id', 'username', 'password', 'email']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Playlist
        fields = ['title', 'public']
