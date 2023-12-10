# views.py
from django.core.serializers import serialize
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from rest_framework import status
from django.db.models import Q
from .models import Playlist, Track
from .forms import PlaylistForm, TrackForm
from rest_framework.response import Response
import json

from .serializers import PlaylistSerializer


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def playlist_list(request):
    if request.user.is_authenticated:
        # Отримано користувача, ви можете використовувати його
        playlists = Playlist.objects.filter(owner=request.user)
        return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                            'public': playlist.public, 'id': playlist.id} for playlist in playlists],
                             'user': request.user.username})
    else:
        # Користувач не аутентифікований, можливо, повернути помилку або перенаправити на сторінку входу
        return JsonResponse({'error': 'Authentication required'}, status=401)


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.owner != request.user and playlist.public:
        return Response("Bad Response", status= status.HTTP_403_FORBIDDEN)
    return JsonResponse({'title': playlist.title, 'owner': playlist.owner.username,
                         'public': playlist.public, 'id': playlist.id})


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_playlist(request):
    serializer = PlaylistSerializer(data=request.data)
    if serializer.is_valid() and request.user.is_authenticated:
        serializer.save(owner=request.user)
        return Response("OK")
    return Response("Nah-ah")

@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_public_playlists(request):
    playlists = Playlist.objects.filter(public=True)
    return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                        'public': playlist.public, 'id': playlist.id} for playlist in playlists]})


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_available_playlists(request):
    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(Q(public=True) | Q(owner=request.user))
        return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                        'public': playlist.public, 'id': playlist.id} for playlist in playlists]})
    else:
        # Користувач не аутентифікований, можливо, повернути помилку або перенаправити на сторінку входу
        return JsonResponse({'error': 'Authentication required'}, status=401)
