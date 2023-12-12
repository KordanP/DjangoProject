from django.db import models
from django.contrib.auth.models import User



class Track(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    duration = models.PositiveIntegerField()

class Playlist(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    tracks = models.ManyToManyField(Track)



