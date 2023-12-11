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

from .serializers import PlaylistSerializer, TrackSerializer


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
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.owner != request.user and playlist.public:
        return Response("Bad Response", status=status.HTTP_403_FORBIDDEN)
    return JsonResponse({'title': playlist.title, 'owner': playlist.owner.username,
                         'public': playlist.public, 'id': playlist.id})


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_playlist(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = PlaylistSerializer(data=request.data)
    if serializer.is_valid() and request.user.is_authenticated:
        serializer.save(owner=request.user)
        return Response("OK")
    return Response("Nah-ah")


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_public_playlists(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    playlists = Playlist.objects.filter(public=True)
    return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                        'public': playlist.public, 'id': playlist.id} for playlist in playlists]})


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_available_playlists(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(Q(public=True) | Q(owner=request.user))
        return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                        'public': playlist.public, 'id': playlist.id} for playlist in playlists]})
    else:
        # Користувач не аутентифікований, можливо, повернути помилку або перенаправити на сторінку входу
        return JsonResponse({'error': 'Authentication required'}, status=401)


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def playlist_add_track(request, playlist_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = TrackSerializer(data=request.data)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if serializer.is_valid() and (request.user == playlist.owner or playlist.public):
        serializer.save(playlist=playlist)
        return Response("OK", status=status.HTTP_200_OK)
    if request.user != playlist.owner and not playlist.public:
        return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)
    return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def playlist_tracks(request, playlist_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    playlist = get_object_or_404(Playlist, id=playlist_id)

    if request.user == playlist.owner or playlist.public:
        tracks = Track.objects.filter(playlist=playlist)
        return JsonResponse({'tracks': [{'title': track.title, 'artist': track.artist,
                                        'duration': track.duration, 'id':track.id} for track in tracks],
                             'id':playlist.id, 'owner': playlist.owner.username})

    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)

@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_track_from_playlist(request,playlist_id,track_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.owner == request.user or playlist.public:
        track = get_object_or_404(Track,id=track_id)
        track.delete()
        return Response("OK", status=status.HTTP_200_OK)
    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)

@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_playlist(request,playlist_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.owner == request.user or playlist.public:
        playlist.delete()
        return Response("OK", status=status.HTTP_200_OK)
    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)

@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_playlist(request):
    if not request.user.is_authenticated:
        return Response("User not authenticated", status=status.HTTP_400_BAD_REQUEST)

    playlist = get_object_or_404(Playlist, id=request.data.get('id'))

    if request.user == playlist.owner or playlist.public:
        serializer = PlaylistSerializer(playlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response("OK", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_track(request):
    if not request.user.is_authenticated:
        return Response("User not authenticated", status=status.HTTP_400_BAD_REQUEST)

    track = get_object_or_404(Track, id=request.data.get('id'))

    if request.user == track.playlist.owner or track.playlist.public:
        serializer = TrackSerializer(track, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response("OK", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)


@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def change_track_playlist(request):
    if not request.user.is_authenticated:
        return Response("User not authenticated", status=status.HTTP_400_BAD_REQUEST)
    track = get_object_or_404(Track, id=request.data.get('id'))
    playlist_new = get_object_or_404(Playlist, id=request.data.get('new_id'))
    if (playlist_new.owner == request.user or playlist_new.public) and (track.playlist.owner == request.user or track.playlist.public):
        track.playlist = playlist_new
        track.save()
        return Response("Success", status=status.HTTP_200_OK)
    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)
