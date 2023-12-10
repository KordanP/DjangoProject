# forms.py
from django import forms
from .models import Playlist, Track

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'public']

class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'artist', 'duration']
